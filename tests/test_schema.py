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
import yaml

from lsst.daf.butler import Butler
import lsst.utils.tests

from lsst.utils import getPackageDir

butler = Butler(
    f'{os.environ["CI_IMSIM_DIR"]}/DATA', collections=["LSSTCam-imSim/runs/ci_imsim"]
)
skymap = list(butler.registry.queryDatasets(datasetType="objectTable_tract"))[0].dataId[
    "skymap"
]


class TestSchemaMatch(lsst.utils.tests.TestCase):
    """Check the schema of the parquet outputs match the DDL in sdm_schemas"""

    def setUp(self):
        self.butler = Butler(
            os.path.join(getPackageDir("ci_imsim"), "DATA"),
            writeable=False,
            collections=["LSSTCam-imSim/runs/ci_imsim"],
        )
        schemaFile = os.path.join(getPackageDir("sdm_schemas"), "yml", "imsim.yaml")
        with open(schemaFile, "r") as f:
            self.schema = yaml.safe_load(f)["tables"]

    def _validateSchema(self, dataset, dataId, tableName):
        """Check column name and data type match between dataset and DDL"""
        info = f"dataset={dataset} tableName={tableName} dataId={dataId}"

        sdmSchema = [table for table in self.schema if table["name"] == tableName]
        self.assertEqual(len(sdmSchema), 1)
        expectedColumns = {
            column["name"]: column["datatype"] for column in sdmSchema[0]["columns"]
        }

        df = self.butler.get(dataset, dataId, storageClass="DataFrame")
        df.reset_index(inplace=True)

        outputColumnNames = df.columns.to_list()
        if "index" in outputColumnNames:
            outputColumnNames.remove("index")
        if "index" in expectedColumns:
            expectedColumns.pop("index")
        self.assertEqual(
            set(outputColumnNames), set(expectedColumns.keys()), f"{info} failed"
        )

        # the data type mapping from felis datatype to pandas
        typeMapping = {
            "boolean": "^bool$",
            "short": "^int16$",
            "int": "^int32$",
            "long": "^int64$",
            "float": "^float32$",
            "double": "^float64$",
            "char": "^object$",
            "timestamp": r"^datetime64\[[un]s\]$",
        }
        for column in outputColumnNames:
            self.assertRegex(
                df.dtypes.get(column).name,
                typeMapping[expectedColumns[column]],
                f"{info} column={column} failed",
            )

    def testObjectSchemaMatch(self):
        """Check objectTable_tract"""
        dataId = {"instrument": "LSSTCam-imSim", "tract": 0, "skymap": skymap}
        self._validateSchema("objectTable_tract", dataId, "Object")

    def testSourceSchemaMatch(self):
        """Check one sourceTable_visit"""
        dataId = {
            "instrument": "LSSTCam-imSim",
            "detector": 100,
            "visit": 5884,
            "band": "y",
        }
        self._validateSchema("sourceTable_visit", dataId, "Source")

    def testForcedSourceSchemaMatch(self):
        """Check forcedSourceTable_tract"""
        dataId = {"instrument": "LSSTCam-imSim", "tract": 0, "skymap": skymap}
        self._validateSchema("forcedSourceTable_tract", dataId, "ForcedSource")

    def testDiaObjectSchemaMatch(self):
        """Check diaObjectTable_tract"""
        dataId = {"instrument": "LSSTCam-imSim", "tract": 0, "skymap": skymap}
        self._validateSchema("diaObjectTable_tract", dataId, "DiaObject")

    def testDiaSourceSchemaMatch(self):
        """Check one diaSourceTable_tract"""
        dataId = {"instrument": "LSSTCam-imSim", "tract": 0, "skymap": skymap}
        self._validateSchema("diaSourceTable_tract", dataId, "DiaSource")

    def testForcedSourceeOnDiaObjectSchemaMatch(self):
        """Check forcedSourceOnDiaObjectTable_tract"""
        dataId = {"instrument": "LSSTCam-imSim", "tract": 0, "skymap": skymap}
        self._validateSchema(
            "forcedSourceOnDiaObjectTable_tract", dataId, "ForcedSourceOnDiaObject"
        )

    def testMatchRefSchemaMatch(self):
        """Check match_ref_truth_summary_objectTable_tract"""
        dataId = {"instrument": "LSSTCam-imSim", "tract": 0, "skymap": skymap}
        self._validateSchema(
            "match_ref_truth_summary_objectTable_tract", dataId, "MatchesTruth"
        )

    def testMatchObjectSchemaMatch(self):
        """Check match_target_truth_summary_objectTable_tract"""
        dataId = {"instrument": "LSSTCam-imSim", "tract": 0, "skymap": skymap}
        self._validateSchema(
            "match_target_truth_summary_objectTable_tract", dataId, "MatchesObject"
        )


if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()
