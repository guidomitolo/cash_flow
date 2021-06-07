# basic libs
from datetime import datetime
import os
# app objects
from application import current_app as app
from application import db
from application.main import bp
from application.main.models import Balance, Credit, CreditCard, CreditStatement
from application.main.forms import FileSubmitCredit, FileSubmitBalance, LoadCreditCard, tags_creator
# add hoc functions
from application.main.reader_balance import load_movs
from application.main.reader_credit import load_PDF
from application.main.queries import get_data, get_credit, get_dates, tag_due_dates, classification, balance_card_payments, add_credit_card
# user management libs
from flask import render_template, flash, redirect, url_for, request, session
from flask_login import login_required, current_user
# db orm func
from sqlalchemy import or_
# file upload security
from werkzeug.utils import secure_filename

from application.main.reader_credit import load_PDF


@bp.route('/upload_movs', methods=['GET', 'POST'])
@login_required
def upload_movs():

    count = 0
    uploaded = None

    form = FileSubmitBalance()
    if request.method == 'POST':
        if form.validate_on_submit():
            f = form.file.data
            filename = secure_filename(f.filename)
            save_path = os.path.join(app.config['UPLOAD_PATH'], filename)
            f.save(save_path)
            if form.upload.data:
                try:
                    # uploaded = load_movs(save_path)
                    uploaded = load_movs(save_path)
                    if uploaded:
                        flash('Upload successful!')
                        app.logger.info('A new file has been uploaded.')
                        # tag due dats
                        tag_due_dates()
                    else:
                        flash('Estos registros ya han sido cargados')
                except:
                    flash('Parsing issue!')
                    app.logger.info('Parsing issue.')

    if Balance.query.all():
        count = len(Balance.query.filter(Balance.user_id == current_user.id).with_entities(Balance.id).distinct().all())

    return render_template('main/upload_movs.html', form=form, data=uploaded, count = count)


@bp.route('/upload_credit', methods=['GET', 'POST'])
@login_required
def upload_credit():

    count = 0
    transactions = None
    close_date = None
    due_date = None
    taxes = None

    cards = CreditCard.query.all()

    form_trans = FileSubmitCredit()
    form_card = LoadCreditCard()

    add_credit_card()

    if request.method == 'POST':
        if 'card_button' in request.form:
            if form_card.validate_on_submit():
                card_vendor = form_card.card.data
                card_number = form_card.card_number.data
                expiration = form_card.expiration.data
                bank = form_card.bank.data
                if cards:
                    for card in cards:
                        if card.number == card_number:
                            flash('La tarjeta ya ha sido cargada')
                            return redirect(url_for('main.upload_credit'))
                credit_card = CreditCard(
                    user_id = current_user.id,
                    number = card_number,
                    vendor = card_vendor,
                    expiration = expiration,
                    bank =  bank
                )
                db.session.add(credit_card)
                db.session.commit()
                flash('Usted ha cargado una nueva tarjeta')
                # add card number if match with card_code
                add_credit_card()
                # add debt type
                classification()
        else:
            if form_trans.validate_on_submit():
                f = form_trans.file.data
                filename = secure_filename(f.filename)
                save_path = os.path.join(app.config['UPLOAD_PATH'], filename)
                f.save(save_path)
                if form_trans.upload.data:
                    try:
                        uploaded = load_PDF(save_path)
                        if uploaded:
                            transactions = uploaded[0]
                            close_date = uploaded[3]
                            due_date = uploaded[2]
                            taxes = uploaded[1]
                            flash('¡Carga exitosa!')
                            app.logger.info('Carga Exitosa')
                        else:
                            flash('Estos registros ya han sido cargados')
                    except:
                        flash('Hemos detectado un problema en la carga')
                        app.logger.info('Error de Lectura')
    
    if Credit.query.all():
        count = len(Credit.query.filter(Credit.user_id == current_user.id).with_entities(Credit.id).distinct().all())

    return render_template(
        'main/upload_credit.html',
        form = form_trans,
        data = transactions,
        close_date = close_date,
        due_date = due_date,
        taxes = taxes,
        count = count,
        cards = cards,
        form_card = form_card
        )


