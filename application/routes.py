from datetime import datetime, timedelta
import locale

from sqlalchemy import extract

from flask_login import login_required, current_user
from flask import render_template
from sqlalchemy.sql.expression import desc

from application.main.models import Balance, CreditStatement
from application import current_app as app, db

@app.route('/')
@app.route('/index')
@login_required
def index():

    # export LC_ALL="en_US.UTF-8"
    # export LC_CTYPE="en_US.UTF-8"
    # sudo dpkg-reconfigure locales 

    locale.setlocale(locale.LC_ALL, 'es_AR.UTF-8')

    bank_list = None
    last_bal = None

    bank_credit = None
    debt = None
        
    if Balance.query.all():
        bank_list = Balance.query.filter(Balance.user_id == current_user.id).with_entities(Balance.account_n, Balance.bank).distinct().all()
        last_bal = {}
        for bank in bank_list:
            bal = Balance.query.with_entities(Balance.bal).filter(Balance.bank == bank.bank).all()
            last_bal[bank.bank] = round(float(bal[-1][0]),2)

    query_statement = CreditStatement.query.order_by(CreditStatement.due_date.desc()).first()
    if query_statement:
        credit = query_statement
        print(query_statement.credit)


    app.logger.info('Entering')
    return render_template(
        "index.html", 
        banks = bank_list, 
        date=datetime.now().date().strftime("%A %w %b de %Y"), 
        last=last_bal,
        credit = credit
        )