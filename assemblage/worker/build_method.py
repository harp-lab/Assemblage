"""
Decide build method based on files in repo directory

Assemblage Windows Worker Build Methods
1. Modify XML file
2. Build with msbuild
Chang
Yihao
"""

import os
import glob
import re
import logging
import subprocess
import signal
import json
import ftplib

import boto3
from botocore.exceptions import ClientError

from assemblage.consts import BuildStatus, PDBJSONNAME, BINPATH
from assemblage.windows.parsers.proj import Project
from assemblage.analyze.analyze import get_build_system

logging.basicConfig(level=logging.INFO)


def cmd_with_output(cmd, timelimit=60, platform='linux'):
    """ The cmd execution function """
    if isinstance(cmd, list):
        cmd = " ".join(cmd)
    with subprocess.Popen(cmd,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          close_fds=True,
                          shell=True) as process:
        try:
            out, err = process.communicate(timeout=timelimit)
            exit_code = process.wait()
            process.kill()
            return out, err, exit_code
        except subprocess.TimeoutExpired:
            if platform == 'linux':
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            return b"subprocess.TimeoutExpired", b"subprocess.TimeoutExpired", 1


def dia_get_func_funcinfo(binfile):
    """ Process the bin to get the info and function"""
    binfile = binfile.replace("\\", "/")
    cmd_args = [
        "powershell", "-Command", "Dia2Dump", "-lines", "*", f"'{binfile}'"
    ]
    file_cache = {}
    out, _err, _exit_code = cmd_with_output(cmd_args, platform='windows')
    try:
        lines_notclean = out.decode().split("\r\n")
    except:
        logging.info("Dia2dump error")
        lines_notclean = []
    lines = []
    for line in lines_notclean:
        lines.append(line.strip())
    funcs_infos = {}
    rva_seg_length = 0
    dbg_seg_length = 0
    source_file = ""
    lines_infos = {}
    for i, line in enumerate(lines):
        lines_dict = {}
        if line.startswith("**"):
            func_name = line.replace("**", "").replace(" ", "").strip()
            rva_seg_length = 0
            dbg_seg_length = 0
            func_name_infoitem = {}
        if line.startswith("line"):
            if len(re.split(r"\w:\\", line)) == 2:
                source_file = re.findall(r"\w:\\", line)[0] + re.split(
                    r"\w:\\", line)[1]
            rva = re.findall(r"at \[\w+\]",
                             line)[0].replace("at ",
                                              "").replace("[",
                                                          "").replace("]", "")
            length = int(
                re.findall(r"len \= \w+", line)[0].replace("len = ", ""), 16)
            line_number = int(
                re.findall(r"line \d+", line)[0].replace("line ", ""), 16)
            lines_dict["line_number"] = line_number
            lines_dict["rva"] = rva
            lines_dict["length"] = length
            lines_dict["source_code"] = ""
            try:
                source_file_cleaned = source_file.split(" (")[0]
            except Exception:
                source_file_cleaned = source_file
            if source_file_cleaned not in file_cache.keys():
                try:
                    with open(source_file_cleaned, 'r') as source_f:
                        file_cache[source_file_cleaned] = source_f.readlines()
                except Exception as excep:
                    file_cache[source_file_cleaned] = []
            try:
                lines_dict["source_code"] = file_cache[source_file_cleaned][line_number].strip()
            except Exception as err:
                lines_dict["source_code"] = ""
            lines_dict["source_file"] = source_file_cleaned
            if "rva_start" not in func_name_infoitem.keys():
                func_name_infoitem["rva_start"] = rva
            if line_number > 10000000:
                dbg_seg_length = dbg_seg_length + length
            rva_seg_length = rva_seg_length + length
            if not lines[i + 1].startswith("line"):
                func_name_infoitem["rva_end"] = str(
                    hex(int(rva, 16) + int(length))).replace("0x", "").rjust(
                        len(rva), "0")
                if rva_seg_length != 0:
                    func_name_infoitem["debug_ratio"] = str(
                        (dbg_seg_length / rva_seg_length) * 100)[:5] + "%"
                else:
                    func_name_infoitem["debug_ratio"] = "0%"
                if func_name in funcs_infos.keys():
                    funcs_infos[func_name].append(func_name_infoitem)
                else:
                    funcs_infos[func_name] = [func_name_infoitem]
            if func_name in lines_infos.keys():
                lines_infos[func_name].append(lines_dict)
            else:
                lines_infos[func_name] = [lines_dict]
    return funcs_infos, lines_infos, source_file


