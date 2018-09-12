from archaic_genome_data_browser import create_app, db, cli
from archaic_genome_data_browser.models import (SuperPopulation, Population,
                                                Sample, ArchaicAnalysisRun,
                                                ArchaicGenomeData)

app = create_app()
cli.register(app)


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'SuperPopulation': SuperPopulation,
            'Population': Population, 'Sample': Sample,
            'ArchaicAnalysisRun': ArchaicAnalysisRun,
            'ArchaicGenomeData': ArchaicGenomeData}
