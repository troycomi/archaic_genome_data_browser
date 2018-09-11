from archaic_genome_data_browser import db
from sqlalchemy.orm import column_property
from sqlalchemy import select, func


class Population(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(32), index=True, unique=True)
    name = db.Column(db.String(128), unique=True)
    description = db.Column(db.String(256))
    super_population_id = db.Column(db.Integer,
                                    db.ForeignKey('super_population.id'))
    samples = db.relationship('Sample', backref='population', lazy='dynamic')

    def __repr__(self):
        return '<Population {}>'.format(self.code)


class Sample(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(32), index=True, unique=True)
    family_code = db.Column(db.String(32), index=True)
    gender = db.Column(db.String(32))
    family_relationship = db.Column(db.String(128))
    comments = db.Column(db.Text)
    population_id = db.Column(db.Integer, db.ForeignKey('population.id'))

    def __repr__(self):
        return '<Sample {}>'.format(self.code)


class SuperPopulation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(32), index=True, unique=True)
    name = db.Column(db.String(128))
    populations = db.relationship('Population',
                                  backref='super_population',
                                  lazy='dynamic')

    def samples(self):
        samples = set()
        for population in self.populations:
            for sample in population.samples:
                samples.add(sample)
        return samples

    population_count = column_property(
        select([func.count(Population.id)]).
        where(Population.super_population_id == id).
        correlate_except(Population)
    )

    def __repr__(self):
        return '<Sample {}>'.format(self.code)
