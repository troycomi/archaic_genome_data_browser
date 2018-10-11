#!/usr/bin/env bash

set -e

flask load_data analysis_runs "data/analysis_runs/analysis_runs.tsv" "Tucci (Unpublished, 2018)"

# flask load_data archaic_genome_data "data/analysis_runs/ALL.amount.n.d.ambig.null.per_ind_Nov9.txt" "tucci_20180915"

