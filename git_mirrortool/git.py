import subprocess

def git(cmd):
    return subprocess.check_output(['git'] + cmd)
