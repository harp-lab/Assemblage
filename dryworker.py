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

from assemblage.consts import BINPATH, PDBPATH, TASK_TIMEOUT_THRESHOLD, BuildStatus, MAX_MQ_SIZE
# from assemblage.worker.base_worker import BasicWorker
from assemblage.worker import build_method
from assemblage.worker.find_bin import find_elf_bin
from assemblage.worker.profile import AWSProfile
# from assemblage.protobufs.assemblage_pb2 import getBuildOptRequest
from assemblage.worker.build_method import DefaultBuildStrategy

from vcpkg_functions import *



mode = "release"
compiler_version = 'v142'
library = "x86/x64"

def taskwrap(url, opt):
    msg, code, clonedir = clone_data(url, opt, mode)
    try:
        run_build(url, clonedir, mode, library, opt,
					"", "", compiler_version)
    except:
        pass


import json
projects = []
with open("projects.json", "r") as f:
    projects = json.load(f)
import random
random.shuffle(projects)
for project in projects:
    for optimization_level in ["Od", "O1", "O2", "Ox"]:
        taskwrap(project, optimization_level)