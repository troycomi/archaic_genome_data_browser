from archaic_genome_data_browser import db
from sqlalchemy.orm import column_property
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import select, func


class Sample(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(32), index=True, unique=True)
    family_code = db.Column(db.String(32), index=True)
    gender = db.Column(db.String(32))
    family_relationship = db.Column(db.String(128))
    comments = db.Column(db.Text)
    population_id = db.Column(db.Integer, db.ForeignKey('population.id'))
    data_source_id = db.Column(db.Integer, db.ForeignKey('data_source.id'))
    archaic_genome_data = db.relationship('ArchaicGenomeData',
                                          backref='sample',
                                          lazy='dynamic')

    def __repr__(self):
        return '<Sample {}>'.format(self.code)


population_group_table = db.Table(
    'population_group', db.Model.metadata,
    db.Column('super_population_id', db.Integer,
              db.ForeignKey('super_population.id')),
    db.Column('population_id', db.Integer, db.ForeignKey('population.id'))
)


class Population(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(32), index=True, unique=True)
    name = db.Column(db.String(128), unique=True)
    description = db.Column(db.String(256))
    data_source_id = db.Column(db.Integer, db.ForeignKey('data_source.id'))
    samples = db.relationship('Sample', backref='population', lazy='dynamic')

    sample_count = column_property(
        select([func.count(Sample.id)]).
        where(Sample.population_id == id).
        correlate_except(Sample)
    )

    def samples_with_data_from_run(self, archaic_analysis_run_id):
        return Sample.query.join(ArchaicGenomeData).\
            join(ArchaicAnalysisRun).\
            join(Population).\
            filter(ArchaicAnalysisRun.id == archaic_analysis_run_id).\
            filter(Population.id == self.id).all()

    def __repr__(self):
        return '<Population {}>'.format(self.code)


class SuperPopulation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(32), index=True, unique=True)
    name = db.Column(db.String(128))
    data_source_id = db.Column(db.Integer, db.ForeignKey('data_source.id'))
    populations = db.relationship('Population',
                                  secondary=population_group_table,
                                  backref=db.backref('super_populations',
                                                     lazy=True)
                                  )

    # TODO Make this a hybrid_property?
    def samples(self):
        samples = set()
        for population in self.populations:
            for sample in population.samples:
                samples.add(sample)
        return samples

    @property
    def population_count(self):
        return db.Session.object_session(self).\
            query(Population).with_parent(self, "populations").count()

    # population_count = column_property(
    #     select([func.count(population_group_table.population_id)]).
    #     select_from(population_group_table.join(Population.__table__)).
    #     where(population_group_table.super_population_id == id).
    #     correlate_except(Population)
    # )

    @property
    def sample_count(self):
        return db.Session.object_session(self).\
            query(Sample).join(Population).\
            with_parent(self, "populations").count()

    # sample_count = column_property(
    #     select([func.count(Sample.id)]).
    #     select_from(Population.__table__.join(Sample.__table__)).
    #     where(Population.super_population_id == id).
    #     correlate_except(Sample)
    # )

    def __repr__(self):
        return '<SuperPopulation {}>'.format(self.code)


data_source_doi_table = db.Table(
    'data_source_doi', db.Model.metadata,
    db.Column('doi_id', db.Integer,
              db.ForeignKey('digital_object_identifier.id')),
    db.Column('data_source_id', db.Integer, db.ForeignKey('data_source.id'))
)


class DataSource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, unique=True)
    description = db.Column(db.Text)
    dois = db.relationship(
        "DigitalObjectIdentifier",
        secondary=data_source_doi_table,
        backref=db.backref("data_sources", lazy=True)
    )
    super_populations = db.relationship(
        "SuperPopulation",
        backref=db.backref("data_source", lazy=True)
    )
    popoulations = db.relationship(
        "Population",
        backref=db.backref("data_source", lazy=True)
    )
    samples = db.relationship(
        "Sample",
        backref=db.backref("data_source", lazy=True)
    )
    archaic_analysis_runs = db.relationship(
        "ArchaicAnalysisRun",
        backref=db.backref("data_source", lazy=True)
    )

    def __repr__(self):
        return '<DataSource {}>'.format(self.name)


class DigitalObjectIdentifier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, unique=True)
    doi = db.Column(db.String(256), unique=True)

    @hybrid_property
    def url(self):
        url = None
        if self.doi is not None:
            url = "https://doi.org/{}".format(self.doi)
        return url

    def __repr__(self):
        return '<DOI {}>'.format(self.doi)


class ArchaicAnalysisRun(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, unique=True)
    description = db.Column(db.Text)
    publication_doi = db.Column(db.String(256))
    date = db.Column(db.DateTime)
    data_source_id = db.Column(db.Integer, db.ForeignKey('data_source.id'))
    archaic_genome_data = db.relationship('ArchaicGenomeData',
                                          backref='archaic_analysis_run',
                                          lazy='dynamic')

    @hybrid_property
    def publication_url(self):
        publication_url = None
        if self.publication_doi is not None:
            publication_url = "https://doi.org/{}".foramt(self.publication_doi)
        return publication_url

    def __repr__(self):
        return '<ArchaicAnalysisRun {}>'.format(self.name)


class ArchaicGenomeData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sample_id = db.Column(db.Integer, db.ForeignKey('sample.id'),
                          nullable=False)
    archaic_analysis_run_id = db.Column(
        db.Integer, db.ForeignKey('archaic_analysis_run.id'),
        nullable=False)
    __table_args__ = (
        db.Index('idx_sample_run', 'sample_id',
                 'archaic_analysis_run_id', unique=True),
    )
    neandertal_bp = db.Column(db.Integer)
    neandertal_haplotypes = db.Column(db.Integer)
    neandertal_sstar_bed = db.Column(db.String(512))
    denisovan_bp = db.Column(db.Integer)
    denisovan_haplotypes = db.Column(db.Integer)
    denisovan_sstar_bed = db.Column(db.String(512))

    def __repr__(self):
        return '<ArchaicGenomeData {}:{}>'.format(
            self.sample.code, self.archaic_analysis_run.name)


def get_one_or_create(session, model, create_method='',
                      create_method_kwargs=None, **kwargs):
    try:
        return session.query(model).filter_by(**kwargs).one(), False
    except NoResultFound:
        kwargs.update(create_method_kwargs or {})
        created = getattr(model, create_method, model)(**kwargs)
        try:
            session.add(created)
            session.flush()
            return created, True
        except IntegrityError:
            session.rollback()
            return session.query(model).filter_by(**kwargs).one(), False
