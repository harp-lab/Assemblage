'''
A ddisasm worker can run ddisasm on binary
'''

import datetime
import json
import logging
import os
import tempfile
import threading
import time
import zipfile
import boto3

from assemblage.worker.base_worker import BasicWorker
from assemblage.worker.build_method import cmd_with_output
from assemblage.worker.ftp import AssemblageFtpSever
from botocore.exceptions import ClientError

class DDisasmWorker(BasicWorker):
    """
    a ddisasm worker
    """

    def __init__(self, rabbitmq_host, rabbitmq_port, rpc_stub, worker_type, opt_id, send_binary_method):
        super().__init__(rabbitmq_host, rabbitmq_port, rpc_stub, worker_type, opt_id)
        # run a ftp server on 10086
        time.sleep(5)
        if not os.path.exists("/binaries/ftp"):
            os.makedirs("/binaries/ftp")
        # ftp_server = AssemblageFtpSever("/binaries/ftp")
        # ftp_thread = threading.Thread(target=ftp_server.start, daemon=True)
        # ftp_thread.start()
        self.sesh = boto3.session.Session(profile_name='assemblage')
        self.s3 = self.sesh.client('s3')

    def on_init(self):
        logging.info("ddisasm worker starting ....")

    def setup_job_queue_info(self):
        # self.topic_exchange = 'post_analysis'
        self.input_queue_name = 'post_analysis.ddisasm'
        self.input_queue_args = {
            "durable": True
        }

    def job_handler(self, ch, method, _props, body):
        repo = json.loads(body)
        ch.basic_ack(method.delivery_tag)
        logging.info(repo)
        try:
            with open(repo['file_name'].replace("data/", ""), 'wb') as f:
                self.s3.download_fileobj('assemblage-data', repo['file_name'], f)
            logging.info("S3 bucket downloaded")
        except Exception as err:
            logging.error(err)
        tmp_bin_dir = repo['file_name'].replace("data/", "")+"_folder"
        try:
            os.mkdir(tmp_bin_dir)
        except:
            os.remove(tmp_bin_dir)
            os.mkdir(tmp_bin_dir)
        zipfile = repo['file_name'].replace("data/", "")
        cmd_with_output(f"unzip {zipfile} -d {tmp_bin_dir}")
        for f in os.listdir(tmp_bin_dir):
            if f.endswith(".exe") or f.endswith(".dll"):
                cmd = f"objdump -D {os.path.join(tmp_bin_dir, f)} > {os.path.join(tmp_bin_dir, f)}.asm"
                # logging.info(cmd)
                out, err, exit_code = cmd_with_output(cmd)
                # logging.info(out)
                try:
                    with open(os.path.join(tmp_bin_dir, f+".asm"), "rb") as fh:
                        self.s3.upload_fileobj(fh, 'assemblage-data', "postprocessed/"+f+".asm")
                    logging.info(f'Uploaded %s', os.path.join(tmp_bin_dir, f+".asm"))
                except Exception as e:
                    logging.error(e)
        cmd_with_output(f"rm -rf {tmp_bin_dir}")
        cmd_with_output(f"rm -rf {zipfile}")
        
