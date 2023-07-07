import os.path
import argparse
import logging

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
                        default=logging.INFO, const=logging.DEBUG,
                        help="Set the log level to DEBUG.")

    args = parser.parse_args()

    collections = args.collections
    if collections == "...":
        collections = ...
    else:
        collections = collections.split(',')

    logging.basicConfig(level=logging.INFO)
    lgr = logging.getLogger("lsst.daf.butler")
    lgr.setLevel(args.logLevel)

    butler = Butler(
        args.root,
        collections=[
            "LSSTCam-imSim/calib",
            "LSSTCam-imSim/calib/unbounded",
            "LSSTCam-imSim/calib/gen2/2022-01-01",
            "LSSTCam-imSim/calib/gen2/2022-08-06",
            "truth_summary",
            "red_galaxies_cosmodc2",
        ],
    )

    datastore_roots = butler.get_datastore_roots()
    assert len(datastore_roots) == 1, "Export script requires a FileDatastore, not ChainedDatastore"
    datastore_root = list(datastore_roots.values())[0]
    assert datastore_root.schema == "file", "Export assumes POSIX datastore."

    def rewrite(dataset: FileDataset) -> FileDataset:
        # Join the datastore root to the exported path.  This should yield
        # absolute paths that start with $CI_IMSIM_DIR.
        abspath = datastore_root.join(dataset.path)
        # Remove symlinks in the path; this should result in absolute paths
        # that start with $TESTDATA_CI_IMSIM_DIR, because ci_imsim always
        # symlinks these datasets from there.
        dataset.path = os.path.realpath(abspath.ospath)
        return dataset

    with butler.export(filename=args.filename) as export:
        for datasetTypeName in (
                "bias",
                "dark",
                "flat",
                "sky",
                "SKY",
                "cal_ref_cat_2_2",
                "truth_summary",
                "cosmodc2_1_1_4_redmapper_v0_8_1_redgals"
        ):
            export.saveDatasets(butler.registry.queryDatasets(datasetTypeName, collections=collections),
                                elements=(), rewrite=rewrite)
        for flattenChains in (True, False):
            for collection in butler.registry.queryCollections(collections, flattenChains=flattenChains):
                export.saveCollection(collection)
