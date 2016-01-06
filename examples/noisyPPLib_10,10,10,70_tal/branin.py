import numpy as np
import math
import subprocess
import string
# Write a function like this called 'main'
def main(job_id, params):
    print 'Anything printed here will end up in the output directory for job #%d' % job_id
    print params

    target = open("jobdesc_%d.txt" % job_id, 'w')
    target.write("/maxIterations VALUE "+str(params["/maxIterations"][0])+"\n")
    target.write("/confidence VALUE "+str(params["/confidence"][0])+"\n")
    target.write("/k VALUE "+str(params["/k"][0])+"\n")
    target.write("/workerCount VALUE "+str(params["/workerCount"][0])+"\n")
    target.write("baseclass VALUE "+params["baseclass"][0])
    target.close()

    cmd = 'cd /home/user/pdeboer/PPLib && sbt "run-main ch.uzh.ifi.pdeboer.pplib.examples.optimization.MCOptimize /home/user/pdeboer/bo/Spearmint/examples/noisyPPLib_10,10,10,70_tal/jobdesc_'+str(job_id)+'.txt answers10,10,10,70"'
    print "will execute "+cmd
    p = subprocess.Popen(['/bin/bash', '-c', cmd], stdout=subprocess.PIPE)
    p.wait()
    output = p.stdout.read()
    p.stdout.close()
    print "process output was:"
    print output
    print "interpreting.."


    lines = string.split(output, "\n")
    relevantLine = lines[len(lines) - 3]
    consoleString = string.split(relevantLine, " ")[1]
    consolePrefix = len("\x1b[0m")
    floatString = consoleString[consolePrefix:len(consoleString) - consolePrefix]
    print "got float string " + floatString
    #return {'branin': float(floatString)}
    return float(floatString)

#return branin(params['/maxIterations'], params['/confidence'], params['/k'], params['/workerCount'])
