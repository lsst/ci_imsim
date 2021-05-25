# -*- python -*-
import os
from lsst.sconsUtils import scripts
from SCons.Script import Environment, SConscript

SConscript(os.path.join(".", "bin.src", "SConscript"))
# Python-only package
scripts.BasicSConstruct("ci_imsim", disableCc=True, noCfgFile=True)

env = Environment(ENV=os.environ)
env["ENV"]["OMP_NUM_THREADS"] = "1"  # Disable threading
PKG_ROOT = env.ProductDir("ci_imsim")

num_process = GetOption('num_jobs')

safe_python = os.path.join(PKG_ROOT, "bin", "sip_safe_python.sh")
command = os.path.join(PKG_ROOT, "bin", "ci_run_imsim.py")
run_ci = env.Command("DATA", "bin", ["{} {} -j {}".format(safe_python, command, num_process)])

env.Alias("all", run_ci)
Default(run_ci)

env.Clean(run_ci, ("DATA",))
