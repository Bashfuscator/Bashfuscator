#!/usr/bin/env python3

#Imported Libraries
from subprocess import run
from tempfile import NamedTemporaryFile
import timeit
from argparse import ArgumentTypeError, ArgumentParser

import plotly
import plotly.graph_objs as go
from numpy import linspace

from bashfuscator.core.obfuscation_handler import ObfuscationHandler


#Arg Parsing & Global Declarations
parser =ArgumentParser()
parser.add_argument("-m", "--mutator", help="Path of the mutator to test.  For example, string/hex_hash")
parser.add_argument("-r", "--repeat", type=int, help="Number of times to repeat the test.")

args=parser.parse_args()

longObfName=args.mutator
repeater=args.repeat

repeat_cmd=":\n"
unobfTimeData=[]
obfTimeData=[]
unobfSizeData=[]
obfSizeData=[]

#list of times to run the command:
iterations = linspace(1, 1000, num=20)

#-------------------------------------------#
#Functions used to generate and process data#
#-------------------------------------------#

def timeRun(payload, repeater): #Returns double: time it took to run payload in bash subprocess
	numRepeats=repeater		#Set to 1 for testing, 5 or higher for actual analysis (It will take forever if you go much higher than 7, but it returns "smoother" results)
	t=timeit.timeit(stmt=lambda: run(payload, executable="/bin/bash", shell=True), number=numRepeats)
	return t/numRepeats	#Return the average runtime

def generateTimeDelta(obfuscatedData):	#Depending on how I store obfuscated execution times, may have to ms/char maniputlation in this function.
	timeDeltaData=[]
	i=0 #Counter
	for obfuscated in obfuscatedData:
		if not timeDeltaData:
			timeDeltaData.append(0)		#First value in the list is always zero
		else:
			timeDeltaData.append(obfuscated-obfuscatedData[i-1])
		i+=1
	return timeDeltaData

#---------------------------#
#Functions used to plot data#
#---------------------------#

def plotRunTime(iterations, obfExecutionTime, unObfExecutionTime):
	trace0 = go.Scatter(x = iterations, y = obfExecutionTime, mode = 'lines', name = 'Obfuscated Execution Time (Total)')
	trace1 = go.Scatter(x = iterations, y= unObfExecutionTime, mode='lines', name = 'Unobfuscated Execution Time (Total)')
	plotly.offline.plot({
    "data": [trace0, trace1],
    "layout": go.Layout(title=longObfName+": Obfuscated Run Time",
		xaxis=dict(autorange=True),
		yaxis=dict(autorange=True)
	)
	}, auto_open=True, filename='RunTime.html')

def plotSizeIncrease(iterations, unobfuscatedData, obfuscatedData):	#Does not return expected results, needs to be fixed.
	sizeDelta=[]
	for obfuscated in obfuscatedData:
		sizeDelta.append(obfuscated)

	trace0=go.Scatter(x = iterations, y=sizeDelta, mode='lines', name= 'Size Difference Ratio')
	plotly.offline.plot({
    "data": [trace0],
    "layout": go.Layout(title=longObfName+": Obfuscated Size Growth",
		xaxis=dict(autorange=True),
		yaxis=dict(autorange=True)
	)
	}, auto_open=True, filename='SizeDelta.html')

#------------------------#
#-----Actual Script------#
#------------------------#


#Add try catch
obHandler = ObfuscationHandler()

for i in iterations:		#Yo Dawg, I heard you liked iterations.  So I iterated over your iterations.
	#j=0 #Index counter for list maniputlation
	i=int(i)
	inputCmd = repeat_cmd * i

	unobfSizeData.append(len(inputCmd))
	#Generate a baseline time (how long it takes to run unobfuscated)
	unobfTimeData.append(timeRun(inputCmd, repeater))
	print("Baseline time for {0} Iterations: {1}".format(i, unobfTimeData[-1]))

	#Obfuscate the command
	obfCommand=obHandler.genObfuscationLayer(inputCmd, userMutator=longObfName, enableMangling=False)

	obfSizeData.append(len(obfCommand))
	#Time run of obfuscated code
	print("Running Obfuscated code...")
	with NamedTemporaryFile(mode="w") as payloadFile:
		payloadFile.write(obfCommand)
		obfTime=timeRun(f"bash {payloadFile.name}", repeater)

	print(obfTime)
	obfTimeData.append(obfTime)

#Plot Total Obfuscated & Unobfuscated run time and Size Increase
plotRunTime(iterations, obfTimeData, unobfTimeData)
plotSizeIncrease(iterations, unobfSizeData, obfSizeData)
