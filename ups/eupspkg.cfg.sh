prep(){
    bin/rewrite.sh
}

config(){
    # verify that the working directory is clean
    bin/sip_safe_python.sh bin/ci_imsim_run.py --clean
}

build(){
    bin/sip_safe_python.sh bin/ci_imsim_run.py --config-limit-deblend -j $NJOBS
}
