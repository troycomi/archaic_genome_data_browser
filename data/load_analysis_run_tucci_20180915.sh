#!/usr/bin/env bash

set -e

flask load-data analysis-runs "data/analysis_runs/analysis_runs.tsv" "Tucci (Unpublished, 2018)"

flask load_data archaic_genome_data tucci_20180915

flask load_data generate_merged_haplotype tucci_20180915
