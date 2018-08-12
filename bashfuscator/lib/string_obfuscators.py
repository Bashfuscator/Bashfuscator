#!/usr/bin/python3

import math

from bashfuscator.common.obfuscator import Mutator

class StringObfuscator(Mutator):
	"""
	Base class for all string obfuscators. If an payload requires
	an eval to execute but has no stub, then it is a string obfuscator.
	
	:param name: name of the StringObfuscator
	:param description: short description of what the StringObfuscator does
	:param sizeRating: rating from 1 to 5 of how much the StringObfuscator 
	increases the size of the overall payload
	:param timeRating: rating from 1 to 5 of how much the StringObfuscator 
	increases the execution time of the overall payload
	:param reversible: This value should always be false.
	:param credits: whom or where inpiration for or the complete obfuscator 
	method was found at
	"""
	def __init__(self, name, description, sizeRating, timeRating, reversible=False, credits=None):
		super().__init__(name, "string", credits)
		
		self.name = name
		self.description = description
		self.sizeRating = sizeRating
		self.timeRating = timeRating
		self.reversible = reversible
		self.deobStub = None
		self.originalCmd = ""
		self.payload = ""


class Globfuscator(StringObfuscator):
	def __init__(self):
		super().__init__(
			name="globfuscator",
			description="Uses files and glob sorting to reassemble a string",
			sizeRating=5,
			timeRating=5,
			credits="elijah-barker"
		)
		
	def obfuscate(self, sizePref, userCmd, writeableDir="/tmp/bashfuscator"):
		self.originalCmd = userCmd
		self.workingDir=writeableDir.replace("'","'\"'\"'")
		
		if   sizePref == 4:
			self.blockSize = 1
		elif sizePref == 3:
			self.blockSize = 3
		elif sizePref == 2:
			self.blockSize = int(len(self.originalCmd)/100+1)
		elif sizePref == 1:
			self.blockSize = int(len(self.originalCmd)/10+1)
		elif sizePref == 0:
			self.blockSize = int(len(self.originalCmd)/3+1)
		
		self.cmdChars = [self.originalCmd[i:i+self.blockSize] for i in range(0, len(self.originalCmd),self.blockSize)]
		self.cmdLen = len(self.cmdChars)
		self.cmdLogLen = int(math.ceil(math.log(self.cmdLen,2)))
		
		self.parts=[]
		for i in range(self.cmdLen):
			ch=self.cmdChars[i]
			ch=ch.replace("'","'\"'\"'")
			self.parts.append(
				"echo -n '" + ch + "' > '" + self.workingDir + "/" + 
				format(i, '0' + str(self.cmdLogLen) + 'b').replace("0","?").replace("1", "\n") + "';"
			)
		self.randGen.randShuffle(self.parts)
		
		self.payload=""
		self.payload+="mkdir -p '" + self.workingDir + "';"
		self.payload+="".join(self.parts)
		self.payload+="cat '" + self.workingDir + "'/" + "?"*self.cmdLogLen + ";"
		self.payload+="rm '"  + self.workingDir + "'/" + "?"*self.cmdLogLen + ";"
		return self.payload

