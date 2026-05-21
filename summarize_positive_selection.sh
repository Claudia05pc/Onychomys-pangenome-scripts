#!/bin/bash

# Define the input files
alignment_file_list="positive_selection_alignment_files.txt"
codeml_output_list="positive_selection_codeml_output_files.txt"

# Temporary files
alignment_length_file="alignment_lengths.txt"
beb_sites_file="beb_positive_selection_sites.txt"
positive_selection_summary_file="positive_selection_summary.txt"

# Step 1: Process FASTA files to compute sequence lengths
while IFS= read -r fasta_file; do
    if [ -f "$fasta_file" ]; then
        first_sequence=$(awk '/^>/ {if (seq) exit} {if (!/^>/) seq=seq$0} END {print seq}' "$fasta_file")
        sequence_length=${#first_sequence}
        result=$((sequence_length / 3))
        echo -e "${fasta_file}\t${result}"
    else
        echo -e "${fasta_file}\tFile not found"
    fi
done < "$alignment_file_list" > "$alignment_length_file"

sed -i 's/.pal2nal//' "$alignment_length_file"

# Step 2: Process .alt.out files for specific matches
while IFS= read -r filename; do
    if [ -f "$filename" ]; then
        matches=$(grep -A 20 "(BEB)" "$filename" | grep "*" | awk '{printf "%s\t", $0}')
        if [ -n "$matches" ]; then
            echo -e "${filename}\t${matches}"
        else
            echo -e "${filename}\tNo matches found"
        fi
    else
        echo -e "${filename}\tFile not found"
    fi
done < "$codeml_output_list" > "$beb_sites_file"

sed -i 's/.alt.out//' "$beb_sites_file"
sed -i -e 's/\*\s\+/*\t/g' -e 's/\.1\s\+/\.1\t/g' "$beb_sites_file"

# Step 3: Process files with Python to combine results
python3 <<EOF
import sys

def read_file(file_path):
    data = {}
    try:
        with open(file_path, 'r') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) == 2:
                    data[parts[0]] = parts[1]
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
    return data

def write_file(file_path, data):
    try:
        with open(file_path, 'w') as f:
            for key, value in data.items():
                f.write(f"{key}\t{value}\n")
    except Exception as e:
        print(f"Error writing {file_path}: {e}", file=sys.stderr)

def merge_positive_selection_results(length_file, beb_sites_file, output_file):
    alignment_lengths = read_file(length_file)
    positive_selection_sites = {}

    try:
        with open(beb_sites_file, 'r') as f:
            for line in f:
                parts = line.strip().split('\t', 1)
                if len(parts) == 2:
                    file_name, matches = parts
                    length_info = alignment_lengths.get(file_name, 'Length not found')
                    positive_selection_sites[file_name] = f"{length_info}\t{matches}"
    except Exception as e:
        print(f"Error reading {beb_sites_file}: {e}", file=sys.stderr)

    write_file(output_file, positive_selection_sites)

# Run the merge operation
merge_positive_selection_results('$alignment_length_file', '$beb_sites_file', '$positive_selection_summary_file')
EOF

echo "Processing complete. Results saved in $positive_selection_summary_file."