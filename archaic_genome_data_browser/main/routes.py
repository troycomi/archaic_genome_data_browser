from flask import render_template, flash, redirect, url_for
from archaic_genome_data_browser.main import bp
from archaic_genome_data_browser.main.forms import LoginForm
from archaic_genome_data_browser.models import (SuperPopulation, Population,
                                                Sample, ArchaicAnalysisRun,
                                                ArchaicGenomeData)


@bp.route('/')
@bp.route('/index')
def index():
    super_populations = SuperPopulation.query.all()
    return render_template('index.html', title='Home',
                           super_populations=super_populations)


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
    super_populations = SuperPopulation.query.join(Population).join(Sample).\
        join(ArchaicGenomeData).\
        filter(ArchaicGenomeData.archaic_analysis_run_id == id)
    return render_template('archaic_analysis_run.html',
                           title=archaic_analysis_run.name,
                           archaic_analysis_run=archaic_analysis_run,
                           super_populations=super_populations)
