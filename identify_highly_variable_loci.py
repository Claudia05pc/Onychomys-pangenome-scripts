import subprocess
import sys

def process_bed_file(input_file, output_file, percentage_change):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    output_lines = []

    for i in range(len(lines) - 1):
        current_line = lines[i].strip().split()
        next_line = lines[i + 1].strip().split()

        try:
            # Convert 4th column values to float (handles both integers & decimals)
            current_value = float(current_line[3])
            next_value = float(next_line[3])
        except (ValueError, IndexError):
            # Skip lines with invalid or missing values
            continue

        # Check if the change is at least the specified percentage
        if abs(current_value - next_value) >= (percentage_change / 100) * min(current_value, next_value):
            output_lines.append("\t".join(current_line))  # Add the first line to the output list

    # Write the processed lines to the output file
    with open(output_file, 'w') as f:
        for line in output_lines:
            f.write(line + "\n")

# Get the percentage of change from the user (default to 50% if not provided)
try:
    percentage_change = float(sys.argv[1])  # Get percentage change from command-line arguments
except IndexError:
    percentage_change = 50.0  # Default to 50% if not provided

# Define file names based on the percentage change
filtered_file = f"filtered_locus_{int(percentage_change)}_change.bed"
corrected_file = f"corrected_locus_{int(percentage_change)}_change.bed"
coordinates_file = f"locus_{int(percentage_change)}_coordinates.bed"
mapped_file = f"mapped_locus_variants_{int(percentage_change)}_change.bed"
sorted_file = f"sorted_locus_variant_output_{int(percentage_change)}_change.bed"
top_5_percent_file = f"top_5_percent_locus_variant_output_{int(percentage_change)}_change.bed"
sorted_5_file = f"var_no_sequence_sorted_{int(percentage_change)}_5_windows_coordinates_200k_locus.bed"
intersected_file = f"intersected_most_variable_regions_{int(percentage_change)}_windows_200k_locus.bed"

# Run the function on windowed_divergence.bed and create filtered_locus_200k.bed as output
process_bed_file("windowed_divergence.bed", filtered_file, percentage_change)


def fix_bed_file(input_file, output_file):
    with open(input_file, 'r') as f:
        lines = [line.strip().split() for line in f.readlines()]

    # Process lines and fix the second column
    for i in range(len(lines)):
        if i == 0 or lines[i][0] != lines[i-1][0]:
            # First line or when chromosome changes → Set second column to 0
            lines[i][1] = "0"
        else:
            # Otherwise, second column = (previous line's third column) + 1000
            lines[i][1] = str(int(lines[i-1][2]) + 1000)

    # Write the corrected file
    with open(output_file, 'w') as f:
        for line in lines:
            f.write("\t".join(line) + "\n")

# Fix the filtered file and create the corrected file
fix_bed_file(filtered_file, corrected_file)


# Run the Bash commands after processing the BED files
def run_bash_commands():
    # Run the 'cut' command to extract columns 1-3 and save it to locus_200k_coordinates.bed
    subprocess.run(f"cut -f1-3 {corrected_file} > {coordinates_file}", shell=True)

    # Run the 'bedtools map' command to map locus_200k_coordinates.bed with minigraph_variants.bed
    subprocess.run(f"bedtools map -a {coordinates_file} -b minigraph_variants.bed -c 8 -o sum > {mapped_file}", shell=True)

    # Run the 'sort' command to sort the output based on the 4th column in descending order
    subprocess.run(f"sort -k4,4nr {mapped_file} > {sorted_file}", shell=True)

    # Keep only the top 5% of the lines from sorted_locus_variant_output.bed
    subprocess.run(f"head -n $(($(wc -l < {sorted_file}) / 20)) {sorted_file} > {top_5_percent_file}", shell=True)

    # Run the 'awk' command to process the file and add chromosome prefix to match the annotation file (OncTor#chr in our case), then sort it
    subprocess.run(f"awk -F'\t' '{{print \"OncTor#chr\"$1, $2, $3}}' OFS='\t' {top_5_percent_file} | sort -k1,1 -k2,2n > {sorted_5_file}", shell=True)

    # Run the 'bedtools intersect' command to find intersecting regions
    subprocess.run(f"bedtools intersect -a gene_annotation.bed -b {sorted_5_file} -f 1 > {intersected_file}", shell=True)

# Call the function to run all the bash commands
run_bash_commands()

