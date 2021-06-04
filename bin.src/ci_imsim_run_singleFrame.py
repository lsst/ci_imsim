import os
import subprocess

from lsst.ci.builder import CommandRunner, BaseCommand, BuildState

INSTRUMENT_NAME = "LSSTCam-imSim"
INPUTCOL = f"{INSTRUMENT_NAME}/defaults"
COLLECTION = f"{INSTRUMENT_NAME}/runs/ci_imsim"
QGRAPH_FILE = "singleFrame.qgraph"

ciRunner = CommandRunner(os.environ["CI_IMSIM_DIR"])


class DummyCommand(BaseCommand):
    def run(self, currentState: BuildState):
        pass


# Both of these seem necessary
ciRunner.register("test", 0)(DummyCommand)
ciRunner.register("import_external", 1)(DummyCommand)


@ciRunner.register("qgraph_singleFrame", 2)
class QgraphCommand(BaseCommand):
    def run(self, currentState: BuildState):
        args = ("qgraph",
                "-d", "skymap='discrete/ci_imsim/4k' AND tract=0 AND patch=24",
                "-b", self.runner.RunDir,
                "--input", INPUTCOL,
                "--output", COLLECTION,
                "-p", "$OBS_LSST_DIR/pipelines/imsim/DRP.yaml#singleFrame",
                "--save-qgraph", os.path.join(self.runner.RunDir, QGRAPH_FILE))
        pipetask = self.runner.getExecutableCmd("CTRL_MPEXEC_DIR", "pipetask", args)
        subprocess.run(pipetask)


@ciRunner.register("process_singleFrame", 3)
class ProcessingCommand(BaseCommand):
    def run(self, currentState: BuildState):
        args = ("run",
                "-j", str(self.arguments.num_cores),
                "-b", self.runner.RunDir,
                "--input", INPUTCOL,
                "--output", COLLECTION,
                "--register-dataset-types",
                "--qgraph", os.path.join(self.runner.RunDir, QGRAPH_FILE))
        pipetask = self.runner.getExecutableCmd("CTRL_MPEXEC_DIR", "pipetask", args)
        subprocess.run(pipetask)


ciRunner.run()
