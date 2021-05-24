# -*- python -*-
import os
from lsst.sconsUtils import scripts
from SCons.Script import Environment, SConscript

SConscript(os.path.join(".", "bin.src", "SConscript"))
# Python-only package
scripts.BasicSConstruct("ci_imsim", disableCc=True, noCfgFile=True)

env = Environment(ENV=os.environ)
env["ENV"]["OMP_NUM_THREADS"] = "1"  # Disable threading

num_process = GetOption('num_jobs')

run_ci = env.Command("DATA", "bin", ["bin/ci_run_imsim.py -j {}".format(num_process)])

env.Alias("all", run_ci)
Default(run_ci)

env.Clean(run_ci, ("DATA",))
