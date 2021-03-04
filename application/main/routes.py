from datetime import datetime
import os

from application import current_app as app
from application import db
from application.main import bp
from application.main.helpers import read_data
from application.models import Account

from flask import render_template, flash, redirect, url_for, request, session
from flask_login import login_required, current_user

from application.main.forms import FileSubmit, TagForm
from wtforms import FieldList, FormField
from flask_wtf import FlaskForm

from werkzeug.utils import secure_filename


def get_data(bank=None, page=None, start=None, end=None):

    if start and end:
        return Account.query\
                .filter(
                        Account.user_id == current_user.id,
                        Account.bank == bank,
                        Account.timestamp >= datetime.strptime(start, "%Y-%m-%d"),
                        Account.timestamp <= datetime.strptime(end, "%Y-%m-%d"),
                )\
                .paginate(page=page, per_page=app.config['ROWS_PER_PAGE'])
    elif start:
        return Account.query\
            .filter(
                    Account.user_id == current_user.id,
                    Account.bank == bank,
                    Account.timestamp >= datetime.strptime(start, "%Y-%m-%d")
            )\
            .paginate(page=page, per_page=app.config['ROWS_PER_PAGE'])
    else:
        return Account.query\
                .filter(
                    Account.user_id == current_user.id,
                    Account.bank == bank
                )\
                .paginate(page=page, per_page=app.config['ROWS_PER_PAGE'])

def get_dates(bank, start=None):

    if bank and start:
        return Account.query.with_entities(Account.timestamp) \
            .filter(Account.bank == bank, Account.timestamp >= datetime.strptime(start, "%Y-%m-%d")) \
            .order_by(Account.timestamp) \
            .distinct().all()
    else:
        return Account.query.with_entities(Account.timestamp) \
            .filter(Account.bank == bank) \
            .order_by(Account.timestamp) \
            .distinct().all()

def tags_creator(rows):
    
    class TagsList(FlaskForm):
        tags = FieldList(FormField(TagForm), min_entries=rows)

    return TagsList()


@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():

    count = 0
    if Account.query.all():
        count = len(Account.query.filter(Account.user_id == current_user.id).with_entities(Account.id).distinct().all())

    uploaded = None
    form = FileSubmit()
    if request.method == 'POST':
        if form.validate_on_submit():
            f = form.file.data
            filename = secure_filename(f.filename)
            save_path = os.path.join(app.config['UPLOAD_PATH'], filename)
            f.save(save_path)
            if form.upload.data:
                try:
                    uploaded = read_data(save_path)
                    if uploaded:
                        flash('Upload successful!')
                        app.logger.info('A new file has been uploaded.')
                    else:
                        flash('Estos registros ya han sido cargados')
                except:
                    flash('Parsing issue!')
                    app.logger.info('Parsing issue.')

    return render_template('main/upload.html', form=form, data=uploaded, count = count)

@bp.route("/flow", methods=["GET","POST"])
@login_required
def flow():

    flow = None
    bank_list = None
    bank = None
    start_date = None
    end_date = None
    s_dates = None
    e_dates = None

    if Account.query.all():
        bank_list = Account.query.filter(Account.user_id==current_user.id).with_entities(Account.bank).distinct().all()

    if request.form.get("bank"):
        bank = session['bank'] = request.form.get("bank")
        page = session['page'] = request.args.get('page', 1, type=int)
        flow = get_data(bank, page)
        s_dates = get_dates(bank)

        session['submit'] = 1
    
    if request.form.get('start_date'):
        bank = session.get("bank")
        page = request.args.get('page', 1, type=int)
        session['start_date'] = request.form.get("start_date")
        start_date = session.get("start_date")
        flow = get_data(bank, page, start_date)
        s_dates = get_dates(bank)
        e_dates = get_dates(bank, start_date)

        session['submit'] = 2
    
    if request.form.get('end_date'):
        bank = session.get("bank")
        page = request.args.get('page', 1, type=int)
        start_date = session['start_date']
        session['end_date'] = request.form.get('end_date')
        end_date = session.get('end_date')
        flow = get_data(bank, page, start_date, end_date)
        s_dates = get_dates(bank)
        e_dates = get_dates(bank, start_date)

        session['submit'] = 3

    if request.args.get('page', type=int):

        page = request.args.get('page', type=int)
        
        if session.get('submit') == 1:
            bank = session.get('bank')
            s_dates = get_dates(bank)
            flow = get_data(bank, page)
        elif session.get('submit') == 2:
            bank = session.get('bank')
            start_date = session.get('start_date')
            s_dates = get_dates(bank)
            e_dates = get_dates(bank, start_date)
            flow = get_data(bank, page, start_date)
        else:
            bank = session.get('bank')
            start_date = session.get('start_date')
            s_dates = get_dates(bank)
            e_dates = get_dates(bank, start_date)
            flow = get_data(bank, page, start_date)
            end_date = session.get('end_date')
            flow = get_data(bank, page, start_date, end_date)
    
    return render_template("main/flow.html", 
        banks=bank_list,
        bank=bank,
        data=flow,
        start_date=start_date,
        end_date=end_date,
        e_dates=e_dates,
        s_dates = s_dates
        )

