########
ci_imsim
########

Description
===========

``ci_imsim`` provides test scripts to run the Rubin Observatory Science
Pipelines code on simulated data.

Test Data
=========

``ci_imsim`` requires the test data in the ``testdata_ci_imsim``
package, which must be set up via eups first.

Running Tests
=============

To run this package locally:

1) Clone this package, `ci_builder <https://github.com/lsst-dm/ci_builder>`_, and 
`testdata_ci_imsim <https://github.com/lsst-dm/testdata_ci_imsim>`_.
2) ``setup -r ci_builder``
3) ``setup -kr testdata_ci_imsim``
4) ``setup -kr ci_imsim``
5) From the root of this package directory run ``bin/rewrite.sh`` to rewrite python shebang lines.
6) Run ``bin/ci_imsim_run.py`` (see available options with ``--help``).

To cleanup after a run, use either ``bin/ci_imsim_run.py --clean`` or ``rm -rf DATA/``.

Note that there are 36 detector visits across 6 bands and 1 patch in
`testdata_ci_imsim`, 30 of which currently are coadded. Thus, running with
up to `-j 36` will speed up visit-level processing. Single-band coadd-level
processing will benefit from up to `-j 6`.

External Resources
==================

The provided ``resources/external.yaml`` can be re-generated using e.g.
``python bin.src/ci_imsim_export_external_data.py /repo/dc2 test.yaml
"2.2i/defaults/ci_imsim"``. Some of the generated paths may need to be
modified to match their paths in ``testdata_ci_imsim``.

