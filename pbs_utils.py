#!/usr/bin/python
# -*- coding: utf-8 -*-
# --------------------------------------------------
# File Name: run_pbs.py
# Purpose: wrapper for running shell commands in pbs queue (works with openpbs/torque)
# Creation Date: 2016
# Author(s): Oliver Pelz
# tested on Linux only
# --------------------------------------------------

import os, stat
import tempfile
import subprocess

# ---------------------------------------------------------------------------

# this class is for running shell commands in a clustered environment 
# using the open source openpbs / torque system
# Please note: this class needs access to a shared nfs mount (accessible on all your pbs nodes)
# because we need to create some temp files which need to be accessible from everywhere
# check if you have write access to nfs_share_dir too!
# deleteFiles parameter deletes all generated files when the program exits
class PBSUtils(object):
   def __init__(self, nfs_share_dir, verbose = False):
      if(not os.path.ismount(self.find_mountpoint(nfs_share_dir))):
         # TODO: throw exception, this method only works if nfs share mount is provided
         # accessible for all nodes
         print nfs_share_dir + " is not a nfs mount"
         return False
      
      self._nfs_share_dir = nfs_share_dir
      self._pbs_cmd = ["qsub", "-I", "-x", "-v", "CMD=%s,STDO_PBS=%s,STDE_PBS=%s", "-N", "%s","%s"]
      self._pbs_script_file = self.create_pbs_run_script()
      self.devnull = open(os.devnull, 'w')
      self._pbs_run_script = self.create_pbs_run_script()
      self._verbose = verbose
   # creates helper bash script for running pbs scripts dynamically   
   # please note if running pbs -I -x this script must be accessible on every node as well!
   def create_pbs_run_script(self):
      script =  """#PBS -S /bin/bash
#PBS -V
## PBS -l nodes=1:ppn=1
# #PBS -l mem=
echo "running commandline: $CMD"
$CMD 1> $STDO_PBS 2>$STDE_PBS\
"""
      f = tempfile.NamedTemporaryFile(dir=self._nfs_share_dir, delete=False)
      f.write(script)
      f.close()
# also make executable for user(needed for openpbs to run it)
      os.chmod(f.name, 0755)
      return f.name
# this comes from stackoverflow: http://stackoverflow.com/questions/4453602/how-to-find-the-mountpoint-a-file-resides-on
# get the mountpoint for a file e.g. : /data/x/y/z/bla.txt -> /data
   def find_mountpoint(self, path):
    for l in open("/proc/mounts", "r"):
        mp = l.split(" ")[1]
        if(mp != "/" and path.find(mp)==0): return mp
    return None
 
   def get_pbs_run_script(self):
       return self._pbs_run_script

   def generate_cmd(self, pbs_run_name, cmd, stdoutFilename, stderrFilename):
       self._pbs_cmd[4] = self._pbs_cmd[4] % (cmd, stdoutFilename, stderrFilename)
       self._pbs_cmd[6] = self._pbs_cmd[6] % (pbs_run_name)
       self._pbs_cmd[7] = self._pbs_cmd[7] % (self._pbs_run_script)
       return self._pbs_cmd
   
   # pbs_run_name is the name of the pbs job (in script defined by #PBS -N )
   # cmd - the command you want to execute in pbs
   # returns the commands stdout and stderr as files
   def run_command_qsub_files(self, pbs_run_name, cmd):
      # generate temp files which hold the cmd's output
      cmdStdoutFile = tempfile.NamedTemporaryFile(dir=self._nfs_share_dir, delete=False)
      cmdStderrFile = tempfile.NamedTemporaryFile(dir=self._nfs_share_dir, delete=False)
      arr = self.generate_cmd(pbs_run_name, cmd, cmdStdoutFile.name, cmdStderrFile.name) 
      if(not self._verbose):
        errorcode = subprocess.call(arr, stdout=self.devnull, stderr=self.devnull)
      else:
        print " ".join(arr)
        errorcode = subprocess.call(arr)
      if(errorcode == 1):
        return False
      return cmdStdoutFile.name, cmdStderrFile.name
 
   def run_command_qsub_output(self, pbs_run_name, cmd, delete_file = True):
     stdoutFilename, stderrFilename = self.run_command_qsub_files(pbs_run_name, cmd)
     try:
       with open(stdoutFilename) as f: stdoutFileContent = f.read()
       with open(stderrFilename) as f: stderrFileContent = f.read()
     except IOError as e:
       print "I/O error({0}): {1}".format(e.errno, e.strerror)
       return False
     return stdoutFileContent, stderrFileContent
     