@bp.route("/due_date", methods=["GET","POST"])
@login_required
def due_dates():

    flow = Balance.query.filter_by(type="Vencimiento Tarjeta").all()
    balance_card_payments()

    cards = CreditCard.query.all()
    dates = []

    for row in flow:
        if row.timestamp.date() not in dates:
            dates.append(row.timestamp.date())

    past_dues = CreditStatement.query.order_by(CreditStatement.due_date).all()
  
    return render_template(
        'main/due_date.html',
        cards = cards,
        past_dues = past_dues,
        dates = dates
        )


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
    tag_list = None
    selected_tag = None

    if Balance.query.all():
        bank_list = Balance.query.filter(Balance.user_id==current_user.id).with_entities(Balance.bank).distinct().all()
        tag_list = Balance.query.filter(Balance.type != None, Balance.type != '').with_entities(Balance.type).distinct().all()

    if request.form.get("type"):
        selected_tag = request.form.get("type")
        tag = session['tag'] = request.form.get("type")
        page = session['page'] = request.args.get('page', 1, type=int)
        flow = get_data(bank, tag=tag)

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
        s_dates = s_dates,
        tag_list = tag_list,
        selected_tag = selected_tag
        )


@bp.route("/tag_table/<string:type>", methods=["GET","POST"])
@login_required
def tag(type):

    session['bank'] = None
    session['start_date'] = None
    session['end_date'] = None
    session['submit'] = None
    session['due_date'] = None
    session['card_number'] = None
    session['credit_type'] = None
  
    if type == 'flow':
        return redirect(url_for('main.tag_balance'))
    else:
        return redirect(url_for('main.card_amount'))



@bp.route("/card_amount", methods=["GET","POST"])
@login_required
def card_amount():

    sel_date = session.get('due_date') 
    sel_card = session.get('card_number')
    sel_type = session.get('credit_type') 

    page = request.args.get('page', 1, type=int)
    if request.args.get('page', type=int):
        page = request.args.get('page', 1, type=int)

    flow = get_credit(page=page)
    cards = CreditCard.query.all()
    dues = db.session.query(CreditStatement.due_date).distinct().all()
    types = db.session.query(Credit.type).distinct().all()

    if request.form.get('button_select_card'):
        card_number = request.form.get('cards').split()[1]
        session['card_number'] = card_number
        flow = get_credit(
            page=page, 
            card_number=card_number, 
            due_date = session.get('due_date')
        )

    if request.form.get('button_select_date'):
        sel_date = datetime.strptime(request.form.get('dues'), "%Y-%m-%d")
        session['due_date'] = sel_date
        flow = get_credit(
            page=page, 
            due_date = sel_date, 
            card_number=session.get('card_number')
        )

    if request.form.get('button_select_type'):
        sel_type = request.form.get('types')
        session['credit_type'] = sel_type
        flow = get_credit(
            page=page, 
            type = sel_type,
        )

    if request.form.get('items_selected'):
        for id in request.form.getlist('chk_type'):
            print(id)
        return redirect(url_for('main.card_amount'))


    return render_template(
        'main/card_amount.html',
        data = flow,
        cards = cards,
        dues = dues,
        types = types,
        sel_type = sel_type,
        sel_date = sel_date,
        sel_card = sel_card,
        )



@bp.route("/flow", methods=["GET","POST"])
@login_required
def tag_balance():

    bank = None
    start_date = None
    end_date = None
    flow=None
    tags=None
    form=None
    s_dates = None
    e_dates = None

    bank_list = None
    if Balance.query.all():
        bank_list = Balance.query.filter(Balance.user_id==current_user.id).with_entities(Balance.bank).distinct().all()

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
        tags = [line.type if line.type != None else '' for line in flow.items]
        form = tags_creator(len(flow.items))

        if 'tag_1' in request.form:
            if form.validate_on_submit():
                for tag, row in zip(form.tags, flow.items):
                    row.tag = tag.data['tag']
            db.session.commit()
            tags = [line.type if line.type != None else '' for line in flow.items]

    elif session.get("submit") == 2:
        # get params
        bank = session.get('bank')
        start_date = session.get('start_date')
        # get dates
        s_dates = get_dates(bank)
        e_dates = get_dates(bank, start_date)

        # get data
        flow = get_data(bank, page, start_date)
        tags = [line.type if line.type != None else '' for line in flow.items]
        # make form
        form = tags_creator(len(flow.items))

        if 'tag_2' in request.form:
            if form.validate_on_submit():
                for tag, row in zip(form.tags, flow.items):
                    row.tag = tag.data['tag']
            db.session.commit()
            tags = [line.type if line.type != None else '' for line in flow.items]

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
        tags = [line.type if line.type != None else '' for line in flow.items]
        # make form
        form = tags_creator(len(flow.items))

        if 'tag_3' in request.form:
            if form.validate_on_submit():
                for tag, row in zip(form.tags, flow.items):
                    row.tag = tag.data['tag']
            db.session.commit()
            tags = [line.type if line.type != None else '' for line in flow.items]

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
        value=tags,
        )