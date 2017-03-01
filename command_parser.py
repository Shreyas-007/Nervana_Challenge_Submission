import os
from subprocess import *
import threading
from time import time
from base import Command
from db import session


class RunCommand(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None

    def run(self, timeout):
        start = time()

        def target():
            print '\n' + 'Thread started'

            file = "/outputs.txt"
            path = os.getcwd() + file
            file_object = open(path, 'w')

            self.process = Popen(self.cmd, stdout=file_object, shell=True)
            self.process.communicate()

            print '\n' + 'Thread finished'

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            print 'Terminating process'
            self.process.terminate()
            thread.join()

        return time() - start


"""
Handles the work of validating and processing command input.
"""


def get_valid_commands(queue, fi):
    # TODO: efficiently evaluate commands
    file = "/commands.txt"
    path = os.getcwd() + file
    fp = open(path, 'r+')

    command_lines = list()
    valid_command_lines = list()

    flag_cmd = False
    flag_valid = False

    # Parse the lines in the file and store COMMANDS and VALID-COMMANDS in separate lists
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

    fp.close()
    command_lines = [x.replace("\n", "") for x in command_lines]
    command_lines = [x.replace("\r", "") for x in command_lines]
    valid_command_lines = [x.replace("\n", "") for x in valid_command_lines]
    valid_command_lines = [x.replace("\r", "") for x in valid_command_lines]

    for i in valid_command_lines:
        queue.put(i)


def process_command_output(queue):
    # TODO: run the command and put its data in the db

    while not queue.empty():

        try:
            file = "/outputs.txt"
            path = os.getcwd() + file
            fp = open(path, 'r+')
            cmd = queue.get()
            command = RunCommand(cmd)

            # Lists to store the data read from output file, eventually we read from these files and put the output in DB
            subCmdOutput = list()
            cmdOutput = list()

            for line in fp:
                subCmdOutput.append(line)

            fp.close()
            cmdOutput.append(subCmdOutput)

            # Set timeout to 1 minute and terminate the child process
            time_taken = command.run(timeout=60)

            string = ""
            for i in cmdOutput:
                string = string.join(i)

            cmd_output = Command(cmd, len(cmd), round(time_taken, 4), string)
            session.add(cmd_output)


        except Exception as ie:
            print ie.message

    # Commit session if everything goes well, else rollback
    try:
        session.commit()
    except Exception as ie:
        session.rollback()