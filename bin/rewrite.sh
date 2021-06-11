# need to manually copy and update the python path
echo "#!$(command -v python)" > bin/ci_imsim_run.py
cat bin.src/ci_imsim_run.py >> bin/ci_imsim_run.py

# verify that the file is executable
chmod ug+x bin/ci_imsim_run.py

