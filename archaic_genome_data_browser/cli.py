import csv
import click
from archaic_genome_data_browser import db
from archaic_genome_data_browser.models import (SuperPopulation, Population,
                                                Sample)


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
                print(', '.join(row.values))
                p = Population.query.filter_by(code=row['Population']).first()
                s = Sample(code=row['Sample'],
                           family_code=row["Family ID"],
                           gender=row["Gender"],
                           family_relationship=row["Relationship"],
                           comments=row["Other Comments"],
                           population=p)
                db.session.add(s)
        db.session.commit()