@bp.route("/tag_table", methods=["GET","POST"])
@login_required
def tag():
    session['bank'] = None
    session['start_date'] = None
    session['end_date'] = None
    session['submit'] = None
    return redirect(url_for('main.tag_table'))

@bp.route("/tag", methods=["GET","POST"])
@login_required
def tag_table():

    bank = None
    start_date = None
    end_date = None
    flow=None
    tags=None
    form=None
    s_dates = None
    e_dates = None

    bank_list = None
    if Account.query.all():
        bank_list = Account.query.filter(Account.user_id==current_user.id).with_entities(Account.bank).distinct().all()

    page = request.args.get('page', 1, type=int)

    if request.form.get("bank"):
        # get bank and save it in session
        session['bank'] = bank = request.form.get("bank")
        # save button
        session['submit'] = submit = 1

    if request.form.get('start_date'):
        # get start date and save it in session
        session['start_date'] = request.form.get("start_date")
        # save button
        session['submit'] = submit = 2
    
    if request.form.get('end_date'):
        # get end date and save it in session
        session['end_date'] = request.form.get('end_date')
        # save button
        session['submit'] = submit = 3

    if session.get("submit") == 1:
        # get params        
        bank = session.get('bank')
        # get all dates
        s_dates = get_dates(session.get('bank'))
    
        flow = get_data(bank, page)
        tags = [line.tag if line.tag != None else '' for line in flow.items]
        form = tags_creator(len(flow.items))

        if 'tag_1' in request.form:
            if form.validate_on_submit():
                for tag, row in zip(form.tags, flow.items):
                    row.tag = tag.data['tag']
            db.session.commit()
            tags = [line.tag if line.tag != None else '' for line in flow.items]

    elif session.get("submit") == 2:
        # get params
        bank = session.get('bank')
        start_date = session.get('start_date')
        # get dates
        s_dates = get_dates(bank)
        e_dates = get_dates(bank, start_date)

        # get data
        flow = get_data(bank, page, start_date)
        tags = [line.tag if line.tag != None else '' for line in flow.items]
        # make form
        form = tags_creator(len(flow.items))

        if 'tag_2' in request.form:
            if form.validate_on_submit():
                for tag, row in zip(form.tags, flow.items):
                    row.tag = tag.data['tag']
            db.session.commit()
            tags = [line.tag if line.tag != None else '' for line in flow.items]

    elif session.get("submit") == 3:
        # get params
        bank = session.get('bank')
        start_date = session.get('start_date')
        end_date = session.get('end_date')

        # get dates
        s_dates = get_dates(bank)
        e_dates = get_dates(bank, start_date)
        # get data
        flow = get_data(bank, page, start_date, end_date)
        tags = [line.tag if line.tag != None else '' for line in flow.items]
        # make form
        form = tags_creator(len(flow.items))

        if 'tag_3' in request.form:
            if form.validate_on_submit():
                for tag, row in zip(form.tags, flow.items):
                    row.tag = tag.data['tag']
            db.session.commit()
            tags = [line.tag if line.tag != None else '' for line in flow.items]

    return render_template("main/tag_table.html", 
        banks=bank_list,
        bank=bank,
        start_date=start_date,
        end_date=end_date,
        e_dates=e_dates,
        s_dates = s_dates,
        submit = session.get('submit'),
        data=flow,
        tags=tags,
        form=form,
        value=tags
        )

