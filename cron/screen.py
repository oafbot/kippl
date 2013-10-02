import subprocess, os, shlex
from subprocess import Popen, PIPE

def screen_is_running():
    out = Popen("screen -list",shell=True,stdout=PIPE).communicate()[0]
    return not out.startswith("No Sockets found")

if not screen_is_running():
	os.chdir("/Users/laika/Documents/Code/python/kippl") 
	command = "screen -S kippl ./collect.py japan"
	subprocess.call(shlex.split(command))
else:
	print Popen("screen -list",shell=True,stdout=PIPE).communicate()[0]