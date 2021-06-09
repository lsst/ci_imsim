########
ci_imsim
########



.. Add a brief (few sentence) description of what this package provides.

To run this package locally:
1) clone and setup ci_builder from https://github.com/lsst-dm/ci_builder
2) clone this package
3) setup this package
4) From the root of the package directory run ``bin/rewrite.sh`` to
   rewrite python shebang lines
5) run ``bin/ci_imsim_run.py`` (see available options with ``--help``)

External Resources
==================

The provided ``resources/external.yaml`` can be re-generated using e.g.
``bin.src/ci_imsim_export_external_data.py /repo/dc2 test.yaml
"2.2i/defaults/ci_imsim"``. Some of the generated paths may need to be
modified to match their paths in ``testdata_ci_imsim``.
