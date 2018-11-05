#!/usr/bin/env python3

#Imported Libraries
import time
import timeit
import plotly
import plotly.graph_objs as go
from subprocess import STDOUT, PIPE, Popen
from bashfuscator.core.obfuscation_handler import ObfuscationHandler


#Globals
longObfName="token/special_char_only"
repeat_cmd=":;\n"
unobfTimeData=[]
obfTimeData=[]

#list of times to run the command.  These values were chosen to work well on a logrithmic scale:
#iterations=["1", "2", "3", "4", "5", "10", "20", "30", "40", "50", "100", "200", "300", "400", "500", "1000", "2000", "3000", "4000", "5000", "10000", "20000", "30000", "40000", "50000"]
iterations=["1", "2", "3", "4", "5", "10", "20", "30", "40", "50", "100", "200", "300", "400", "500", "1000", "2000", "3000", "4000", "5000", "10000", "20000", "30000"]

#Functions
def timeRun(payload): #Returns double: time it took to run payload in bash

	mysetup='''from subprocess import STDOUT, PIPE, Popen
from __main__ import payload, runProcess'''
	snippet="runProcess(payload)"
	t=timeit.timeit(setup=mysetup, stmt=snippet, number=1)
	print(t)
	return t

def runProcess(payload):
	proc = Popen(payload, executable="/bin/bash", stdout=PIPE, stderr=STDOUT, shell=True, universal_newlines=True)

	while proc.poll() is None:
		time.sleep(0)

	return

def plotAllTheThings(xList, yList, Title):
	#Still a work in progress: I don't have the right numbers or processed lists yet.
	plotly.offline.plot({
    "data": [go.Scatter(x=xList, y=yList)],
    "layout": go.Layout(title=Title,
		xaxis=dict(
        	type='log',
        	autorange=True
    	)
	)
	}, auto_open=True)


#Add try catch
for i in iterations:        #Yo Dawg, I heard you liked iterations.  So I iterated over your iterations.
	j=0 #Index counter for list maniputlation
	i=int(i)
	payload = repeat_cmd * i

	#Generate a baseline time (how long it takes to run unobfuscated)
	unobfTimeData.append(timeRun(payload))
	print("Baseline time for {0} Iterations: {1}".format(i, unobfTimeData[-1]))


	#Obfuscate the command
	obHandler = ObfuscationHandler()
	obfCommand=obHandler.genObfuscationLayer(payload, userMutator=longObfName, enableMangling=None)

	#Time run of obfuscated code
	print("Running Obfuscated code...")
	##$n/$len_cmd"*1000"
	obfTime=timeRun(obfCommand)
	print(obfTime)
	#obfTimeData.append((obfTime-unobfTimeData[-1])/(i*len(repeat_cmd)*1000))	#Append to list
	obfTimeData.append(obfTime)

plotAllTheThings(iterations, obfTimeData, longObfName)