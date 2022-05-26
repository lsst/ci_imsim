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

import unittest
import os

from lsst.daf.butler import Butler
from lsst.utils import getPackageDir


class TestHipsOutputs(unittest.TestCase):
    """Check that HIPS outputs are as expected."""
    def setUp(self):
        self.butler = Butler(os.path.join(getPackageDir("ci_imsim"), "DATA"),
                             instrument="LSSTCam-imSim", skymap="discrete/ci_imsim/4k",
                             writeable=False, collections=["LSSTCam-imSim/runs/ci_imsim_hips"])
        self._bands = ['u', 'g', 'r', 'i', 'z', 'y']

    def test_hips_exist(self):
        """Test that the HIPS images exist and are readable."""
        for band in self._bands:
            datasets = set(self.butler.registry.queryDatasets("deepCoadd_hpx", band=band))

            # There are 90 HiPS images for each band.
            self.assertEqual(len(datasets), 90)

            for dataset in datasets:
                self.assertTrue(self.butler.datastore.exists(dataset), msg="File exists for deepCoadd_hpx")

            exp = self.butler.getDirect(list(datasets)[0])

            self.assertEqual(exp.wcs.getFitsMetadata()["CTYPE1"], "RA---HPX")
            self.assertEqual(exp.wcs.getFitsMetadata()["CTYPE2"], "DEC--HPX")


if __name__ == "__main__":
    unittest.main()
