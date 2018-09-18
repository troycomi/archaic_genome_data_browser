#!/usr/bin/env bash

set -e

flask load_data data_source data/tucci2018/tucci2018_data_source.yml

flask load_data superpopulations data/tucci2018/geographic_regions.tsv "Tucci (Unpublished, 2018)"

flask load_data populations data/tucci2018/populations.tsv "Tucci (Unpublished, 2018)"

flask load_data samples data/tucci2018/samples.tsv "Tucci (Unpublished, 2018)"
