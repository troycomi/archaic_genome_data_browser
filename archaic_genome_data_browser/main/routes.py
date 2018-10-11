import os
from flask import render_template, flash, redirect, url_for, jsonify, send_file
from archaic_genome_data_browser import db
from archaic_genome_data_browser.main import bp
from archaic_genome_data_browser.main.forms import LoginForm
from archaic_genome_data_browser.models import (SuperPopulation, Population,
                                                Sample, ArchaicAnalysisRun,
                                                ArchaicGenomeData, DataSource)


@bp.route('/', defaults={'super_population_data_source_id': 2})
@bp.route('/index/', defaults={'super_population_data_source_id': 2})
@bp.route('/index/<super_population_data_source_id>')
def index(super_population_data_source_id):
    selected_data_source = (
        DataSource.query.join(SuperPopulation).
        filter(DataSource.id == super_population_data_source_id).first_or_404()
    )
    other_data_sources = (
        DataSource.query.join(SuperPopulation).
        filter(DataSource.id != super_population_data_source_id)).all()
    return render_template(
        'index.html', title='Home',
        other_data_sources=other_data_sources,
        selected_data_source=selected_data_source)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('main.index'))
    return render_template('login.html', title='Sign In', form=form)


@bp.route('/superpopulation/<id>')
def super_population(id):
    super_population = SuperPopulation.query.filter_by(id=id).first_or_404()
    return render_template('super_population.html',
                           title=super_population.name,
                           super_population=super_population)


@bp.route('/population/<id>')
def population(id):
    population = Population.query.filter_by(id=id).first_or_404()
    return render_template('population.html',
                           title=population.name,
                           population=population)


@bp.route('/sample/<id>')
def sample(id):
    sample = Sample.query.filter_by(id=id).first_or_404()
    return render_template('sample.html',
                           title=sample.code,
                           sample=sample)


@bp.route('/archaic_analysis_run/<id>')
def archaic_analysis_run(id):
    archaic_analysis_run = \
        ArchaicAnalysisRun.query.filter_by(id=id).first_or_404()
    populations_query = Population.query.\
        join(Sample).\
        join(ArchaicGenomeData).\
        filter(ArchaicGenomeData.archaic_analysis_run_id == id)
    populations_with_data = populations_query.all()

    return render_template('archaic_analysis_run.html',
                           title=archaic_analysis_run.name,
                           archaic_analysis_run=archaic_analysis_run,
                           populations=populations_with_data)


@bp.route('/population_data/<super_population_data_source_id>')
def population_data(super_population_data_source_id):
    pop_superpops = db.session.query(Population, SuperPopulation).\
        join(SuperPopulation, Population.super_populations).\
        filter(SuperPopulation.data_source_id
               == super_population_data_source_id).all()
    geojson = {
        'type': 'FeatureCollection',
        'features': []
    }
    for (population, super_population) in pop_superpops:
        geojson['features'].append({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [population.longitude,
                                population.latitude]
            },
            'properties': {
                'name': population.name,
                'description': population.description,
                'url': url_for('main.population', id=population.id),
                'color': super_population.color
            },
        })
    return jsonify(geojson)


@bp.route('/archaic_genome_data_bed_file/<id>')
def archaic_genome_data_bed_file(id):
    archaic_genome_data = ArchaicGenomeData.query.filter_by(id=id).\
        first_or_404()
    return send_file(archaic_genome_data.bed_file, as_attachment=True)


@bp.app_template_filter('basename')
def basename(path):
    return os.path.basename(path)
