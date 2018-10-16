#!/usr/bin/env bash

set -e

flask load-data data-source data/tucci2018/tucci2018_data_source.yml

flask load-data superpopulations data/tucci2018/geographic_regions.tsv "Tucci (Unpublished, 2018)"

flask load-data populations data/tucci2018/populations.tsv "Tucci (Unpublished, 2018)"

flask load-data samples data/tucci2018/samples.tsv "Tucci (Unpublished, 2018)"
