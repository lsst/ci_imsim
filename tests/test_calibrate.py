# This file is part of ci_imsim.
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import unittest
import numpy as np

from lsst.daf.butler import Butler
import lsst.utils.tests

from lsst.utils import getPackageDir


class TestReprocessVisitImageOutputs(lsst.utils.tests.TestCase):
    """Test the output data products of ReprocessVisitImageTask make sense.

    This is a regression test and not intended for scientific validation.
    """

    def setUp(self):
        self.butler = Butler(os.path.join(getPackageDir("ci_imsim"), "DATA"),
                             writeable=False, collections=["LSSTCam-imSim/runs/ci_imsim"])
        self.dataId = {"detector": 55, "visit": 206039, "band": "y"}
        self.exposure = self.butler.get("pvi", self.dataId)
        self.catalog = self.butler.get("sources_footprints_detector", self.dataId)

    def testLocalPhotoCalibColumns(self):
        """Check exposure's calibs are consistent with catalog's
        photocalib columns.
        """
        # Check that means are in the same ballpark
        exposureCalib = self.exposure.photoCalib.getCalibrationMean()
        exposureCalibErr = self.exposure.photoCalib.getCalibrationErr()
        catalogCalib = np.mean(self.catalog['base_LocalPhotoCalib'])
        catalogCalibErr = np.mean(self.catalog['base_LocalPhotoCalibErr'])

        self.assertAlmostEqual(exposureCalib, catalogCalib, places=3)
        self.assertAlmostEqual(exposureCalibErr, catalogCalibErr, places=3)

        # and that calibs evalutated at local positions match a few rows
        randomRows = [0, 8, 20]
        for rowNum in randomRows:
            record = self.catalog[rowNum]
            localEval = self.exposure.photoCalib.getLocalCalibration(record.getCentroid())
            self.assertAlmostEqual(localEval, record['base_LocalPhotoCalib'])

    def testLocalWcsColumns(self):
        """Check the initial_pvi's wcs match local wcs columns in initial_stars
        """
        # Check a few rows:
        randomRows = [1, 9, 21]
        for rowNum in randomRows:
            record = self.catalog[rowNum]
            centroid = record.getCentroid()
            trueCdMatrix = np.radians(self.exposure.wcs.getCdMatrix(centroid))

            self.assertAlmostEqual(record['base_LocalWcs_CDMatrix_1_1'], trueCdMatrix[0, 0])
            self.assertAlmostEqual(record['base_LocalWcs_CDMatrix_2_1'], trueCdMatrix[1, 0])
            self.assertAlmostEqual(record['base_LocalWcs_CDMatrix_1_2'], trueCdMatrix[0, 1])
            self.assertAlmostEqual(record['base_LocalWcs_CDMatrix_2_2'], trueCdMatrix[1, 1])
            self.assertAlmostEqual(
                self.exposure.wcs.getPixelScale(centroid).asRadians(),
                np.sqrt(np.fabs(record['base_LocalWcs_CDMatrix_1_1']*record['base_LocalWcs_CDMatrix_2_2']
                                - record['base_LocalWcs_CDMatrix_2_1']*record['base_LocalWcs_CDMatrix_1_2'])))


if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()
