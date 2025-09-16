import pandas as pd
# This script generates a final table where it reports:
# Per proteome, per HMM used, if hit prints the protein ID, if no hit, print "no". 
# For hmm with multiple positive hits, it captures the one with lower e-value of the list.

# File paths
results_path = "results_v2.xlsx" # Table in tabular format that holds all hmmsearch results together for all hmms and all proteomes
final_table_path = "Final table of presence absence v2.xlsx" # Final table with the desired format, order of proteomes to list and hmms columns that needs to be maintained for the final order of reporting results.
output_path = "Final_presence_absence_with_acessions_v2.xlsx" # Final output that has the same rows and colums as the previous empty table but now filled.

print("Loading input files...")
# Load data
results = pd.read_excel(results_path)
presence_absence = pd.read_excel(final_table_path, index_col=0)
print("Files loaded successfully.")

# Reduce to best hits: lowest e-value per (Sample, HMM_used)
print("Selecting best hits based on lowest e-value...")
best_hits = results.sort_values('E-value').groupby(['Sample', 'HMM_used'], as_index=False).first()

# Create a dictionary for quick lookup: (species, protein) -> Sequence_ID
hit_dict = {(row['Sample'], row['HMM_used']): row['Sequence_ID'] for _, row in best_hits.iterrows()}
print(f"Total unique best hits: {len(hit_dict)}")

# Fill in the presence/absence table with Sequence_IDs
print("Filling in presence/absence table...")
species_total = len(presence_absence.index)
for i, species in enumerate(presence_absence.index, start=1):
    if i % 10 == 0 or i == species_total:
        print(f"Processing species {i} of {species_total}: {species}")
    for protein in presence_absence.columns:
        key = (species, protein)
        presence_absence.loc[species, protein] = hit_dict.get(key, "no")

# Save the filled table
print("Saving output file...")
presence_absence.to_excel(output_path)
print(f"Done! Filled table saved to: {output_path}")
