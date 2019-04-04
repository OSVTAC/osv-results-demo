set -x

ORR_PATH=submodules/osv-results-reporter


orr -v --input-dir "submodules/osv-sample-data/2018-06-05/out-orr/" \
    --extra "${ORR_PATH}/templates/test-minimal/extra" \
    --template "${ORR_PATH}/templates/test-minimal" \
    --output-parent docs --output-dir 2018-06-05
