#!/usr/bin/env python3

#Imported Libraries
from subprocess import run
from tempfile import NamedTemporaryFile
import timeit
from argparse import ArgumentTypeError, ArgumentParser

import numpy as np
from numpy.polynomial.polynomial import polyfit
import plotly
import plotly.graph_objs as go

from bashfuscator.core.obfuscation_handler import ObfuscationHandler


#Arg Parsing & Global Declarations
parser =ArgumentParser()
parser.add_argument("-m", "--mutator", help="Path of the mutator to test.  For example, string/hex_hash")
parser.add_argument("-r", "--repeat", type=int, default=5, help="Number of times to repeat the test. Default is 5.")
parser.add_argument("-n", "--datapoints", type=int, default=20, help="Number of datapoints.  Default is 20.")
parser.add_argument("-s", "--max-input-size", type=int, default=2000, help="Maximum size of the final input size")
parser.add_argument("-o", "--output-dir", type=str, default="", help="Directory to write graphs to")

args=parser.parse_args()

longObfName=args.mutator
mutatorType=longObfName.split("/")[0]
repeater=args.repeat
outputDir=args.output_dir + mutatorType + "/"

repeat_cmd=":\n"
unobfTimeData=[]
obfTimeData=[]
unobfSizeData=[]
obfSizeData=[]

#list of times to run the command:
iterations = np.linspace(1, args.max_input_size, num=args.datapoints)

#-------------------------------------------#
#Functions used to generate and process data#
#-------------------------------------------#

def timeRun(payload, repeater): #Returns double: time it took to run payload in bash subprocess
	numRepeats=repeater
	t=timeit.timeit(stmt=lambda: run(payload, executable="/bin/bash", shell=True), number=numRepeats)
	return t/numRepeats	#Return the average runtime


#---------------------------#
#Functions used to plot data#
#---------------------------#

def plotRunTime(iterations, obfExecutionTime, unObfExecutionTime):
	trace0 = go.Scatter(x = iterations, y = obfExecutionTime, mode = 'lines', name = 'Obfuscated Execution Time (Total)')
	trace1 = go.Scatter(x = iterations, y= unObfExecutionTime, mode='lines', name = 'Unobfuscated Execution Time (Total)')
	trace2 = go.Scatter(x = iterations, y= np.poly1d(np.polyfit(iterations, obfExecutionTime, 1))(iterations), mode='lines', name = 'Average Runtime Increase')
	plotly.offline.plot({
    "data": [trace0, trace1, trace2],
    "layout": go.Layout(title=longObfName+": Obfuscated Run Time",
		legend=dict(orientation="h"),
		xaxis=dict(autorange=True, title='Command Length (Characters)'),
		yaxis=dict(autorange=True, title='Execution Time (Seconds)')
	)
	}, auto_open=True, filename=outputDir + "runtime_graph.html")

def plotSizeIncrease(iterations, unobfuscatedData, obfuscatedData):
	sizeDelta=[]
	for obfuscated in obfuscatedData:
		sizeDelta.append(obfuscated)

	trace0 = go.Scatter(x = iterations, y=sizeDelta, mode='lines', name= 'Size Difference Ratio')
	trace1 = go.Scatter(x = iterations, y= np.poly1d(np.polyfit(iterations, sizeDelta, 1))(iterations), mode='lines', name = 'Average Size Increase')
	plotly.offline.plot({
    "data": [trace0, trace1],
    "layout": go.Layout(title=longObfName+": Obfuscated Size Growth",
		legend=dict(orientation="h"),
		xaxis=dict(autorange=True, title='Original Command Length (Characters)'),
		yaxis=dict(autorange=True, title='Obfuscated Command Length (Characters)')
	)
	}, auto_open=True, filename=outputDir + "size_graph.html")

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
	obfCommand=obHandler.genObfuscationLayer(inputCmd, userMutator=longObfName, enableMangling=False, writeDir="/mnt/tmpfs")

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
