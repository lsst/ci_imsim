import os.path
import argparse
import logging

import lsst.log
from lsst.daf.butler import Butler, FileDataset

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Re-export the YAML file used to ingest calibs, refcats, and masks."
    )
    parser.add_argument(
        "root",
        help="Path to input Gen3 butler to export from."
    )
    parser.add_argument(
        "filename",
        help="Path to output YAML file describing external files (usually resources/external.yaml)."
    )
    parser.add_argument(
        "collections",
        default=...,
        help="Collections to search for; default ellipsis (...)"
    )
    parser.add_argument("-v", "--verbose", action="store_const", dest="logLevel",
                        default=lsst.log.Log.INFO, const=lsst.log.Log.DEBUG,
                        help="Set the log level to DEBUG.")

    args = parser.parse_args()
    log = lsst.log.Log.getLogger("lsst.daf.butler")
    log.setLevel(args.logLevel)

    # Forward python logging to lsst logger
    lgr = logging.getLogger("lsst.daf.butler")
    lgr.setLevel(logging.INFO if args.logLevel == lsst.log.Log.INFO else logging.DEBUG)
    lgr.addHandler(lsst.log.LogHandler())

    butler = Butler(
        args.root,
        collections=[
            "LSSTCam-imSim/calib",
            "LSSTCam-imSim/calib/unbounded",
            "LSSTCam-imSim/calib/gen2/2022-01-01",
            "LSSTCam-imSim/calib/gen2/2022-08-06"
        ],
    )

    def rewrite(dataset: FileDataset) -> FileDataset:
        # Join the datastore root to the exported path.  This should yield
        # absolute paths that start with $CI_IMSIM_DIR.
        lgr.warning(f'{dataset.path}, {butler.datastore.root.ospath}')
        dataset.path = os.path.join(butler.datastore.root.ospath, dataset.path)
        lgr.warning(dataset.path)
        # Remove symlinks in the path; this should result in absolute paths
        # that start with $TESTDATA_CI_IMSIM_DIR, because ci_hsc_gen2 always
        # symlinks these datasets from there.
        dataset.path = os.path.realpath(dataset.path)
        lgr.warning(dataset.path)
        return dataset

    with butler.export(filename=args.filename) as export:
        for datasetTypeName in ("bias", "dark", "flat", "sky", "SKY", "cal_ref_cat_2_2"):
            export.saveDatasets(butler.registry.queryDatasets(datasetTypeName, collections=args.collections),
                                elements=(), rewrite=rewrite)
        for flattenChains in (True, False):
            for collection in butler.registry.queryCollections(args.collections, flattenChains=flattenChains):
                export.saveCollection(collection)
