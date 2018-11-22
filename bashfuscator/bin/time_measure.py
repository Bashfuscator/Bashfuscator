#!/usr/bin/env python3

#Imported Libraries
from subprocess import run
from tempfile import NamedTemporaryFile
import time
import timeit

import plotly
import plotly.graph_objs as go

from bashfuscator.core.obfuscation_handler import ObfuscationHandler


#Globals
longObfName="token/special_char_only"
#longObfName="string/hex_hash"
repeat_cmd=":\n"
unobfTimeData=[]
obfTimeData=[]
obfTimeMSCHAR=[]
unobfSizeData=[]
obfSizeData=[]

#list of times to run the command.  These values were chosen to work well on a logrithmic scale:
#iterations=["1", "2", "3", "4", "5", "10", "20", "30", "40", "50", "100", "200", "300", "400", "500", "1000", "2000", "3000", "4000", "5000", "10000", "20000", "30000"]
iterations=["1", "2", "3", "4", "5", "10", "20", "30", "40", "50", "100", "200", "300", "400", "500", "1000", "2000", "3000", "4000", "5000"]
#iterations=["1", "2", "3", "4", "5", "10", "20", "30", "40", "50", "100", "200", "300", "400", "500", "1000"]

#-------------------------------------------#
#Functions used to generate and process data#
#-------------------------------------------#

def timeRun(payload): #Returns double: time it took to run payload in bash subprocess
	repeater=5		#Set to 1 for testing, 5 or higher for actual analysis
	t=timeit.timeit(stmt=lambda: run(payload, executable="/bin/bash", shell=True), number=repeater)
	#Figure out a way to account for and subtract overhead?
	return t/repeater	#Return the average runtime

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
def plotObfTimeGrowth(iterations, obfExecutionTime):	#Generates and automatically opens graphs
	#Still a work in progress: I don't have the right numbers or processed lists yet.

	trace0 = go.Scatter(x = iterations, y = obfExecutionTime, mode = 'lines', name = 'Execution Time (MS/CHAR)')

	plotly.offline.plot({
    "data": [trace0],
    "layout": go.Layout(title=longObfName+": Obfuscated Time Growth",
		xaxis=dict(
        	type='log',
        	autorange=True
    	),
		yaxis=dict(autorange=True)
	)
	}, auto_open=True, filename='ObfuscatedTimeGrowth.html')

def plotRunTime(iterations, obfExecutionTime, unObfExecutionTime):
	trace0 = go.Scatter(x = iterations, y = obfExecutionTime, mode = 'lines', name = 'Obfuscated Execution Time (Total)')
	trace1 = go.Scatter(x = iterations, y= unObfExecutionTime, mode='lines', name = 'Unobfuscated Execution Time (Total)')
	plotly.offline.plot({
    "data": [trace0, trace1],
    "layout": go.Layout(title=longObfName+": Obfuscated Run Time",
		xaxis=dict(
        	type='log',
        	autorange=True
    	),
		yaxis=dict(autorange=True)
	)
	}, auto_open=True, filename='RunTime.html')

def plotSizeIncrease(iterations, unobfuscatedData, obfuscatedData):	#Does not return expected results, needs to be fixed.
	sizeDelta=[]
	for unobfuscated, obfuscated in zip(unobfuscatedData, obfuscatedData):
		#sizeDelta.append(((obfuscated - unobfuscated) / ((obfuscated + unobfuscated) / 2)) * 100)		#Percent difference, might not want *100, we'll see what it looks like.
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
	unobfTimeData.append(timeRun(inputCmd))
	print("Baseline time for {0} Iterations: {1}".format(i, unobfTimeData[-1]))

	#Obfuscate the command
	obfCommand=obHandler.genObfuscationLayer(inputCmd, userMutator=longObfName, enableMangling=False)

	obfSizeData.append(len(obfCommand))
	#Time run of obfuscated code
	print("Running Obfuscated code...")
	with NamedTemporaryFile(mode="w") as payloadFile:
		payloadFile.write(obfCommand)
		obfTime=timeRun(f"bash {payloadFile.name}")

	print(obfTime)
	obfTimeData.append(obfTime)
	obfTimeMSCHAR.append((obfTime)-unobfTimeData[-1]/(i*len(repeat_cmd)*1000))

#Plot Total Obfuscated & Unobfuscated run time
plotRunTime(iterations, obfTimeData, unobfTimeData)

#Generate TimeDeltaData for ObfTimeGrowth Graph
timeDeltaData=generateTimeDelta(obfTimeMSCHAR)
#Plot Delta-T graph: obfuscation time growth.  Need to discuss with the team exaclty how we want to do this, but... It's a good start.
plotObfTimeGrowth(iterations, timeDeltaData)

plotSizeIncrease(iterations, unobfSizeData, obfSizeData)
