#!/usr/bin/env python

from argparse import ArgumentParser
import os

from lsst.ci.builder import CommandRunner, BuildState
from lsst.ci.builder.commands import (CreateButler, RegisterInstrument, WriteCuratedCalibrations,
                                      RegisterSkyMap, IngestRaws, DefineVisits, ButlerImport,
                                      TestRunner)

TESTDATA_DIR = os.environ['TESTDATA_CI_IMSIM_DIR']
INSTRUMENT_NAME = "LSSTCam-imSim"

ciRunner = CommandRunner(os.environ["CI_IMSIM_DIR"])
ciRunner.register("butler", 0)(CreateButler)


@ciRunner.register("instrument", 1)
class ImsimRegisterInstrument(RegisterInstrument):
    instrumentName = "lsst.obs.lsst.LsstCamImSim"


@ciRunner.register("write_calibrations", 2)
class ImsimWriteCuratedCalibrations(WriteCuratedCalibrations):
    instrumentName = INSTRUMENT_NAME


ciRunner.register("skymap", 3)(RegisterSkyMap)


@ciRunner.register("skymap_small", 4)
class RegisterSkyMapSmall(RegisterSkyMap):
    relativeConfigPath: str = os.path.join("configs", "skymap_small.py")

    @classmethod
    def addArgs(cls, parser: ArgumentParser):
        pass


@ciRunner.register("ingest", 5)
class ImsimIngestRaws(IngestRaws):
    rawLocation = os.path.join(TESTDATA_DIR, "raw")


@ciRunner.register("define_visits", 6)
class ImsimDefineVisits(DefineVisits):
    instrumentName = INSTRUMENT_NAME
    collectionsName = f"{INSTRUMENT_NAME}/raw/all"

    def run(self, currentState: BuildState):
        # Limit number of cores until DM-30607 is fixed
        self.arguments.num_cores, saveCores = '1', self.arguments.num_cores
        super().run(currentState)
        self.arguments.num_cores = saveCores


@ciRunner.register("import_external", 7)
class ImsimBaseButlerImport(ButlerImport):
    dataLocation = TESTDATA_DIR

    @property
    def importFileLocation(self) -> str:
        return os.path.join(self.runner.pkgRoot, "resources", "external.yaml")


ciRunner.register("test", 8)(TestRunner)

ciRunner.run()
