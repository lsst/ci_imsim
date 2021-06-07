# -*- python -*-
import os
import shutil
from lsst.sconsUtils import scripts
from SCons.Script import Environment, SConscript, AlwaysBuild, Glob

SConscript(os.path.join(".", "bin.src", "SConscript"))
# Python-only package
scripts.BasicSConstruct("ci_imsim", disableCc=True, noCfgFile=True)

env = Environment(ENV=os.environ)
env["ENV"]["OMP_NUM_THREADS"] = "1"  # Disable threading
PKG_ROOT = env.ProductDir("ci_imsim")

num_process = GetOption('num_jobs')

path_data = os.path.join(PKG_ROOT, "DATA")

if os.path.isdir(path_data):
    shutil.rmtree(path_data)

safe_python = os.path.join(PKG_ROOT, "bin", "sip_safe_python.sh")

cmd_run = env.Command(
    os.path.join(path_data),
    "bin",
    f"{safe_python} {os.path.join(PKG_ROOT, 'bin', 'ci_imsim_run.py')} -j {num_process}",
)
AlwaysBuild(cmd_run)

everything = [cmd_run]
env.Alias("all", everything)
Default(everything)

env.Clean(everything, ("DATA",))
