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
import re

from lsst.daf.butler import Butler
from lsst.utils import getPackageDir
from lsst.resources import ResourcePath

butler = Butler(f'{os.environ["CI_IMSIM_DIR"]}/DATA', collections=['LSSTCam-imSim/runs/ci_imsim'])
skymap = list(butler.registry.queryDatasets(datasetType='objectTable_tract'))[0].dataId['skymap']


class TestHipsOutputs(unittest.TestCase):
    """Check that HIPS outputs are as expected."""
    def setUp(self):
        self.butler = Butler(os.path.join(getPackageDir("ci_imsim"), "DATA"),
                             instrument="LSSTCam-imSim", skymap=skymap,
                             writeable=False, collections=["LSSTCam-imSim/runs/ci_imsim_hips"])
        self._bands = ['u', 'g', 'r', 'i', 'z', 'y']
        self.hips_uri_base = ResourcePath(os.path.join(getPackageDir("ci_imsim"), "DATA", "hips"))

    def test_hips_exist(self):
        """Test that the HIPS images exist and are readable."""
        for band in self._bands:
            datasets = set(self.butler.registry.queryDatasets("deepCoadd_hpx", band=band))

            # There are 90 HiPS images for each band.
            self.assertEqual(len(datasets), 90)

            for dataset in datasets:
                self.assertTrue(self.butler.datastore.exists(dataset), msg="File exists for deepCoadd_hpx")

            exp = self.butler.get(list(datasets)[0])

            self.assertEqual(exp.wcs.getFitsMetadata()["CTYPE1"], "RA---HPX")
            self.assertEqual(exp.wcs.getFitsMetadata()["CTYPE2"], "DEC--HPX")

    def test_hips_trees_exist(self):
        """Test that the HiPS tree exists and has correct files."""
        for band in self._bands:
            self._check_hips_tree(self.hips_uri_base.join(f"band_{band}", forceDirectory=True))
        self._check_hips_tree(self.hips_uri_base.join("color_gri", forceDirectory=True), check_fits=False)

    def _check_hips_tree(self, hips_uri, check_fits=True):
        """Check a HiPS tree for files.

        Parameters
        ----------
        hips_uri : `lsst.resources.ResourcePath`
            URI of base of HiPS tree.
        check_fits : `bool`, optional
            Check if FITS images exist.
        """
        self.assertTrue(hips_uri.join("properties").exists(), msg="properties file not found.")
        self.assertTrue(hips_uri.join("Moc.fits").exists(), msg="Moc.fits file not found.")
        allsky = hips_uri.join("Norder3", forceDirectory=True).join("Allsky.png")
        self.assertTrue(allsky.exists(), msg="Allsky.png file not found.")

        for order in range(3, 12):
            order_uri = hips_uri.join(f"Norder{order}", forceDirectory=True)
            png_uris = list(
                ResourcePath.findFileResources(
                    candidates=[order_uri],
                    file_filter=re.compile(r'Npix.*\.png'),
                )
            )
            self.assertGreater(len(png_uris), 0, msg="No PNGs found.")

            if check_fits:
                fits_uris = list(
                    ResourcePath.findFileResources(
                        candidates=[order_uri],
                        file_filter=re.compile(r'Npix.*\.fits'),
                    )
                )
                self.assertEqual(len(fits_uris), len(png_uris), msg="Number of FITS != number of PNGs.")


if __name__ == "__main__":
    unittest.main()
