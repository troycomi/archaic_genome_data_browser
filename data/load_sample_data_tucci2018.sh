#!/usr/bin/env bash

set -e

flask load-data data-source data/tucci-20180915/tucci2018_data_source.yml

flask load-data superpopulations data/tucci-20180915/geographic_regions.tsv "Tucci (Unpublished, 2018)"

flask load-data populations data/tucci-20180915/populations.tsv "Tucci (Unpublished, 2018)"

flask load-data samples data/tucci-20180915/samples.tsv "Tucci (Unpublished, 2018)"
