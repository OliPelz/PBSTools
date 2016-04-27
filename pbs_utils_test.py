import os
import re
import subprocess
from pbs_utils import PBSUtils


def grepFile(filename, patt):
   for line in open(filename, 'r'):
     print patt
     print re.escape(patt)
     if re.search(re.escape(patt), line):
        return True
   return False

def test_constructor():
   nfs_dir = "/data/minUP-test/minoTour-data"
   pbs_utils = PBSUtils(nfs_dir)      
   assert pbs_utils._nfs_share_dir == nfs_dir

def test_create_pbs_run_script():
   nfs_dir = "/data/minUP-test/minoTour-data"
   pbs_utils = PBSUtils(nfs_dir)
   filename = pbs_utils.create_pbs_run_script()
   assert os.path.isfile(filename)
   assert grepFile(filename, "#PBS")  
   assert grepFile(filename, "STDO_PBS")
   assert not grepFile(filename, "Micky Mouse") 

def test_generate_cmd():
   run_name = "ABC"
   cmd = "grep xyz /tmp/bla"
   stdoutFilename  = "/tmp/myStdoutfile"
   stderrFilename = "/tmp/myStderrfile"
   
   nfs_dir = "/data/minUP-test/minoTour-data"
   pbs_utils = PBSUtils(nfs_dir)

   arr = pbs_utils.generate_cmd(run_name, cmd, stdoutFilename, stderrFilename)
   txt = " ".join(arr)
   toCompare = "qsub -I -x -v CMD=grep xyz /tmp/bla,STDO_PBS=/tmp/myStdoutfile,STDE_PBS=/tmp/myStderrfile -N ABC " + pbs_utils.get_pbs_run_script()
   print txt
   print toCompare
   assert txt == toCompare

def test_run_cmd_qsub_files():
   nfs_dir = "/data/minUP-test/minoTour-data"
   pbs_utils = PBSUtils(nfs_dir, verbose = False)
   # run locally
   dateToTest = subprocess.check_output(["date", "+'%y%m%d'"])
   
   # run the same command on the queue
   result = pbs_utils.run_command_qsub_files('this-is-a-testrun', "date +'%y%m%d'")
   assert result is not False
   stdoutFile, stderrFile = result
   with open(stdoutFile) as f: fileContent = f.read()
#   print fileContent
#   print dateToTest
   assert fileContent == dateToTest

def test_run_command_qsub_output():
   nfs_dir = "/data/minUP-test/minoTour-data"
   pbs_utils = PBSUtils(nfs_dir, verbose = False)
   # run locally
   dateToTest = subprocess.check_output(["date", "+'%y%m%d'"])
   result = pbs_utils.run_command_qsub_output('this-is-a-testrun', "date +'%y%m%d'")
   assert result is not False
   stdoutFileContent, stderrFileContent = result
   assert stdoutFileContent  == dateToTest 

def test_run_command_qsub_output_deletes_files():
   assert False   

