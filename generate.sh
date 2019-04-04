set -x

ORR_PATH=submodules/osv-results-reporter

orr -v --input-dir "${ORR_PATH}/sampledata/test-minimal" \
    --extra "${ORR_PATH}/templates/test-minimal/extra" \
    --template "${ORR_PATH}/templates/test-minimal" \
    --output-parent docs --output-dir minimal-test

# TODO: uncomment this when it completes without errors.
#
# orr -v --input-dir "submodules/osv-sample-data/2018-11-06/out-orr/" \
#     --extra "${ORR_PATH}/templates/test-minimal/extra" \
#     --template "${ORR_PATH}/templates/test-minimal" \
#     --output-parent docs --output-dir 2018-11-06