def dia_list_binaries(dest_binfolder):
    """ get binary file under the binfolder """
    bfiles = []
    if os.path.isdir(dest_binfolder):
        files = os.listdir(dest_binfolder)
        for single_file in files:
            if single_file.endswith("exe") or single_file.endswith("dll"):
                bfiles.append(single_file)
    return bfiles


def post_processing_pdb(dest_binfolder, build_mode, library, repoinfo, toolset,
                        optimization):
    """ Postprocess the pdb """
    bin_files = dia_list_binaries(dest_binfolder)
    outer_list = []
    for _, binfile in enumerate(bin_files):
        binfile = os.path.join(dest_binfolder, binfile)
        logging.info("Checking binary info %s: %s", binfile,
                     os.path.isfile(binfile))
        funcs_infos, lines_infos, source_file = dia_get_func_funcinfo(binfile)
        item_dict = {}
        item_dict["functions"] = []
        item_dict["file"] = binfile
        for func_name, infos in funcs_infos.items():
            functions_val = {}
            functions_val["function_name"] = func_name
            functions_val["source_file"] = source_file
            if len(infos) == 1:
                functions_val["intersect_ratio"] = "0%"
            else:
                rva_segs = []
                for info_dict in infos:
                    rva_segs.append(
                        (info_dict["rva_start"], info_dict["rva_end"]))
                rva_segs.sort()
                rva_len = int(rva_segs[-1][1], 16) - int(rva_segs[0][0], 16)
                rva_gap = 0
                for k in range(0, len(rva_segs) - 1):
                    rva_gap += int(rva_segs[k+1][0], 16) - \
                        int(rva_segs[k][1], 16)
                functions_val["intersect_ratio"] = str(
                    (rva_gap / rva_len) * 100)[:5] + "%"
            functions_val["function_info"] = funcs_infos[func_name]
            functions_val["lines"] = lines_infos[func_name]
            item_dict["functions"].append(functions_val)
        outer_list.append(item_dict)
    try:
        json_di = {}
        json_di["Platform"] = library
        json_di["Build_mode"] = build_mode
        json_di["Toolset_version"] = toolset
        json_di["URL"] = repoinfo["url"]
        json_di["Binary_info_list"] = outer_list
        json_di["Optimization"] = optimization
        json_di["Pushed_at"] = repoinfo["updated_at"]
        with open(os.path.join(dest_binfolder, PDBJSONNAME), "w") as outfile:
            json.dump(json_di, outfile, sort_keys=False, indent=4)
        repoid = dest_binfolder.split("\\")[-1]
        # with open(os.path.join(PDBPATH, f"{repoid}.json"), "w") as outfile:
        #     json.dump(json_di, outfile, sort_keys=False, indent=4)
    except FileNotFoundError:
        logging.info("Pdbjsonfile not found")


def post_processing_compress(dest_binfolder, repo, build_opt, num):
    """ Compress the binary file """
    repo_fname = dest_binfolder.split("\\")[-1]
    zipname = str(repo["repo_id"])+"_"+str(build_opt)+"_"+str(num)
    if os.name=="nt":
        cmd = f"cd {BINPATH}/{repo_fname}&&7z a -r -tzip {zipname}.zip *"
        out, _err, _exit_code = cmd_with_output(cmd, platform='windows')
    else:
        cmd = f"cd {BINPATH}&&zip -r {zipname}.zip {repo_fname}"
        out, _err, _exit_code = cmd_with_output(cmd, platform='linux')
    logging.info("Compress output %s", zipname)
    return f"{zipname}.zip"

