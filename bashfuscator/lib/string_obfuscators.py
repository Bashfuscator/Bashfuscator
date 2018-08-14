import math
import string
import hashlib

from bashfuscator.common.objects import Mutator

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
	def __init__(self, name, description, sizeRating, timeRating, fileWrite=False, credits=None):
		super().__init__(name, "string", credits)
		
		self.name = name
		self.description = description
		self.sizeRating = sizeRating
		self.timeRating = timeRating
		self.fileWrite = fileWrite
		self.originalCmd = ""
		self.payload = ""


class GlobObfuscator(StringObfuscator):
	def __init__(self, name, description, sizeRating, timeRating, credits=None):
		super().__init__(
			name=name,
			description=description,
			sizeRating=sizeRating,
			timeRating=timeRating,
			fileWrite=True,
			credits=credits
		)

		self.writeableDir = ""
		self.workingDir = ""
		self.minDirLen = None
		self.maxDirLen = None
		self.sectionSize = None
		# TODO: Maybe in the future, or make command line option:
		#self.charList = "".join(chr(i) for i in range(1, 127) if i != 37 and i != 47)
		self.charList = "0123456789abcdef"
		
	def generate(self, sizePref, userCmd, writeableDir=None):
		# TODO: create a tempDir option where the user can pick the dir to write to
		if writeableDir is None or writeableDir == "":
			self.writeableDir = ("/tmp/" + self.randGen.randUniqueStr(self.minDirLen, self.maxDirLen, self.charList))
		
		self.workingDir = self.writeableDir.replace("'","'\"'\"'")
		
		cmdChars = [userCmd[i:i + self.sectionSize] for i in range(0, len(userCmd), self.sectionSize)]
		cmdLen = len(cmdChars)
		cmdLogLen = int(math.ceil(math.log(cmdLen, 2)))
		if cmdLogLen <= 0:
			cmdLogLen = 1
		
		parts = []
		for i in range(cmdLen):
			ch = cmdChars[i]
			ch = ch.replace("'","'\"'\"'")
			parts.append(
				"printf -- '" + ch + "' > '" + self.workingDir + "/" + 
				format(i, '0' + str(cmdLogLen) + "b").replace("0", "?").replace("1", "\n") + "';"
			)
		self.randGen.randShuffle(parts)
		
		self.payload = ""
		self.payload += "mkdir -p '" + self.workingDir + "';"
		self.payload += "".join(parts)
		self.payload += "cat '" + self.workingDir + "'/" + "?" * cmdLogLen + ";"
		self.payload += "rm '"  + self.workingDir + "'/" + "?" * cmdLogLen + ";"
	
	def setSizes(self, sizePref, userCmd):
		if sizePref == 0:
			self.minDirLen = self.maxDirLen = 1
			self.sectionSize = int(len(userCmd) / 3 + 1)
		elif sizePref == 1:
			self.minDirLen = 1
			self.maxDirLen = 3
			self.sectionSize = int(len(userCmd) / 10 + 1)
		elif sizePref == 2:
			self.minDirLen = 6
			self.maxDirLen = 12
			self.sectionSize = int(len(userCmd) / 100 + 1)
		elif sizePref == 3:
			self.minDirLen = 12
			self.maxDirLen = 24
			self.sectionSize = 3
		elif sizePref == 4:
			self.minDirLen = self.maxDirLen = 32
			self.sectionSize = 1

class FileGlob(GlobObfuscator):
	def __init__(self):
		super().__init__(
			name="File Glob",
			description="Uses files and glob sorting to reassemble a string",
			sizeRating=5,
			timeRating=5,
			credits="elijah-barker"
		)

	def obfuscate(self, sizePref, userCmd):
		self.originalCmd = userCmd

		self.setSizes(sizePref, userCmd)
		self.generate(sizePref, userCmd)

		return self.payload


class FolderGlob(GlobObfuscator):
	def __init__(self):
		super().__init__(
			name="Folder Glob",
			description="Same as file glob, but better",
			sizeRating=5,
			timeRating=5,
			credits="elijah-barker"
		)

	def obfuscate(self, sizePref, userCmd):
		self.originalCmd = userCmd
		
		self.setSizes(sizePref, userCmd)
		self.writeableDir = ("/tmp/" + self.randGen.randUniqueStr(self.minDirLen, self.maxDirLen, self.charList))
		self.workingDir= self.writeableDir.replace("'", "'\"'\"'")
		
		cmdChunks = [userCmd[i:i + self.sectionSize] for i in range(0, len(userCmd), self.sectionSize)]
		parts=[]
		for chunk in cmdChunks:
			self.generate(sizePref, chunk, self.writeableDir + "/" + self.randGen.randUniqueStr(self.minDirLen, self.maxDirLen, self.charList))
			parts.append(self.payload)
			
		self.payload = "".join(parts)
		
		return self.payload
		

class HexHash(StringObfuscator):
	def __init__(self):
		super().__init__(
			name="Hex Hash",
			description="Uses the output of md5 to encode strings",
			sizeRating=5,
			timeRating=5,
			credits="elijah-barker"
		)
		
	def obfuscate(self, sizePref, userCmd):
		self.originalCmd = userCmd
		
		self.payload=""
		for ch in list(userCmd):
			hexchar = str(bytes(ch, "utf-8").hex())
			randomhash = ""

			while not hexchar in randomhash:
				m = hashlib.md5()
				randomString = self.randGen.randUniqueStr(1, 3)
				m.update(bytes(randomString, "utf-8"))
				randomhash = m.digest().hex()

			index = randomhash.find(hexchar)
			self.payload += 'printf -- "\\x$(printf \'' + randomString + "\'|md5sum|cut -b" + str(index + 1) + "-" + str(index + 2) + ')";\n'
		
		return self.payload
