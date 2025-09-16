#!/bin/bash
# This script will join all the hmmsearch tables per hmm (for multiple proteomes) into one master table, with Hit_status, and creates one table per hmm as well in the process
# Output master table
MASTER_TABLE="results_v2.tsv"
echo -e "Sample\tSequence_ID\tE-value\tScore\tBias\tHit_status\tHMM_used" > "$MASTER_TABLE"

# List of subdirectories (HMM directories)
SUBDIRECTORIES=(*/)

for dir in "${SUBDIRECTORIES[@]}"; do
    FOLDER_NAME=$(basename "$dir" /)  # Folder name corresponds to the HMM used
    HMM_TABLE="${FOLDER_NAME}_hmmsearch_results.tsv"
    
    # Initialize the individual HMM table for this HMM
    echo -e "Sample\tSequence_ID\tE-value\tScore\tBias\tHit_status\tHMM_used" > "$HMM_TABLE"

    # Find all *_tabular.txt files inside the folder
    TBL_FILES=($(find "$dir" -maxdepth 1 -name "*_tabular.txt"))

    if [ ${#TBL_FILES[@]} -eq 0 ]; then
        echo "No *_tabular.txt files found in $dir"
        continue
    fi

    for tbl in "${TBL_FILES[@]}"; do
        # Extract the sample name (organism part) by stripping the prefix and suffix
        SAMPLE=$(basename "$tbl" "_tabular.txt" | sed -E 's/^PTHR[0-9]+_SF[0-9]+_x_([A-Za-z0-9_]+)_metaeuk$/\1/')

        # Check if tabular file has any non-comment lines
        HITS=$(grep -v "^#" "$tbl" | wc -l)

        if [ "$HITS" -eq 0 ]; then
            # No hits found, write a NoHit entry
            echo -e "${SAMPLE}\tNA\tNA\tNA\tNA\tNoHit\t${FOLDER_NAME}" >> "$MASTER_TABLE"
            echo -e "${SAMPLE}\tNA\tNA\tNA\tNA\tNoHit\t${FOLDER_NAME}" >> "$HMM_TABLE"
        else
            # Hits found, process each hit
            grep -v "^#" "$tbl" | awk -v sample="$SAMPLE" -v hmm="$FOLDER_NAME" '{
                gsub(/[[:space:]]+/, " ");
                split($0, fields, " ");
                seq_id = fields[1];
                evalue = fields[5];
                score = fields[6];
                bias = fields[7];
                print sample "\t" seq_id "\t" evalue "\t" score "\t" bias "\t" "Hit" "\t" hmm;
            }' >> "$MASTER_TABLE"
            grep -v "^#" "$tbl" | awk -v sample="$SAMPLE" -v hmm="$FOLDER_NAME" '{
                gsub(/[[:space:]]+/, " ");
                split($0, fields, " ");
                seq_id = fields[1];
                evalue = fields[5];
                score = fields[6];
                bias = fields[7];
                print sample "\t" seq_id "\t" evalue "\t" score "\t" bias "\t" "Hit" "\t" hmm;
            }' >> "$HMM_TABLE"
        fi
    done

    echo "Done with $HMM_TABLE"
done

echo "Done. Master table created at: $MASTER_TABLE"
