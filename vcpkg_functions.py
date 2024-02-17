import datetime
import logging
import os
import shutil
import json
import time
import random
import string

import glob
# import grpc
import requests
import ntpath


def clone_data(repo, optimization_level, mode):
	""" vcpkg don't need clone, pass the final result dir as clone dir """
	# vcpkg packge name is also stored in 'url' because of scraper code
	dest_path = f"Builds/{repo}_{optimization_level}_{mode}"
	if os.path.exists(dest_path):
		shutil.rmtree(dest_path, ignore_errors=False, onerror=None)
	os.makedirs(os.path.join(dest_path, "triplets"))
	logging.info("Clone called")
	return b'No need for clone', 1, dest_path

def post_build_hook(dest_binfolder, build_mode, library, repoinfo, toolset,
					optimization):
	""" Postprocess the pdb """

	return


def run_build(repo, target_dir, build_mode, library, optimization,
					slnfile, platform, compiler_version):
	""""""
	logging.info(f" >>> Building {repo} ...")
	triplet_cpu_arch = "x64"
	triplet_path = os.path.relpath(os.path.join(target_dir, "triplets", f"{triplet_cpu_arch}-{optimization.lower()}-windows.cmake"))
	triplet_flags = {"VCPKG_TARGET_ARCHITECTURE": triplet_cpu_arch, "VCPKG_CRT_LINKAGE":"dynamic", "VCPKG_LIBRARY_LINKAGE":"dynamic"}
	if build_mode.lower()=="release":
		triplet_flags["VCPKG_BUILD_TYPE"] = "release"
	else:
		triplet_flags["VCPKG_BUILD_TYPE"] = "debug"
	triplet_flags["CMAKE_CXX_FLAGS"] = f"/{optimization}"
	triplet_flags["CMAKE_C_FLAGS"] = f"/{optimization}"
	triplet_flags["VCPKG_CXX_FLAGS"] = f"/{optimization}"
	triplet_flags["VCPKG_C_FLAGS"] = f"/{optimization}"
	triplet_flags["CMAKE_CXX_FLAGS_RELEASE"] = f"/{optimization}"
	triplet_flags["CMAKE_C_FLAGS_RELEASE"] = f"/{optimization}"
	triplet_flags["VCPKG_CXX_FLAGS_RELEASE"] = f"/{optimization}"
	triplet_flags["VCPKG_C_FLAGS_RELEASE"] = f"/{optimization}"


	with open(triplet_path, "w") as f:
		for x in triplet_flags:
			f.write(f"set({x} {triplet_flags[x]})\n")
	cmd = f"vcpkg install {repo} --overlay-triplets={target_dir}/triplets --x-install-root={target_dir} --triplet {triplet_cpu_arch}-{optimization}-windows"
	logging.info(cmd)
	os.system(cmd)

	os.remove(triplet_path)
	triplet_cpu_arch = "x86"
	triplet_path = os.path.relpath(os.path.join(target_dir, "triplets", f"{triplet_cpu_arch}-{optimization.lower()}-windows.cmake"))
	triplet_flags = {"VCPKG_TARGET_ARCHITECTURE": triplet_cpu_arch, "VCPKG_CRT_LINKAGE":"dynamic", "VCPKG_LIBRARY_LINKAGE":"dynamic"}
	if build_mode.lower()=="release":
		triplet_flags["VCPKG_BUILD_TYPE"] = "release"
	else:
		triplet_flags["VCPKG_BUILD_TYPE"] = "debug"
	triplet_flags["CMAKE_CXX_FLAGS"] = f"/{optimization}"
	triplet_flags["CMAKE_C_FLAGS"] = f"/{optimization}"
	triplet_flags["VCPKG_CXX_FLAGS"] = f"/{optimization}"
	triplet_flags["VCPKG_C_FLAGS"] = f"/{optimization}"
	triplet_flags["CMAKE_CXX_FLAGS_RELEASE"] = f"/{optimization}"
	triplet_flags["CMAKE_C_FLAGS_RELEASE"] = f"/{optimization}"
	triplet_flags["VCPKG_CXX_FLAGS_RELEASE"] = f"/{optimization}"
	triplet_flags["VCPKG_C_FLAGS_RELEASE"] = f"/{optimization}"


	with open(triplet_path, "w") as f:
		for x in triplet_flags:
			f.write(f"set({x} {triplet_flags[x]})\n")
	cmd = f"vcpkg install {repo} --overlay-triplets={target_dir}/triplets --allow-unsupported --triplet {triplet_cpu_arch}-{optimization}-windows"
	logging.info(cmd)
	os.system(cmd)

	return

def run_arm_build(repo, target_dir, build_mode, library, optimization,
					slnfile, platform, compiler_version):
	""""""
	logging.info(f" >>> Building {repo} ...")
	triplet_cpu_arch = "arm64"
	if os.path.isdir(target_dir):
		return
	triplet_path = os.path.relpath(os.path.join(target_dir, "triplets", f"{triplet_cpu_arch}-{optimization.lower()}-windows.cmake"))
	triplet_flags = {"VCPKG_TARGET_ARCHITECTURE": triplet_cpu_arch, "VCPKG_CRT_LINKAGE":"dynamic", "VCPKG_LIBRARY_LINKAGE":"dynamic"}
	triplet_flags["VCPKG_BUILD_TYPE"] = "release"
	triplet_flags["CMAKE_CXX_FLAGS"] = f"/{optimization}"
	triplet_flags["CMAKE_C_FLAGS"] = f"/{optimization}"
	triplet_flags["VCPKG_CXX_FLAGS"] = f"/{optimization}"
	triplet_flags["VCPKG_C_FLAGS"] = f"/{optimization}"
	triplet_flags["CMAKE_CXX_FLAGS_RELEASE"] = f"/{optimization}"
	triplet_flags["CMAKE_C_FLAGS_RELEASE"] = f"/{optimization}"
	triplet_flags["VCPKG_CXX_FLAGS_RELEASE"] = f"/{optimization}"
	triplet_flags["VCPKG_C_FLAGS_RELEASE"] = f"/{optimization}"

	with open(triplet_path, "w") as f:
		for x in triplet_flags:
			f.write(f"set({x} {triplet_flags[x]})\n")
	cmd = f"vcpkg install {repo} --overlay-triplets={target_dir}/triplets --x-install-root={target_dir} --triplet {triplet_cpu_arch}-{optimization}-windows"
	logging.info(cmd)
	os.system(cmd)

