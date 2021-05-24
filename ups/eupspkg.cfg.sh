prep(){
    bin/rewrite.sh
}

config(){
    # verify that the working directory is clean
    bin/ci_imsim_run.py --clean
}

build(){
    bin/ci_imsim_run.py --config-limit-deblend -j $NJOBS
}
