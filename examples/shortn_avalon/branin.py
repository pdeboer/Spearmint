import numpy as np
import math
import subprocess
import string
import random
import sys

def main(job_id, params):
    cmdParams = {item:params[item][0] for item in params.keys()}
    cmd = "python mysqlfunc.py \"%s\"" % cmdParams
    print "executing %s" % cmd
    p = subprocess.Popen(['/bin/bash', '-lc', cmd], stdout=subprocess.PIPE)
    p.wait()
    output = p.stdout.read()
    p.stdout.close()

    print output
    lines = string.split(output, "\n")

    retValue = float(lines[len(lines) - 2])
    print "returning %s" % retValue
    return retValue