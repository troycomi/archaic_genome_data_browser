import csv
import click
import sys
import yaml
from dateutil.parser import parse
from archaic_genome_data_browser import db
from archaic_genome_data_browser.models import (SuperPopulation, Population,
                                                Sample, ArchaicAnalysisRun,
                                                ArchaicGenomeData, DataSource,
                                                DigitalObjectIdentifier,
                                                get_one_or_create)


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
    @click.argument('filename')
    @click.argument('analysis_run_name')
    def archaic_genome_data(filename, analysis_run_name):
        """Import archaic genome analysis data for specified analysis run"""
        analysis_run = ArchaicAnalysisRun.query.filter_by(
            name=analysis_run_name).one()
        print("Importing archaic genome data from '{}'".format(filename))
        print("Using archaic analysis run: {}".format(analysis_run))
        with open(filename) as file:
            csvreader = csv.DictReader(file, delimiter=' ')
            for row in csvreader:
                print(row)
                sample = Sample.query.filter_by(code=row['ind']).first()
                if sample is None:
                    sys.stderr.write("Unable to find sample '{}'\n".
                                     format(row['ind']))
                    continue
                print(analysis_run)
                print(sample)
                genome_data = ArchaicGenomeData(
                    sample=sample,
                    archaic_analysis_run=analysis_run,
                    neandertal_bp=row['neand'],
                    denisovan_bp=row['den'])
                db.session.add(genome_data)
        db.session.commit()
