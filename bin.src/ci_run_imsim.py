#!/usr/bin/env python

import os
import subprocess

from lsst.ci.builder import CommandRunner, BaseCommand, BuildState
from lsst.ci.builder.commands import (CreateButler, RegisterInstrument, WriteCuratedCalibrations,
                                      RegisterSkyMap, IngestRaws, DefineVisits, ButlerImport,
                                      TestRunner)

TESTDATA_DIR = os.environ['TESTDATA_CI_IMSIM_DIR']
INSTRUMENT_NAME = "LSSTCam-imSim"
INPUTCOL = f"{INSTRUMENT_NAME}/defaults"
COLLECTION = f"{INSTRUMENT_NAME}/runs/ci_imsim"
QGRAPH_FILE = "qgraph_file.qgraph"


ciRunner = CommandRunner(os.environ["CI_IMSIM_DIR"])


ciRunner.register("butler", 0)(CreateButler)


@ciRunner.register("instrument", 1)
class ImsimRegisterInstrument(RegisterInstrument):
    instrumentName = "lsst.obs.lsst.LsstCamImSim"


@ciRunner.register("calibrations", 2)
class ImsimWriteCuratedCalibrations(WriteCuratedCalibrations):
    instrumentName = INSTRUMENT_NAME


ciRunner.register("skymap", 3)(RegisterSkyMap)


@ciRunner.register("ingest", 4)
class ImsimIngestRaws(IngestRaws):
    rawLocation = os.path.join(TESTDATA_DIR, "raw")


@ciRunner.register("defineVisits", 5)
class ImsimDefineVisits(DefineVisits):
    instrumentName = INSTRUMENT_NAME
    collectionsName = f"{INSTRUMENT_NAME}/raw/all"


@ciRunner.register("importExternalBase", 6)
class ImsimBaseButlerImport(ButlerImport):
    dataLocation = TESTDATA_DIR

    @property
    def importFileLocation(self) -> str:
        return os.path.join(self.runner.pkgRoot, "resources", "external.yaml")


@ciRunner.register("qgraph", 8)
class QgraphCommand(BaseCommand):
    def run(self, currentState: BuildState):
        args = ("qgraph",
                "-d", '''skymap='discrete/ci_imsim' AND tract=0 AND patch=84''',
                "-b", self.runner.RunDir,
                "--input", INPUTCOL,
                "--output", COLLECTION,
                "-p", "$OBS_LSST_DIR/pipelines/imsim/DRP.yaml#singleFrame,multiVisit",
                "--config", "deblend:multibandDeblend.useCiLimits=True",
                "--config", "deblend:multibandDeblend.processSingles=False",
                "--config", "calibrate:deblend.useCiLimits=True",
                "--save-qgraph", os.path.join(self.runner.RunDir, QGRAPH_FILE))
        pipetask = self.runner.getExecutableCmd("CTRL_MPEXEC_DIR", "pipetask", args)
        subprocess.run(pipetask)


@ciRunner.register("processing", 9)
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


ciRunner.register("tests", 10)(TestRunner)

ciRunner.run()
