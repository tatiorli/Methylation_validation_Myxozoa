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

# Mapping sample names to final row names -- This is important so the correct name will be matched to the correct proteome
# Duplicates: we have two proteomes that have both a metaeuk de novo proteome and a published reference proteome - M honghuensis and T kitauei
print("Mapping sample names to final row names...")
sample_to_final_row = {
    'Ceratonova_shasta_metaeuk': 'Ceratonova_shasta',
    'Enteromyxium_leei_metaeuk': 'Enteromyxium_leei',
    'Henneguya_salminicola_metaeuk': 'Henneguya_salminicola',
    'Kudoa_iwatai_metaeuk': 'Kudoa_iwatai',
    'Myxobolus_honghuensis_metaeuk': 'Myxobolus_honghuensis_m',
    'Myxobolus_squamalis_metaeuk': 'Myxobolus_squamalis',
    'sample_57_metaeuk': 'sample_57',
    'sample_58_metaeuk': 'sample_58',
    'sample_108_metaeuk': 'sample_108',
    'sample_115_metaeuk': 'sample_115',
    'sample_70_metaeuk': 'sample_70',
    'Sphaeromyxa_zaharoni_metaeuk': 'Sphaeromyxa_zaharoni',
    'Thelohanellus_kitauei_metaeuk': 'Thelohanellus_kitauei_m',

    'Kudoa_neothunni_proteome_GCA_964304625': 'Kudoa_neothunni',
    'Kudoa_trachurus_proteome_GCA_964275015': 'Kudoa_trachurus',
    'Myxobolus_honghuensis_proteome': 'Myxobolus_honghuensis_p',
    'Myxobolus_rasmusseni_proteome': 'Myxobolus_rasmusseni',
    'Thelohanellus_kitauei_proteome_GCA_000827895': 'Thelohanellus_kitauei_p',

    'Human_proteome_GCA_000001405.29': 'Human',
    'Nematostella_vectensis_proteome_GCA_932526225.1': 'Nematostella_vectensis',

    'Aedes_aegypti_proteome_GCF_002204515.2': 'Aedes_aegypti',
    'Caenorhabditis_elegans_proteome_GCA_000002985.3': 'Caenorhabditis_elegans',
    'Chrysodeixis_includens_proteome_GCA_903961255.1': 'Chrysodeixis_includens',
    'Drosophila_melanogaster_proteome_GCA_000001215.4': 'Drosophila_melanogaster',
    'Schistosoma_mansoni_proteome_GCA_000237925.2': 'Schistosoma_mansoni',
    'Schmidtea_mediterranea_proteome': 'Schmidtea_mediterranea',
}
print("Mapping complete.")

# Map sample names in results
results['Final_Row'] = results['Sample'].map(sample_to_final_row)

# Check how many samples were successfully mapped
unmapped = results[results['Final_Row'].isna()]
print(f"Total samples: {len(results)}")
print(f"Mapped samples: {len(results.dropna(subset=['Final_Row']))}")
if not unmapped.empty:
    print("Warning: Some samples could not be mapped:")
    print(unmapped['Sample'].unique())

# Reduce to best hits: lowest e-value per (Final_Row, HMM_used)
print("Selecting best hits based on lowest e-value...")
best_hits = results.sort_values('E-value').groupby(['Final_Row', 'HMM_used'], as_index=False).first()

# Create a dictionary for quick lookup: (species, protein) -> Sequence_ID
hit_dict = {(row['Final_Row'], row['HMM_used']): row['Sequence_ID'] for _, row in best_hits.iterrows()}
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
