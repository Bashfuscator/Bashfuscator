from bashfuscator.modules.string_obfuscators.glob_obfuscators._glob_obfuscator import GlobObfuscator


class FileGlob(GlobObfuscator):
    def __init__(self):
        super().__init__(
            name="File Glob",
            description="Uses files and glob sorting to reassemble a string",
            sizeRating=5,
            timeRating=5,
            author="Elijah-Barker"
        )

    def mutate(self, userCmd):
        self.setSizes(userCmd)
        self.generate(userCmd)

        self.mangler.addPayloadLine(f"* *:rmdir:^ ^'{self.workingDir}'END0* *")

        return self.mangler.getFinalPayload()
