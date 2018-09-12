import csv
import click
import sys
from archaic_genome_data_browser import db
from archaic_genome_data_browser.models import (SuperPopulation, Population,
                                                Sample, ArchaicAnalysisRun,
                                                ArchaicGenomeData,
                                                get_one_or_create)


def register(app):
    @app.cli.group()
    def load_data():
        """Load data into the database."""
        pass

    @load_data.command()
    @click.argument('file')
    def superpopulations(file):
        """Import superpopulations from tsv file."""
        print("Importing super populations from '{}'".format(file))
        with open(file) as fh:
            csvreader = csv.reader(fh, delimiter='\t')
            for row in csvreader:
                print(', '.join(row))
                db.session.add(SuperPopulation(code=row[1], name=row[0]))
        db.session.commit()

    @load_data.command()
    @click.argument('file')
    def populations(file):
        """Import populations from tsv file."""
        print("Importing populations from '{}'".format(file))
        with open(file) as fh:
            csvreader = csv.reader(fh, delimiter='\t')
            for row in csvreader:
                print(', '.join(row))
                sp = SuperPopulation.query.filter_by(code=row[3]).first()
                p = Population(code=row[0], name=row[1], description=row[2],
                               super_population=sp)
                db.session.add(p)
        db.session.commit()

    @load_data.command()
    @click.argument('file')
    def samples(file):
        """Import samples from tsv file."""
        print("Importing samples from '{}'".format(file))
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
                           population=p)
                db.session.add(s)
        db.session.commit()

    @load_data.command()
    @click.argument('filename')
    @click.argument('analysis_run_name')
    def archaic_genome_data(filename, analysis_run_name):
        """Import archaic genome analysis data for specified analysis run"""
        analysis_run, created = get_one_or_create(
            db.session, ArchaicAnalysisRun, name=analysis_run_name)
        if created:
            print("Created new Analysis Run {}".format(analysis_run))
        db.session.add(analysis_run)
        if analysis_run is None:
            raise RuntimeError("Unable to find analysis run named '{}'".
                               format(analysis_run_name))
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
