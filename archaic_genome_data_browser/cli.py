import csv
import click
import os
import yaml
from dateutil.parser import parse
from archaic_genome_data_browser import db
from archaic_genome_data_browser.models import (SuperPopulation, Population,
                                                Sample, ArchaicAnalysisRun,
                                                DataSource,
                                                DigitalObjectIdentifier,
                                                get_one_or_create)
from archaic_genome_data_browser.main import statistics


def register(app):
    @app.cli.group()
    def load_data():
        """Load data into the database."""
        pass

    @load_data.command()
    @click.argument('yml_filename')
    def data_source(yml_filename):
        """Import data_sources from yml file."""
        print("Importing data sources from '{}'".format(yml_filename))
        with open(yml_filename) as yml_file:
            data_sources_yaml = yaml.load(yml_file)
            for data_source_yaml in data_sources_yaml['data_sources']:
                data_source = DataSource(
                    name=data_source_yaml['name'],
                    description=data_source_yaml['description'])
                db.session.add(data_source)
                if data_source_yaml['dois']:
                    for doi_yaml in data_source_yaml['dois']:
                        doi = DigitalObjectIdentifier(name=doi_yaml['name'],
                                                      doi=doi_yaml['doi'])
                        data_source.dois.append(doi)
                        db.session.add(doi)
        db.session.commit()

    @load_data.command()
    @click.argument('tsv_filename')
    @click.argument('data_source_name')
    def superpopulations(tsv_filename, data_source_name):
        """Import superpopulations from tsv file."""
        print("Importing super populations from '{}'".format(tsv_filename))
        data_source = DataSource.query.filter_by(name=data_source_name).one()
        print("Using data source: {}".format(data_source))
        with open(tsv_filename) as file:
            csvreader = csv.DictReader(file, delimiter='\t')
            for row in csvreader:
                print(row)
                db.session.add(SuperPopulation(code=row['code'],
                                               name=row['name'],
                                               color=row['color'],
                                               data_source=data_source))
        db.session.commit()

    @load_data.command()
    @click.argument('tsv_filename')
    @click.argument('data_source_name')
    def populations(tsv_filename, data_source_name):
        """Import populations from tsv file."""
        print("Importing populations from '{}'".format(tsv_filename))
        data_source = DataSource.query.filter_by(name=data_source_name).one()
        print("Using data source: {}".format(data_source))
        with open(tsv_filename) as file:
            csvreader = csv.DictReader(file, delimiter='\t')
            for row in csvreader:
                print(row)
                if 'super_population' in row:
                    super_population_code = row['super_population']
                elif 'geographic_region' in row:
                    super_population_code = row['geographic_region']
                sp = SuperPopulation.query.filter_by(
                    code=super_population_code).one()
                p, created = get_one_or_create(
                    db.session, Population, code=row['code'], name=row['name'],
                    description=row['description'],
                    latitude=float(row['latitude']),
                    longitude=float(row['longitude']))
                if created:
                    p.data_source = data_source
                p.super_populations.append(sp)
                db.session.add(p)
        db.session.commit()

    @load_data.command()
    @click.argument('file')
    @click.argument('data_source_name')
    def samples(file, data_source_name):
        """Import samples from tsv file."""
        print("Importing samples from '{}'".format(file))
        data_source = DataSource.query.filter_by(name=data_source_name).one()
        print("Using data source: {}".format(data_source))
        with open(file) as fh:
            csvreader = csv.DictReader(fh, delimiter='\t')
            for row in csvreader:
                print(row)
                p = Population.query.filter_by(code=row['Population']).first()
                s = Sample(code=row['Sample'],
                           family_code=row["Family ID"],
                           gender=row["Gender"],
                           family_relationship=row["Relationship"],
                           comments=row["Other Comments"],
                           population=p,
                           data_source=data_source)
                db.session.add(s)
        db.session.commit()

    @load_data.command()
    @click.argument('filename')
    @click.argument('data_source_name')
    def analysis_runs(filename, data_source_name):
        """Import analysis run records from tsv file."""
        print("Importing analysis runs from '{}'".format(filename))
        with open(filename) as file:
            csvreader = csv.DictReader(file, delimiter='\t')
            for row in csvreader:
                print(row)
                data_source = DataSource.query.filter_by(
                    name=row['data_source_name']).one()
                date = parse(row['date'])
                run = ArchaicAnalysisRun(
                    name=row['name'],
                    description=row['description'],
                    date=date,
                    data_source=data_source)
                db.session.add(run)
        db.session.commit()

    @load_data.command()
    @click.argument('analysis_run_name')
    def archaic_genome_data(analysis_run_name):
        """Import archaic genome analysis data for specified analysis run"""
        data_dir = app.config['DATA_DIR']
        analysis_run = ArchaicAnalysisRun.query.filter_by(
            name=analysis_run_name).one()
        print("Importing archaic analysis genome data for run: {}"
              .format(analysis_run))
        analysis_run_dir = os.path.join(
            data_dir, statistics.directory_for_archaic_analysis_run_bed_file(
                analysis_run.id))
        for sample in Sample.query.all():
            for genome_call in ('neand', 'den', 'ambig', 'null'):
                for haplotype in (1, 2):
                    filename = statistics.\
                        filename_for_archaic_genome_data_bedfile(
                            sample_id=sample.id,
                            archaic_genome_call=genome_call,
                            haplotype=haplotype)
                    filepath = os.path.join(analysis_run_dir, filename)
                    print("Checking for file: {}".format(filepath), end='')
                    if (os.path.exists(filepath)):
                        statistics.add_archaic_genome_data_from_bed_file(
                            session=db.session,
                            sample_id=sample.id,
                            archaic_analysis_run_id=analysis_run.id,
                            archaic_genome_call=genome_call,
                            haplotype=haplotype,
                            bed_file_name=filepath
                        )
                        print(" - added")
                    else:
                        print(" - not found")

    @load_data.command()
    @click.argument('analysis_run_name')
    def generate_merged_haplotype(analysis_run_name):
        """Combine two haplotypes into a "merged" haplotype file"""
        data_dir = app.config['DATA_DIR']
        analysis_run = ArchaicAnalysisRun.query.filter_by(
            name=analysis_run_name).one()
        print("Importing archaic analysis genome data for run: {}"
              .format(analysis_run))
        analysis_run_dir = os.path.join(
            data_dir, statistics.directory_for_archaic_analysis_run_bed_file(
                analysis_run.id))
        for sample in Sample.query.all():
            for genome_call in ('neand', 'den', 'ambig', 'null'):
                haplotype_1_filepath = os.path.join(
                    analysis_run_dir, statistics.
                    filename_for_archaic_genome_data_bedfile(
                        sample_id=sample.id,
                        archaic_genome_call=genome_call,
                        haplotype=1))
                haplotype_2_filepath = os.path.join(
                    analysis_run_dir, statistics.
                    filename_for_archaic_genome_data_bedfile(
                        sample_id=sample.id,
                        archaic_genome_call=genome_call,
                        haplotype=2))
                haplotype_0_filepath = os.path.join(
                    analysis_run_dir, statistics.
                    filename_for_archaic_genome_data_bedfile(
                        sample_id=sample.id,
                        archaic_genome_call=genome_call,
                        haplotype=0))
                print("Merging haplotype 1 and 2 for sample {}:{}".format(
                    sample.code, genome_call), end='')
                try:
                    statistics.merge_bed_files(haplotype_1_filepath,
                                               haplotype_2_filepath,
                                               haplotype_0_filepath)
                    statistics.add_archaic_genome_data_from_bed_file(
                        session=db.session,
                        sample_id=sample.id,
                        archaic_analysis_run_id=analysis_run.id,
                        archaic_genome_call=genome_call,
                        haplotype=0,
                        bed_file_name=haplotype_0_filepath
                    )
                    print(" - done")
                except (ValueError, FileNotFoundError) as e:
                    print("{} - skipped".format(e))
                    continue

    @load_data.command()
    @click.argument('filename')
    def parse_bed_file(filename):
        """Load bed file"""
        stats = statistics.parse_bed_file(filename)
        print(stats)
