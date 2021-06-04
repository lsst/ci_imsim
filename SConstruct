# -*- python -*-
import os
from lsst.sconsUtils import scripts
from SCons.Script import Environment, SConscript, AlwaysBuild, Glob

SConscript(os.path.join(".", "bin.src", "SConscript"))
# Python-only package
scripts.BasicSConstruct("ci_imsim", disableCc=True, noCfgFile=True)

env = Environment(ENV=os.environ)
env["ENV"]["OMP_NUM_THREADS"] = "1"  # Disable threading
PKG_ROOT = env.ProductDir("ci_imsim")

num_process = GetOption('num_jobs')

safe_python = os.path.join(PKG_ROOT, "bin", "sip_safe_python.sh")

everything = []
script_infos = [
    (("ci_imsim_setup.py",), "DATA/butler.yaml"),
    (("ci_imsim_run_singleFrame.py",), "DATA/LSSTCam-imSim/runs/ci_imsim"),
    (("ci_imsim_run_coaddition.py", "ci_imsim_run_multiVisit.py"), "DATA/LSSTCam-imSim/runs/ci_imsim_4k"),
]

for scripts, target in script_infos:
    command = env.Command(
        target,
        [x for x in everything],
        " && ".join((
            f"{safe_python} {os.path.join(PKG_ROOT, 'bin', script)} -j {num_process}"
            for script in scripts
        )),
    )
    AlwaysBuild(command)
    everything.append(command)

env.Alias("all", everything)
Default(everything)

env.Clean(everything, ("DATA",))
