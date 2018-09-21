from flask import render_template, flash, redirect, url_for, jsonify
from archaic_genome_data_browser.main import bp
from archaic_genome_data_browser.main.forms import LoginForm
from archaic_genome_data_browser.models import (SuperPopulation, Population,
                                                Sample, ArchaicAnalysisRun,
                                                ArchaicGenomeData, DataSource)
import random


@bp.route('/')
@bp.route('/index')
def index():
    super_population_data_sources = (
        DataSource.query.join(SuperPopulation).all())
    return render_template(
        'index.html', title='Home',
        super_population_data_sources=super_population_data_sources)


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
    # TODO Implement some average stats function(s)
    # https://stackoverflow.com/questions/7143235/how-to-use-avg-and-sum-in-sqlalchemy-query
    # session.query(func.avg(Rating.field2).label('average')).filter(Rating.url==url_string.netloc)
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
    # super_populations_query = SuperPopulation.query.join(
    #     populations_query.subquery(),
    #     SuperPopulation.populations)
    # super_populations_with_data = super_populations_query.all()
    populations_with_data = populations_query.all()

    return render_template('archaic_analysis_run.html',
                           title=archaic_analysis_run.name,
                           archaic_analysis_run=archaic_analysis_run,
                           populations=populations_with_data)


@bp.route('/population_data/<archaic_analysis_run_id>')
def population_data(archaic_analysis_run_id):
    populations = Population.query.all()
    geojson = {
        'type': 'FeatureCollection',
        'features': []
    }
    for population in populations:
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
                'color': '#A00'
            },
        })
    return jsonify(geojson)
