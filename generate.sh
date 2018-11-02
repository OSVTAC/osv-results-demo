set -x

ORR_PATH=submodules/osv-results-reporter

orr -v --input "${ORR_PATH}/sampledata/test-minimal" \
    --extra "${ORR_PATH}/templates/test-minimal/extra" \
    --template "${ORR_PATH}/templates/test-minimal" \
    --output-parent docs --output-dir minimal-test
