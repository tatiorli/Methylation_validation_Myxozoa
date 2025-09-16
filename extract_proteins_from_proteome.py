from Bio import SeqIO
# This script extracts proteins of interest from a large proteome file, based on a list of headers and create a new fasta file that has the sequences
# Input files
fasta_file = "Thelohanellus_kitauei_proteome_GCA_000827895.fasta"
headers_file = "proteins_Thelohanellus_kitauei_proteome.txt"
output_file = "proteins_Thelohanellus_kitauei_proteome.fasta"

# Load headers
with open(headers_file) as f:
    wanted_ids = set(line.strip() for line in f if line.strip())

# Extract matching records
with open(fasta_file) as fasta, open(output_file, "w") as out:
    for record in SeqIO.parse(fasta, "fasta"):
        header_prefix = record.id  # id is the part before the first whitespace
        if any(header_prefix.startswith(wanted) for wanted in wanted_ids):
            SeqIO.write(record, out, "fasta")
