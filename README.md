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

## 🔹 Script 1: `generate_hmm_tabular_all_proteomes_loop.sh`

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
# Prepare inputs
mkdir all_hmms all_proteomes
cp *.hmm all_hmms/
cp *.fasta all_proteomes/

# Run script
bash generate_hmm_tabular_all_proteomes_loop.sh
