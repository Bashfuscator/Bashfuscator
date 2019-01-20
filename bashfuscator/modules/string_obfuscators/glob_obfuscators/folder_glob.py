from bashfuscator.modules.string_obfuscators.glob_obfuscators._glob_obfuscator import GlobObfuscator


class FolderGlob(GlobObfuscator):
    def __init__(self):
        super().__init__(
            name="Folder Glob",
            description="Same as file glob, but better",
            sizeRating=5,
            timeRating=5,
            author="Elijah-Barker"
        )

    def mutate(self, userCmd):
        self.setSizes(userCmd)

        cmdChunks = [userCmd[i:i + self.sectionSize] for i in range(0, len(userCmd), self.sectionSize)]

        for chunk in cmdChunks:
            self.generate(chunk, self.randGen.randUniqueStr())
            self.mangler.addPayloadLine(f"* *:rmdir:^ ^'{self.workingDir}'END0")

        self.mangler.addPayloadLine(f"* *:rmdir:^ ^'{self.startingDir}'END0* *")

        return self.mangler.getFinalPayload()
