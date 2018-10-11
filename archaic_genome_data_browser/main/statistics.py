import os
import pybedtools
from slugify import slugify
from archaic_genome_data_browser.models import (Sample, ArchaicAnalysisRun,
                                                ArchaicGenomeData)


def parse_bed_file(filename):
    '''Parse bed file and output stastics as dictionary'''
    bedtool = pybedtools.bedtool.BedTool(filename)
    stats = {
        "total_coverage": bedtool.total_coverage(),
        "count": bedtool.count()
    }
    return stats


def filename_for_archaic_genome_data_bedfile(sample_id, archaic_genome_call,
                                             haplotype):
    bed_file_name_template = (
        "{sample_code}.{population_code}.{archaic_genome_call}_hap{haplotype}."
        "bed.merged.bed")

    sample = Sample.query.get(sample_id)
    population_code = "None"
    if sample.population is not None:
        population_code = sample.population.code
    bed_file_name = bed_file_name_template.format(
        sample_code=sample.code,
        population_code=population_code,
        archaic_genome_call=archaic_genome_call,
        haplotype=str(haplotype)
    )
    return bed_file_name


def directory_for_archaic_analysis_run(archaic_analysis_run_id):
    archaic_analysis_run = ArchaicAnalysisRun.query.get(
        archaic_analysis_run_id)
    archaic_analysis_dirname_slug = slugify(archaic_analysis_run.name)
    return archaic_analysis_dirname_slug


def directory_for_archaic_analysis_run_bed_file(archaic_analysis_run_id):
    return os.path.join(directory_for_archaic_analysis_run(
        archaic_analysis_run_id), 'bed_files')


def add_archaic_genome_data_from_bed_file(session, sample_id,
                                          archaic_analysis_run_id,
                                          archaic_genome_call, haplotype,
                                          bed_file_name):
    sample = Sample.query.get(sample_id)
    archaic_analysis_run = ArchaicAnalysisRun.query.get(
        archaic_analysis_run_id)
    stats = parse_bed_file(bed_file_name)
    archaic_genome_data = ArchaicGenomeData(
        sample=sample,
        archaic_analysis_run=archaic_analysis_run,
        archaic_genome_call=archaic_genome_call,
        haplotype=haplotype,
        bed_file=bed_file_name,
        total_bps=stats.get('total_coverage'),
        total_haplotypes=stats.get('count')
    )
    session.add(archaic_genome_data)
    session.commit()


# def avg_neadertal_bp(query):
#     '''Calculates averages for columns in archaic_genome_data rows'''
#     archaic_genome_data_query = db.session.query(
#         func.avg(ArchaicGenomeData.neandertal_bp))
#
#
#     .join(Sample).\
#         join(Population).join(SuperPopulation).\
#             filter(SuperPopulation.id == id)
#     archaic_analysis_data = {}
#     for archaic_analysis_run in archaic_analysis_runs:
#         data = archaic_genome_data_query.join(ArchaicAnalysisRun).\
#             filter(ArchaicAnalysisRun.id == archaic_analysis_run.id).first()
#         archaic_analysis_data[archaic_analysis_run.id] = data
