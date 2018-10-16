#!/usr/bin/env bash

set -e

flask load-data analysis-runs "data/analysis_runs/analysis_runs.tsv" "Tucci (Unpublished, 2018)"

# flask load-data archaic-genome-data "data/analysis_runs/ALL.amount.n.d.ambig.null.per_ind_Nov9.txt" "tucci_20180915"

