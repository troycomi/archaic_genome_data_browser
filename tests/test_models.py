from archaic_genome_data_browser.models import (Sample, DataSource,
                                                DigitalObjectIdentifier,
                                                SuperPopulation)


def test_datasource_add(session):
    datasource = DataSource(name='Testing',
                            description='A unit test datasource')

    assert session.query(DataSource).count() == 0
    session.add(datasource)
    session.commit()
    assert session.query(DataSource).count() == 1

    datasource = session.query(DataSource).one()
    assert datasource.name == 'Testing'
    assert datasource.description == 'A unit test datasource'


def test_doi_datasource_relation(session):
    ds = DataSource(name='DS1', description="")
    session.add(ds)
    ds = DataSource(name='DS2', description="")
    session.add(ds)
    assert session.query(DataSource).count() == 2

    ds = [session.query(DataSource).filter_by(name="DS1").one(),
          session.query(DataSource).filter_by(name="DS2").one()]

    dnames = [f'doi_{i}' for i in range(3)]
    dois = [f'10.{i}' for i in range(3)]

    for i in range(3):
        doi = DigitalObjectIdentifier(name=dnames[i],
                                      doi=dois[i])
        ds[i % 2].dois.append(doi)
        session.add(doi)

    assert session.query(DigitalObjectIdentifier).count() == 3

    ds = session.query(DataSource).filter_by(name="DS1").one()
    assert [doi.name for doi in ds.dois] == ['doi_0', 'doi_2']

    ds = session.query(DataSource).filter_by(name="DS2").one()
    assert [doi.name for doi in ds.dois] == ['doi_1']


def test_superpopulation_datasource_relation(session):
    ds = DataSource(name='DS1', description="")
    session.add(ds)
    ds = DataSource(name='DS2', description="")
    session.add(ds)
    assert session.query(DataSource).count() == 2

    ds = [session.query(DataSource).filter_by(name="DS1").one(),
          session.query(DataSource).filter_by(name="DS2").one()]

    names = [f'name_{i}' for i in range(9)]
    codes = [f'code_{i}' for i in range(9)]
    colors = [f'color_{i}' for i in range(9)]

    for i in range(9):
        session.add(SuperPopulation(code=codes[i],
                                    name=names[i],
                                    color=colors[i],
                                    data_source=ds[i % 2]))

    assert session.query(SuperPopulation).count() == 9

    ds = session.query(DataSource).filter_by(name="DS1").one()
    assert [pop.name for pop in ds.super_populations] == names[0::2]

    ds = session.query(DataSource).filter_by(name="DS2").one()
    assert [pop.name for pop in ds.super_populations] == names[1::2]


def test_sample_add(session):
    sample = Sample(code="test")

    assert session.query(Sample).count() == 0
    session.add(sample)
    session.commit()
    assert session.query(Sample).count() == 1

    sample = session.query(Sample).one()
    assert sample.id > 0
    assert sample.code == "test"


def test_empty(session):
    assert session.query(Sample).count() == 0
