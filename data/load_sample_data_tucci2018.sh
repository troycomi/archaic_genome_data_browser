#!/usr/bin/env bash

set -e

flask load_data data_source data/tucci-20180915/tucci2018_data_source.yml

flask load_data superpopulations data/tucci-20180915/geographic_regions.tsv "Tucci (Unpublished, 2018)"

flask load_data populations data/tucci-20180915/populations.tsv "Tucci (Unpublished, 2018)"

flask load_data samples data/tucci-20180915/samples.tsv "Tucci (Unpublished, 2018)"