def post_processing_ftp(serveraddr, zipfile_path, _repo, zipfile_name):
    ftp_conn = ftplib.FTP()
    ftp_conn.connect(serveraddr, 10086)
    ftp_conn.login("assemblage", "assemblage")
    if zipfile_name not in ftp_conn.nlst():
        with open(zipfile_path, 'rb') as bin_f:
            ftp_conn.storbinary(
                f'STOR {zipfile_name}', fp=bin_f)
    ftp_conn.close()

def post_processing_s3(repo_fname, file_location):
    sesh = boto3.Session(profile_name='default')
    s3 = sesh.client('s3')

    try:
        logging.info("SENDING S3 DATA FOR %s.", repo_fname)
        s3.upload_file(file_location, 'assemblage-data', "data/"+repo_fname,
                       ExtraArgs={'StorageClass': 'STANDARD_IA'})
    except ClientError as e:
        # TODO: What do?
        logging.error(e)
        return None
    return "data/"+repo_fname

def clean(folders, platform):
    """ Delete the dirs to free space """
    if platform == 'windows':
        for folder in folders:
            folder_name_cleaned = os.path.abspath(folder)
            try:
                _out, _err, _exit_code = cmd_with_output(
                    f"DEL /F/Q/S {folder_name_cleaned}", platform='windows')
                _out, _err, _exit_code = cmd_with_output(
                    f"RMDIR /Q/S {folder_name_cleaned}", platform='windows')
                logging.info("Cleaned %s", folder_name_cleaned)
            except subprocess.CalledProcessError as e:
                logging.error("Clean err %s", e.output)
            except UnicodeDecodeError:
                logging.error("Clean UnicodeDecodeError")
    elif platform == 'linux':
        for folder in folders:
            os.system(f"rm -rf {folder}")


def windows_pre_processing(Target_dir,
                           Optimization,
                           _tmp_dir,
                           VC_Version,
                           Favorsizeorspeed="",
                           Inlinefunctionexpansion="",
                           Intrinsicfunctions=""):
    """ Modifying the build file to save flags """
    logging.info("Parsing")
    files = []
    for filename in glob.iglob(Target_dir + '**/**', recursive=True):
        files.append(filename)
    slnfile = ""
    projfiles = []
    for f in files:
        if f.endswith("sln"):
            slnfile = f
        if f.endswith("vcxproj"):
            projfiles.append(f)
    if slnfile == "":
        logging.error("No solution file found")
        return "No SLN file found", BuildStatus.FAILED, ""
    try:

        for projfile in projfiles:
            # if projfile.endswith("csproj"):
            #     return "Language Error, C# is rejected", BuildStatus.FAILED, ""
            # Parser related
            projobj = Project(projfile)
            # projobj.set_toolset_version(VC_Version)
            projobj.set_optimization(Optimization)
            if Favorsizeorspeed != "":
                projobj.set_favorsizeorspeed(Favorsizeorspeed)
            if Inlinefunctionexpansion != "":
                projobj.set_inlinefunctionexpansion(Inlinefunctionexpansion)
            if Intrinsicfunctions != "":
                projobj.enable_intrinsicfunctions()
            projobj.write()

            projobj_saved = Project(projfile)
            optimization_mode = ""
            if "O2" in Optimization:
                optimization_mode = "MaxSpeed"
            elif "O1" in Optimization:
                optimization_mode = "MinSpace"
            elif "Ox" in Optimization:
                optimization_mode = "Full"
            else:
                optimization_mode = "Disabled"
            logging.info("Read config: %s, correct: %s", projobj_saved.get_optimization(), optimization_mode)
            assert optimization_mode == projobj_saved.get_optimization()
            # assert VC_Version == projobj_saved.get_toolset_version()

    except FileNotFoundError:
        logging.error("Build File not exist")
        return "Parsing FileNotFoundError", BuildStatus.FAILED, ""
    except AttributeError as err:
        logging.error("Build vcxproj file parsing error %s", str(err))
        return "Parsing AttributeError", BuildStatus.FAILED, ""
    except KeyError:
        logging.error("Build vcxproj file setting error")
        return "Parsing file key error", BuildStatus.FAILED, ""
    except AssertionError:
        return "Parsing file verification error", BuildStatus.FAILED, ""
    logging.info("Parsing success")
    return "Parsing success", BuildStatus.SUCCESS, slnfile

