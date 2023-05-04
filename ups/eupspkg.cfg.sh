prep(){
    bin/rewrite.sh
}

config(){
    # verify that the working directory is clean
    $CI_BUILDER_DIR/bin/sip_safe_python.sh bin/ci_imsim_run.py --clean
}

build(){
    $CI_BUILDER_DIR/bin/sip_safe_python.sh bin/ci_imsim_run.py -j $NJOBS
}

install() {
    clean_old_install
    install_ups
}
