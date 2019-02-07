import archaic_genome_data_browser.models as mod
import pytest


@pytest.fixture
def test_db(session):
    # add some populations
    for i in range(3):
        session.add(mod.Population(name=f'pop{i}'))

    # hold populations for adding samples later
    pops = session.query(mod.Population)

    run = mod.ArchaicAnalysisRun(name='run1')
    session.add(run)
    sample1 = mod.Sample(code='samp1', population=pops[0])
    for gc, bp, hap in zip(['neand', 'den', 'ambig', 'null'],
                           [100, 200, 300, 400],
                           [10, 20, 30, 40]):
        session.add(mod.ArchaicGenomeData(sample=sample1,
                                          archaic_analysis_run=run,
                                          archaic_genome_call=gc,
                                          haplotype=1,
                                          bed_file="",
                                          total_bps=bp,
                                          total_haplotypes=hap))

        session.add(mod.ArchaicGenomeData(sample=sample1,
                                          archaic_analysis_run=run,
                                          archaic_genome_call=gc,
                                          haplotype=2,
                                          bed_file="",
                                          total_bps=bp,
                                          total_haplotypes=hap))

    run = mod.ArchaicAnalysisRun(name='run2')
    session.add(run)
    run = mod.ArchaicAnalysisRun(name='run3')
    session.add(run)
    return session


def test_get_statistics(test_db):
    runs = test_db.query(mod.ArchaicAnalysisRun).all()
    assert runs[0].get_statistics(1) == {'neandertal_bp': 0.1,
                                         'neandertal_haplotypes': 0.1,
                                         'denisovan_bp': 0.2,
                                         'denisovan_haplotypes': 0.2,
                                         }