def get_cmd(target_dir,
            build_tool,
            build_mode,
            library,
            optimization,
            slnfile=None,
            platform='linux',
            compiler_version='v142'):
    """ Generate cmd to execute """
    if platform.lower() == 'windows':
        cmd = ["powershell", "-Command", "msbuild"]
        if build_mode in ["Release", "Debug"]:
            cmd.append(f"/property:Configuration={build_mode}")
        if library == "x86" or library == "Win32":
            cmd.append("/property:Platform=Win32")
        elif library == "x64":
            cmd.append("/property:Platform=x64")
        elif library == "Mixed Platforms":
            cmd.append("/property:Platform='Mixed Platforms'")
        # elif library == "Any CPU":
        #     cmd.append("/property:Platform='Any CPU'")
        cmd.append(f"/p:PlatformToolset={compiler_version}")
        # cmd.append("/p:WindowsTargetPlatformVersion= ")
        cmd.append("/maxcpucount:1")
        cmd.append("/property:PostBuildEvent= ")
        cmd.append("/property:OutDir=assemblage_outdir_bin/")
        cmd.append(f"'{slnfile}'")
        cmd = " ".join(cmd)
        logging.info("Windows cmd generated: %s", cmd)
        return cmd
    cmd = ""
    if platform.lower() == 'linux':
        if build_tool == 'bootstrap':
            cmd = f'cd {target_dir} && ./bootstrap && ' \
                'bash ./configure && timeout -m 5000000 make -j4'
        elif build_tool == 'configure':
            cmd = f'cd {target_dir} && bash ./configure && ' \
                'timeout -m 5000000 -- make -j4'
        elif build_tool == 'cmake':
            cmd = f'cd {target_dir} && cmake -Bbuild ./ && cd build && ' \
                'timeout -m 5000000 -- make -j4'
        elif build_tool == 'make':
            cmd = f'cd {target_dir} && timeout -m 5000000 -- make -j4'
    return cmd


def build(target_dir,
          build_tool,
          platform,
          build_mode="Release",
          library="x64",
          optimization="Od",
          tmp_dir="Builds",
          compiler_version="v142",
          favorsizeorspeed="",
          inlinefunctionexpansion="Obd",
          intrinsicfunctions=False):
    """ The actual build process """
    build_file = ""
    if platform.lower() == "windows":
        msg, status, build_file = windows_pre_processing(
            target_dir, optimization, tmp_dir, compiler_version,
            favorsizeorspeed, inlinefunctionexpansion, intrinsicfunctions)
        if status != BuildStatus.SUCCESS:
            return msg, status, build_file
    if platform.lower() == "linux":
        files = []
        for filename in glob.iglob(target_dir + '**/**', recursive=True):
            files.append(filename.split("/")[-1])
        logging.info("%s files in repo", len(files))
        build_tool = get_build_system(files)
    cmd = get_cmd(target_dir,
                  build_tool,
                  build_mode,
                  library,
                  optimization,
                  slnfile=build_file,
                  platform=platform,
                  compiler_version=compiler_version)
    out, err, exit_code = cmd_with_output(cmd, 60, platform)
    logging.info("Build complete with %s, finishing up", exit_code)
    try:
        output_dec = out.decode('utf-8')
        output_dec += err.decode('utf-8')
    except UnicodeDecodeError:
        logging.info("Build exited: %s", exit_code)
        return "UnicodeDecodeError", BuildStatus.FAILED, build_file
    if exit_code == 0:
        return 'success', BuildStatus.SUCCESS, build_file
    return output_dec, BuildStatus.FAILED, build_file
