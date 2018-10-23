#!/usr/bin/env python

#Imported Libraries
import time
from subprocess import STDOUT, PIPE, Popen
from bashfuscator.core.obfuscation_handler import ObfuscationHandler

#Functions
def timeRun(payload):
	start_time = time.time()            #Start Timer
	proc = Popen(payload, executable="/bin/bash", stdout=PIPE, stderr=STDOUT, shell=True, universal_newlines=True)
	#stdout, __ = proc.communicate()
	return time.time() - start_time		#End Timer and return

#Variables
repeat_cmd=":;\n"
len_cmd = len(repeat_cmd)-1
#list of times to run the command:
iterations=["1", "2", "3", "4", "5", "10", "20", "30", "40", "50", "100", "200", "300", "400", "500", "1000", "2000", "3000", "4000", "5000", "10000", "20000", "30000", "40000", "50000"]

for i in iterations:        #Yo Dawg, I heard you liked iterations.  So I iterated over your iterations.
	i=int(i)
	payload = repeat_cmd * i

	#Generate a baseline time (how long it takes to run unobfuscated)
	print("Baseline time for {0} Iterations: {1}".format(i, timeRun(payload)))
	
	#Obfuscate the command
	obHandler = ObfuscationHandler()
	obfCommand=obHandler.genObfuscationLayer(payload, "string/hex_hash")

	#Time run of obfuscated code
	print("Running Obfuscated code...")
	print(timeRun(payload))
	print("\n")
