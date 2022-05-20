from argparse import ArgumentParser
import os
import subprocess

from lsst.ci.builder import CommandRunner, BuildState, BaseCommand
from lsst.ci.builder.commands import (CreateButler, RegisterInstrument, WriteCuratedCalibrations,
                                      RegisterSkyMap, IngestRaws, DefineVisits, ButlerImport,
                                      TestRunner)

TESTDATA_DIR = os.environ['TESTDATA_CI_IMSIM_DIR']
INSTRUMENT_NAME = "LSSTCam-imSim"
QGRAPH_FILE = "DRP.qgraph"
INPUTCOL = f"{INSTRUMENT_NAME}/defaults"
COLLECTION = f"{INSTRUMENT_NAME}/runs/ci_imsim"
HIPS_QGRAPH_FILE = "hips.qgraph"
HIPS_COLLECTION = f"{INSTRUMENT_NAME}/runs/ci_imsim_hips"

index_command = 0

ciRunner = CommandRunner(os.environ["CI_IMSIM_DIR"])
ciRunner.register("butler", 0)(CreateButler)


@ciRunner.register("instrument", index_command := index_command + 1)
class ImsimRegisterInstrument(RegisterInstrument):
    instrumentName = "lsst.obs.lsst.LsstCamImSim"


@ciRunner.register("write_calibrations", index_command := index_command + 1)
class ImsimWriteCuratedCalibrations(WriteCuratedCalibrations):
    instrumentName = INSTRUMENT_NAME


ciRunner.register("skymap", index_command := index_command + 1)(RegisterSkyMap)


@ciRunner.register("skymap_small", index_command := index_command + 1)
class RegisterSkyMapSmall(RegisterSkyMap):
    relativeConfigPath: str = os.path.join("configs", "skymap_small.py")

    @classmethod
    def addArgs(cls, parser: ArgumentParser):
        pass


@ciRunner.register("ingest", index_command := index_command + 1)
class ImsimIngestRaws(IngestRaws):
    rawLocation = os.path.join(TESTDATA_DIR, "raw")

    # TODO: Remove when DM-30607 is fixed (needed for MacOS only)
    def run(self, currentState: BuildState):
        self.arguments.num_cores, saveCores = '1', self.arguments.num_cores
        super().run(currentState)
        self.arguments.num_cores = saveCores


@ciRunner.register("define_visits", index_command := index_command + 1)
class ImsimDefineVisits(DefineVisits):
    instrumentName = INSTRUMENT_NAME
    collectionsName = f"{INSTRUMENT_NAME}/raw/all"

    # TODO: Remove when DM-30607 is fixed
    def run(self, currentState: BuildState):
        self.arguments.num_cores, saveCores = '1', self.arguments.num_cores
        super().run(currentState)
        self.arguments.num_cores = saveCores


@ciRunner.register("import_external", index_command := index_command + 1)
class ImsimBaseButlerImport(ButlerImport):
    dataLocation = TESTDATA_DIR

    @property
    def importFileLocation(self) -> str:
        return os.path.join(self.runner.pkgRoot, "resources", "external.yaml")


@ciRunner.register("qgraph", index_command := index_command + 1)
class QgraphCommand(BaseCommand):
    @classmethod
    def addArgs(cls, parser: ArgumentParser):
        parser.add_argument("--config-limit-deblend", dest="limit_deblend", action="store_true",
                            help="Whether to enable useCiLimits for deblending")
        parser.add_argument("--config-process-singles", dest="process_singles", action="store_true",
                            help="Whether to enable processSingles for deblending")

    def run(self, currentState: BuildState):
        args = (
            "--long-log",
            "qgraph",
            "-d", "skymap='discrete/ci_imsim/4k' AND tract=0 AND patch=24",
            "-b", self.runner.RunDir,
            "--input", INPUTCOL,
            "--output", COLLECTION,
            "-p", "$DRP_PIPE_DIR/pipelines/LSSTCam-imSim/DRP-ci_imsim.yaml",
            "--skip-existing",
            "--save-qgraph", os.path.join(self.runner.RunDir, QGRAPH_FILE),
            "--config", f"deblend:multibandDeblend.useCiLimits={self.arguments.limit_deblend}",
            "--config", f"calibrate:deblend.useCiLimits={self.arguments.limit_deblend}",
            "--config", f"deblend:multibandDeblend.processSingles={self.arguments.process_singles}",
        )
        pipetask = self.runner.getExecutableCmd("CTRL_MPEXEC_DIR", "pipetask", args)
        subprocess.run(pipetask, check=True)


@ciRunner.register("process", index_command := index_command + 1)
class ProcessingCommand(BaseCommand):
    def run(self, currentState: BuildState):
        args = (
            "--long-log",
            "run",
            "-j", str(self.arguments.num_cores),
            "-b", self.runner.RunDir,
            "--input", INPUTCOL,
            "--output", COLLECTION,
            "--register-dataset-types",
            "--skip-existing",
            "--qgraph", os.path.join(self.runner.RunDir, QGRAPH_FILE),
        )
        pipetask = self.runner.getExecutableCmd("CTRL_MPEXEC_DIR", "pipetask", args)
        subprocess.run(pipetask, check=True)


@ciRunner.register("hips_qgraph", index_command := index_command + 1)
class HipsQgraphCommand(BaseCommand):
    def run(self, currentState: BuildState):
        args = (
            "build",
            "-b", self.runner.RunDir,
            "-p", "$CI_IMSIM_DIR/resources/highres_hips.yaml",
            "-i", COLLECTION,
            "--pixels", str(33),
            "-q", os.path.join(self.runner.RunDir, HIPS_QGRAPH_FILE)
        )
        builder = self.runner.getExecutableCmd("PIPE_TASKS_DIR", "build-high-resolution-hips-qg", args)
        subprocess.run(builder, check=True)


@ciRunner.register("hips_process", index_command := index_command + 1)
class HipsProcessCommand(BaseCommand):
    def run(self, currentState: BuildState):
        args = (
            "--long-log",
            "run",
            "-j", str(self.arguments.num_cores),
            "-b", self.runner.RunDir,
            "--output", HIPS_COLLECTION,
            "--register-dataset-types",
            "-g", HIPS_QGRAPH_FILE
        )
        pipetask = self.runner.getExecutableCmd("CTRL_MPEXEC_DIR", "pipetask", args)
        subprocess.run(pipetask, check=True)


ciRunner.register("test", index_command := index_command + 1)(TestRunner)

ciRunner.run()
