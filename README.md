repository which contains PBS related Python code

# class PBSUtils
handles communication (job submission and result returning) of torque's qsub command
It blocks and waits for finishing of qsub results.

Please note: this class uses qsub's -I -x  interactive mode to connect to qsub and wait for the result.
Using such a system is fine for single instances and the code works as it is but you should note that spawing multiple instances of this class
will reduce server execution performance drastically. 
This is because each run will open and hold a new qsub connection...which brings a lot of overhead
If you need to submit multiple jobs to qsub (and wait / block for the result) its better to use DRMAA python.

note2: you need a shared directory / nfs share which must be available on all compute nodes for proper job communication.
Example:

```
nfs_dir = "/data/minUP-test/minoTour-data"
pbs_utils = PBSUtils(nfs_dir, verbose = False)
# run locally
dateToTest = subprocess.check_output(["date", "+'%y%m%d'"])
# this will block execution until finished
result = pbs_utils.run_command_qsub_output('this-is-a-testrun', "date +'%y%m%d'")
stdoutFileContent, stderrFileContent = result
print stdoutFileContent
```
