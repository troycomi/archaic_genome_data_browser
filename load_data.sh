#!/usr/bin/env bash

flask db upgrade

./data/load_sample_data_1000genomes.sh

./data/load_sample_data_tucci2018.sh

./data/load_analysis_run_tucci_20180915.sh