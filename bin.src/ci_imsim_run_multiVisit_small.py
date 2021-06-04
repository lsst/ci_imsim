import os
import subprocess

from lsst.ci.builder import CommandRunner, BaseCommand, BuildState

INSTRUMENT_NAME = "LSSTCam-imSim"
INPUTCOL = f"{INSTRUMENT_NAME}/runs/ci_imsim"
COLLECTION = f"{INSTRUMENT_NAME}/runs/ci_imsim_2k"
QGRAPH_FILE = "multiVisit_small.qgraph"

ciRunner = CommandRunner(os.environ["CI_IMSIM_DIR"])


class DummyCommand(BaseCommand):
    def run(self, currentState: BuildState):
        pass


ciRunner.register("process_singleFrame", 0)(DummyCommand)
# User may have run coaddition or multiVisit last
ciRunner.register("process_coaddition", 1)(DummyCommand)
ciRunner.register("process_multiVisit", 2)(DummyCommand)


@ciRunner.register("qgraph_multiVisit_small", 3)
class QgraphCommand(BaseCommand):
    def run(self, currentState: BuildState):
        args = ("qgraph",
                "-d", "skymap='discrete/ci_imsim/2k' AND tract=0 AND patch=115",
                "-b", self.runner.RunDir,
                "--input", INPUTCOL,
                "--output", COLLECTION,
                "-p", "$OBS_LSST_DIR/pipelines/imsim/DRP.yaml#multiVisit",
                "--skip-existing",
                "--save-qgraph", os.path.join(self.runner.RunDir, QGRAPH_FILE))
        pipetask = self.runner.getExecutableCmd("CTRL_MPEXEC_DIR", "pipetask", args)
        subprocess.run(pipetask)


@ciRunner.register("process_multiVisit_small", 4)
class ProcessingCommand(BaseCommand):
    def run(self, currentState: BuildState):
        args = ("run",
                "-j", str(self.arguments.num_cores),
                "-b", self.runner.RunDir,
                "--input", INPUTCOL,
                "--output", COLLECTION,
                "--register-dataset-types",
                "--skip-existing",
                "--qgraph", os.path.join(self.runner.RunDir, QGRAPH_FILE))
        pipetask = self.runner.getExecutableCmd("CTRL_MPEXEC_DIR", "pipetask", args)
        subprocess.run(pipetask)


ciRunner.run()
