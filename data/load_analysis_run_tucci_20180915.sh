#!/usr/bin/env bash

set -e

flask load-data analysis-runs "data/analysis_runs/analysis_runs.tsv" "Tucci (Unpublished, 2018)"

flask load-data archaic-genome-data tucci_20180915

flask load-data generate-merged-haplotype tucci_20180915
