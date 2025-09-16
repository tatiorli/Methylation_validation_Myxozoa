import pandas as pd
from pathlib import Path
from Bio import SeqIO

# Paths
excel_file = "Final_presence_absence_with_acessions_v2.xlsx"
proteomes_dir = Path("all_proteomes")

# Load data, skip first row (descriptive)
df = pd.read_excel(excel_file, sheet_name="Sheet1", skiprows=1)

# Go through each HMM column (skip the first column with proteome names)
for hmm in df.columns[1:]:
    print(f"Processing {hmm}...")
    
    # Collect all protein IDs for this HMM
    protein_ids = (
        df[hmm]
        .dropna()
        .loc[lambda x: x != "no"]
        .apply(lambda s: s.split("|")[0])
        .unique()
    )
    
    if len(protein_ids) == 0:
        print(f"  No hits for {hmm}, skipping.")
        continue
    
    # Output file for this HMM
    output_file = f"{hmm}_selected_proteins.fasta"
    
    with open(output_file, "w") as out_f:
        # Go through all proteome files
        for fasta_file in proteomes_dir.glob("*"):
            if fasta_file.suffix.lower() not in [".faa", ".fasta", ".fa"]:
                continue
            
            for record in SeqIO.parse(fasta_file, "fasta"):
                if record.id in protein_ids:
                    SeqIO.write(record, out_f, "fasta")
    
    print(f"  Saved {output_file} with {len(protein_ids)} protein IDs.")
