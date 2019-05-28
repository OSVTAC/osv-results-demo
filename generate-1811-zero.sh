# Generate "zero reports" for the Nov. 2018 election.
set -x

ORR_PATH=submodules/osv-results-reporter


orr -v --input-dir submodules/osv-sample-data/2018-11-06/out-orr/ \
    --input-results-dir "submodules/osv-sample-data/2018-11-06/out-orr/resultdata-zero/" \
    --template-dir "${ORR_PATH}/templates/test-minimal" \
    --extra-template-dirs "${ORR_PATH}/templates/test-minimal/extra" \
    --output-parent docs --output-subdir 2018-11-06-zero
