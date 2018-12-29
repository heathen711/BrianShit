#!/usr/bin/env python

import shlex
import subprocess

def run_and_check(command):
    print "Executing: {}".format(command)
    result = subprocess.check_output(shlex.split(command))
    print "Output:\n{}".format(result)

commands = [

]
for command in commands:
    run_and_check(command)
