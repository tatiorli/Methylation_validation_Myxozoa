# Myxozoa Methylation validation project
This repository contains accessory scripts for generating the `hmmsearch` analyses used in the article (insert citation).

_This is a response to: [Long-read metagenomic sequencing negates inferred loss of cytosine methylation in Myxosporea (Cnidaria: Myxozoa)](https://academic.oup.com/gigascience/article/doi/10.1093/gigascience/giaf014/8075032)_  

---

## 🔹 Motivation

The study by **Long et al. (2024)** suggested that DNA methylation was present in some myxozoan genomes newly assembled using Oxford Nanopore (ONT) sequencing. Specifically:
- Specimens **57 and 58** were reported to have large numbers of methylated genes.  
- Their inference was based on:
  1. ONT methylation calls (Figure 6)  
  2. Presence of DNA methylation proteins (Table 3)  
  3. Skew in CpG O/E (Table 4, Figure 8B)  

These findings contrast with our previously published results ([Kyger et al. 2021](https://academic.oup.com/mbe/article/38/2/393/5902833)), where we proposed the absence of DNA methylation in myxozoa, based on:
1. Lack of DNA methylation enzymes in myxozoa (Figure 1)  
2. Lack of methylated Cs from WGBS (Table 1, Figures 2 and 3)  

The scripts here were developed to **systematically search for DNA methylation–related proteins across myxozoan proteomes using HMMER**, as part of the methodological response.

---

## 🔹 First step is to run script: `generate_hmm_tabular_all_proteomes_loop.sh`

### Purpose
Run **all HMMs selected against all proteomes selected** using `hmmsearch`.  
Each HMM is compared to each proteome, producing both:
- A **full alignment report** (`.txt`)
- A **tabular summary** (`_tabular.txt`)

This allows downstream parsing and identification of candidate DNA methylation–related proteins.

---

### Logic
1. **Load HMMER module**  
   Ensures the correct version (`HMMER/3.3.2`) is available.

2. **Set input and output directories**
   - `all_hmms/` → directory containing `.hmm` files (one per domain/protein model).  
   - `all_proteomes/` → directory containing proteomes in `.fasta` format.  
   - `results_hmmsearch/` → main results folder.

3. **Loop over each HMM file**
   - Extracts the base name of the HMM (e.g. `DNMT1.hmm` → `DNMT1`).  
   - Creates a dedicated results subfolder (e.g. `results_hmmsearch/DNMT1/`).

4. **Loop over each proteome file**
   - Extracts the base name of the proteome (e.g. `sample57.fasta` → `sample57`).  
   - Defines output file names:
     - Long format report: `DNMT1_x_sample57.txt`  (useful in case of manual verification of the alignment)
     - Tabular format report: `DNMT1_x_sample57_tabular.txt`  (for downstream parsing needs)

5. **Run hmmsearch twice per proteome**
   - Standard output (`-o`) for detailed alignments.  
   - Tabular output (`--tblout`) for structured downstream analysis.

---

### Example Workflow

```bash
# Prepare inputs folders to match the script structure
mkdir all_hmms all_proteomes
cp *.hmm all_hmms/
cp *.fasta all_proteomes/

# Run script
bash generate_hmm_tabular_all_proteomes_loop.sh
```
## 🔹 Second step is to run script: `generate_table_of_hmmsearch_results_combined.sh`

### Purpose
After running `hmmsearch` (see 1st step script), each HMM × proteome comparison produces its own **tabular file** output (results).  
This script consolidates those results into:
1. A **master results table** (`results_v2.tsv`) containing all hits across all HMMs and proteomes.  
2. An **individual results table per HMM**, combining its hits across all proteomes for that HMM only (intermediate step for the mater table).

---

### Logic
1. **Initialize master table**
   - Creates `results_v2.tsv` with header:  
     ```
     Sample   Sequence_ID   E-value   Score   Bias   Hit_status   HMM_used
     ```

2. **Iterate through all HMM directories**
   - Each subdirectory corresponds to a single HMM (e.g. `DNMT1/`).  
   - For each HMM, create an individual output file (e.g. `DNMT1_hmmsearch_results.tsv`).

3. **Find tabular hmmsearch outputs**
   - Detects all `*_tabular.txt` files inside the HMM folder.  
   - If none exist → skip with a warning.

4. **Extract sample name**
   - From file names like:  
     ```
     PTHR####_SF##_x_SampleName_metaeuk_tabular.txt
     ```
   - Uses `sed` regex to capture just the **SampleName**.

5. **Check for hits**
   - If the tabular file has **no hits** (only comments), append a row with:
     ```
     Sample   NA   NA   NA   NA   NoHit   HMM
     ```
   - If hits exist, parse them using `awk`.

6. **Process hits with awk**
   - For each line (ignoring `#` comments):
     - Extract:
       - `Sequence_ID` = first column  
       - `E-value` = 5th column  
       - `Score` = 6th column  
       - `Bias` = 7th column  
     - Append to both the **master table** and the **HMM-specific table**, marking `Hit_status = Hit`.

7. **Completion message**
   - Prints progress updates (`Done with DNMT1_hmmsearch_results.tsv`).  
   - At the end:  
     ```
     Done. Master table created at: results_v2.tsv
     ```

---

### Example Workflow

```bash
# Run from results_hmmsearch/ after Script 1
bash generate_table_of_hmmsearch_results_combined.sh
```
---

## 🔹 Third step is script: `generate_final_absence_presence_table.py` (there are some variations of it)

### Purpose
This script creates the **final presence/absence matrix** across all proteomes and HMMs.  
- If a **hit** is found → reports the **protein accession (Sequence_ID)**.  
- If **no hit** is found → reports `"no"`.  
- If **multiple hits** are found for the same proteome/HMM → keeps the **best hit (lowest E-value)**.  

This table is the **main summary output** of the analysis.

---

### Logic
1. **Input files**
   - `results.xlsx` → consolidated results table from Script 2 (all HMMs × all proteomes).  
   - `Final table of presence absence.xlsx` → an **empty template** with rows = proteomes, columns = HMMs, in the desired reporting order.  
   - Output: `Final_presence_absence_with_acessions.xlsx`.

2. **Load results**
   - Import both the results and the template using **pandas**.  

3. **Select best hits per (Sample, HMM)**
   - Sort by E-value.  
   - Use `groupby(['Sample', 'HMM_used']).first()` to keep only the lowest E-value hit for each pair.  

4. **Build lookup dictionary**
   - Create a mapping:
     ```
     (Sample, HMM_used) → Sequence_ID
     ```
   - This allows constant-time retrieval of the best protein accession for each cell.

5. **Fill presence/absence matrix**
   - Iterate through each proteome (row) and HMM (column) in the template.  
   - If a hit exists → insert the `Sequence_ID`.  
   - If no hit exists → insert `"no"`.  
   - Maintains the **same order** of proteomes and HMMs as defined in the input template.

6. **Save final table**
   - Export to Excel: `Final_presence_absence_with_acessions_v2.xlsx`.

---

### Example Workflow

```bash
# Run the Python script
python generate_final_absence_presence_table.py
```
---

## 🔹  Fourth step is script: `extract_proteins_from_proteome.py`

### Purpose
This script extracts the **protein sequences** corresponding to the best hits reported in the **final presence/absence matrix** (from step 3).  
For each HMM, it collects all protein accessions across proteomes, retrieves them from the proteome FASTA files, and writes them into a **multi-FASTA file per HMM**.  

These FASTA files can then be used for **phylogenetic tree construction**.

---

### Logic
1. **Input files**
   - `Final_presence_absence_with_acessions_v2.xlsx` → final matrix with protein IDs or `"no"`.  
   - `all_proteomes/` → directory containing proteome FASTA files (`.faa`, `.fasta`, `.fa`).  

2. **Read Excel matrix**
   - Skip the first row (descriptive header).  
   - Iterate through each HMM column (excluding the first column with sample names).

3. **Collect protein IDs for each HMM**
   - Ignore `"no"` entries.  
   - Extract only the **protein accession** (before any `|` separator).  
   - Ensure uniqueness.

4. **Extract sequences**
   - For each HMM:
     - Open/create an output FASTA file:  
       ```
       HMM_selected_proteins.fasta
       ```
     - Search through every proteome file in `all_proteomes/`.  
     - Parse with `Biopython`’s `SeqIO`.  


---

## 🔹 Extra Step: `extract_evalues.py`

### Purpose
This script augments the **final presence/absence matrix** by filling in the **lower E-values** corresponding to each protein hit in an extra column.  
Originally, the pipeline only tracked whether a protein ID was present (`Sequence_ID` or `"no"`). This step ensures that the statistical significance of the hit (E-value from HMMER) is also recorded alongside.

### Input files
- **`Final_presence_absence.csv`**  
  The manually curated presence/absence matrix with protein IDs. Some columns are for protein IDs, and added adjacent ones, which are empty `E-value` columns to be filled.
- **`All_results.xlsx`**  
  Complete hmmsearch results for all proteomes and HMMs, including `Sample`, `HMM_used`, `Sequence_ID`, and `E-value`.

### Main logic
1. **Load data**  
   - Reads both the matrix and the full results table.
2. **Normalize identifiers**  
   - Handles variations in sequence IDs (UniProt style, metaeuk contigs, versions like `.1`, `.2`, etc.).
   - Makes HMM names consistent by normalizing to lowercase and underscores.
3. **Build lookup dictionary**  
   - Maps `(Sequence_ID token, HMM)` → list of E-values.
   - Ensures fast access when filling the matrix.
4. **Match IDs and assign best E-values**  
   - For each non-`"no"` protein ID in the matrix, searches for candidate E-values.
   - Picks the lowest (best) E-value if multiple are found.
   - Fills the E-value column next to the protein ID.
5. **Track unmatched cases**  
   - Any sequence–HMM combination not found in the lookup is logged separately.
6. **Save outputs**  
   - `updated_matrix_with_evalues.csv` → full updated matrix with E-values filled.  
   - `unmatched_seq_hmm.csv` → list of unmatched protein IDs + HMMs, useful for debugging.

### Output files
- **Updated matrix with filled E-values**  
- **Unmatched sequence/HMM report** for troubleshooting

### Example command
```bash
python extract_evalues.py
```
