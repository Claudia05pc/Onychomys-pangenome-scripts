# *Onychomys* pangenome analysis scripts

Custom scripts used for analyses in:

**Perez-Calles et al.**  
*The Onychomys pangenome reveals the unique molecular adaptations that confer toxin resistance.*

Preprint DOI: https://doi.org/10.1101/2025.10.28.685014

## Repository contents

### `identify_highly_variable_loci.py`

Identifies candidate highly variable loci by comparing sequence divergence between consecutive genomic windows. Sequence divergence is then mapped to identified loci, loci are ranked by divergence magnitude, the top 5% most variable regions are retained, and overlapping genes are extracted using genome annotations.

#### Required input files

- `windowed_divergence.bed`: BED file of genome-wide sliding windows (200 kb windows, 1 kb step) containing sequence-divergence values in column 4.

- `minigraph_variants.bed`: Minigraph-derived BED file containing variation information, where column 8 corresponds to the length of the largest variation bubble (sequence divergence metric).

- `gene_annotation.bed`: BED-format genome annotation file used to identify genes fully overlapping highly variable regions.

**Note:** chromosome names in the annotation file must match the prefix used in the script (`OncTor#chr` in our case).

#### Requirements

- Python 3
- bedtools v2.30.0+
- Unix command-line tools:
  - `cut`
  - `sort`
  - `head`
  - `wc`
  - `awk`

#### Usage

Default threshold (50%):

```bash
python identify_highly_variable_loci.py
```

Custom threshold (example: 50%):

```bash
python identify_highly_variable_loci.py 50
```

#### Output

The final output file contains annotated genes fully overlapping highly variable regions:

```txt
intersected_most_variable_regions_<threshold>_windows_200k_locus.bed
```
---

### `summarize_positive_selection.sh`

Generates a summary table of candidate genes under positive selection, alignment lengths, and positively selected amino acid sites identified by Bayes Empirical Bayes (BEB) analysis (posterior probability >0.95).

The script:

1. Calculates alignment lengths from PAL2NAL FASTA alignments.
2. Extracts positively selected amino acid sites from CODEML files by parsing BEB results.
3. Merges sequence lengths and BEB output into a final summary table.

#### Required input files

- `positive_selection_alignment_files.txt`: text file containing paths to PAL2NAL FASTA alignment files (one per line).

- `positive_selection_codeml_output_files.txt`: text file containing paths to CODEML output files (one per line).

#### Requirements

- Bash
- Python 3
- Unix command-line tools:
  - `awk`
  - `grep`
  - `sed`

#### Usage

```bash
bash summarize_positive_selection.sh
```

#### Output

Final summary table:

```txt
positive_selection_summary.txt
```

This file contains:

- gene name
- alignment length
- positively selected amino acid positions
- BEB posterior probabilities (>0.95)
  
## Citation

If using these scripts, please cite:

Pérez-Calles et al. *The Onychomys pangenome reveals the unique molecular adaptations that confer toxin resistance.*

DOI: https://doi.org/10.1101/2025.10.28.685014
