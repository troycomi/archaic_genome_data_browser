#!/usr/bin/env bash

flask load_data superpopulations data/1000genomes/superpopulations.tsv

flask load_data populations data/1000genomes/populations.tsv

flask load_data samples data/1000genomes/20130606_sample_info.txt

flask load_data archaic_genome_data data/vernot2016/ALL.amount.n.d.ambig.null.per_ind_Nov9.txt Vernot2016
