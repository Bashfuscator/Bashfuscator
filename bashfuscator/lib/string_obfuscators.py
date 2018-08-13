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

	def evalWrap(self):
		self.payload = '''"$({1})" "$({0})"'''.format(self.payload, self.obfuscate(4, "eval", evalWrappingCall=True))


class FileGlob(StringObfuscator):
	def __init__(self,
			name="File Glob",
			description="Uses files and glob sorting to reassemble a string",
			sizeRating=5,
			timeRating=5,
			credits="elijah-barker"):
		super().__init__(
			name=name,
			description=description,
			sizeRating=sizeRating,
			timeRating=timeRating,
			credits=credits
		)
		
	def generate(self, sizePref, userCmd, writeableDir):
		
		if writeableDir == None or writeableDir == "":
			writeableDir = ("/tmp/" + self.randGen.randGenStr(32,32,"0123456789abcdef"))
		self.workingDir=writeableDir.replace("'","'\"'\"'")
		
		if sizePref == 4:
			blockSize = 1
		elif sizePref == 3:
			blockSize = 3
		elif sizePref == 2:
			blockSize = int(len(userCmd)/100+1)
		elif sizePref == 1:
			blockSize = int(len(userCmd)/10+1)
		elif sizePref == 0:
			blockSize = int(len(userCmd)/3+1)
		
		cmdChars = [userCmd[i:i+blockSize] for i in range(0, len(userCmd),blockSize)]
		cmdLen = len(cmdChars)
		cmdLogLen = int(math.ceil(math.log(cmdLen,2)))
		if cmdLogLen <= 0:
			cmdLogLen = 1
		
		parts = []
		for i in range(cmdLen):
			ch = cmdChars[i]
			ch = ch.replace("'","'\"'\"'")
			parts.append(
				"printf -- '" + ch + "' > '" + self.workingDir + "/" + 
				format(i, '0' + str(cmdLogLen) + 'b').replace("0","?").replace("1", "\n") + "';"
			)
		self.randGen.randShuffle(parts)
		
		self.payload = ""
		self.payload += "mkdir -p '" + self.workingDir + "';"
		self.payload += "".join(parts)
		self.payload += "cat '" + self.workingDir + "'/" + "?" * cmdLogLen + ";"
		self.payload += "rm '"  + self.workingDir + "'/" + "?" * cmdLogLen + ";"
	
	def obfuscate(self, sizePref, userCmd, writeableDir=None, evalWrappingCall=False):
		
		self.generate(sizePref, userCmd, writeableDir)
		if not evalWrappingCall:
			self.evalWrap()
		return self.payload


class FolderGlob(FileGlob):
	def __init__(self):
		super().__init__(
			name="Folder Glob",
			description="Same as file glob, but better",
			sizeRating=5,
			timeRating=5,
			credits="elijah-barker"
		)

	def obfuscate(self, sizePref, userCmd, writeableDir=None, evalWrappingCall=False):
		
		if writeableDir == None or writeableDir == "":
			writeableDir = ("/tmp/"+self.randGen.randGenStr(32,32,"0123456789abcdef"))
		self.workingDir=writeableDir.replace("'","'\"'\"'")
		
		if sizePref == 4:
			folderSize = 1
		elif sizePref == 3:
			folderSize = 3
		elif sizePref == 2:
			folderSize = int(len(userCmd)/100+1)
		elif sizePref == 1:
			folderSize = int(len(userCmd)/10+1)
		elif sizePref == 0:
			folderSize = int(len(userCmd)/3+1)
		
		cmdChunks = [userCmd[i:i+folderSize] for i in range(0, len(userCmd),folderSize)]
		parts=[]
		for chunk in cmdChunks:
			self.generate(sizePref, chunk, writeableDir + "/" + self.randGen.randGenStr(32,32,"0123456789abcdef"))
			parts.append(self.payload)
			
		self.payload = "".join(parts)
		
		if not evalWrappingCall:
			self.evalWrap()
		
		return self.payload
