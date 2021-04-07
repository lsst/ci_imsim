"""Sphinx configuration file for an LSST stack package.

This configuration only affects single-package Sphinx documentation builds.
"""

from documenteer.sphinxconfig.stackconf import build_package_configs
import lsst.ci.imsim


_g = globals()
_g.update(build_package_configs(
    project_name='ci_imsim',
    version=lsst.ci.imsim.version.__version__))
