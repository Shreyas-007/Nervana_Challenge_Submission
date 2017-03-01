from glob import glob
import os

#print(os.path.dirname(os.path.realpath(__file__)))

#TODO: should be in current dir or not
#chdir("cloud_code_challenge")

for file in glob("*.txt"):
    path = os.getcwd() + "/" + file
    fp = open(path, 'r+')
    print(file,fp)