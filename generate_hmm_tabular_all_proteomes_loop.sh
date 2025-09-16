#!/bin/bash
ml HMMER/3.3.2-gompi-2022b
# Run all HMMs against all proteomes, in a loop per HMM, using hmmsearch and making output format both long and tabular for further downstream parsing.

# Define input and output directories
HMM_DIR="all_hmms" # This dir holds all the HMMs files ending with .hmm
PROTEOME_DIR="all_proteomes" # This dir holds all the proteomes in .fasta format
RESULTS_DIR="results_hmmsearch" # To save the results organized by folder per each hmm

# Create the main results directory
mkdir -p "$RESULTS_DIR"

# Loop over each HMM file in all_hmms
for hmm_file in "$HMM_DIR"/*.hmm; do
    # Extract base name without extension
    hmm_base=$(basename "$hmm_file" .hmm)

    # Create a subdirectory for this HMM inside results/
    hmm_result_dir="${RESULTS_DIR}/${hmm_base}"
    mkdir -p "$hmm_result_dir"

    echo "Processing HMM: $hmm_file -> results in $hmm_result_dir/"

    # Loop over each proteome file in all_proteomes
    for prot_file in "$PROTEOME_DIR"/*.fasta; do
        prot_base=$(basename "$prot_file" .fasta)

        # Define output paths
        output_normal="${hmm_result_dir}/${hmm_base}_x_${prot_base}.txt"
        output_tabular="${hmm_result_dir}/${hmm_base}_x_${prot_base}_tabular.txt"

        echo "  Running hmmsearch for $prot_file"
        hmmsearch -o "$output_normal" "$hmm_file" "$prot_file"
        hmmsearch --tblout "$output_tabular" "$hmm_file" "$prot_file"
    done
done
