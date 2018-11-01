from archaic_genome_data_browser.models import Sample


def test_sample_model(session):
    sample = Sample(code="test")

    session.add(sample)
    session.commit()

    assert sample.id > 0
    assert sample.code == "test"


def test_empty(session):
    assert session.query(Sample).count() == 0
