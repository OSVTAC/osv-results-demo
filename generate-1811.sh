set -x

ORR_PATH=submodules/osv-results-reporter


orr -v --input-dir submodules/osv-sample-data/2018-11-06/out-orr/ \
    --template-dir "${ORR_PATH}/templates/test-minimal" \
    --extra-template-dirs "${ORR_PATH}/templates/test-minimal/extra" \
    --output-parent docs --output-subdir 2018-11-06

# orr-docker --input-dir submodules/osv-sample-data/2018-11-06/out-orr/ \
#     --template-dir "${ORR_PATH}/templates/test-minimal" \
#     --extra-template-dirs "${ORR_PATH}/templates/test-minimal/extra" \
#     --output-parent docs --output-subdir 2018-11-06 \
#     --source-dir submodules/osv-results-reporter \
#     --orr -v
