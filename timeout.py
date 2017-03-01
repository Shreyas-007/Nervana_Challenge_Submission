import os
import subprocess
import threading
from time import time


class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None

    def run(self, timeout):
        start = time()

        def target():
            print 'Thread started'

            self.process = subprocess.Popen(self.cmd, shell=True)
            self.process.communicate()
            print 'Thread finished'

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            print 'Terminating process'
            self.process.terminate()
            thread.join()
        print self.process.returncode
        return time()-start


file = "/commands.txt"
path = os.getcwd() + file
fp = open(path, 'r+')

command_lines = list()
valid_command_lines = list()

flag_cmd = False
flag_valid = False

for line in fp:
    if line.startswith("[COMMAND LIST]"):
        flag_cmd = True
        continue

    elif line.startswith("[VALID COMMANDS]"):
        flag_valid = True

    elif flag_cmd and not flag_valid:
        command_lines.append(line)

    elif flag_cmd and flag_valid:
        valid_command_lines.append(line)

command_lines = [x.replace("\n", "") for x in command_lines]
command_lines = [x.replace("\r", "") for x in command_lines]
valid_command_lines = [x.replace("\n", "") for x in valid_command_lines]
valid_command_lines = [x.replace("\r", "") for x in valid_command_lines]

for i in valid_command_lines:

    try:
        # file_object = open("outputs.txt","w")
        # p = call(i, stdout=file_object,shell=True)

        command = Command(i)
        print("Time taken by " + command + "is : "  + command.run(timeout=10))

    # file_object.close()
    except Exception as e:
        print type(e)  # the exception instance
        print e.args
