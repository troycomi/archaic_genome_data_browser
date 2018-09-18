#!/usr/bin/env bash

set -e

flask load_data data_source data/1000genomes/1000genomes_data_source.yml

flask load_data superpopulations data/1000genomes/superpopulations.tsv "1000 Genomes Project"

flask load_data populations data/1000genomes/populations.tsv "1000 Genomes Project"

flask load_data samples data/1000genomes/20130606_sample_info.txt "1000 Genomes Project"