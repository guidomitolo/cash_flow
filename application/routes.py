from datetime import datetime
import locale

from flask_login import login_required, current_user
from flask import render_template

from .models import Account
from application import current_app as app

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
        
    if Account.query.all():
        bank_list = Account.query.filter(Account.user_id == current_user.id).with_entities(Account.account_n, Account.bank).distinct().all()
        last_bal = {}
        for bank in bank_list:
            bal = Account.query.with_entities(Account.bal).filter(Account.bank == bank.bank).all()
            last_bal[bank.bank] = round(float(bal[-1][0]),2)

    app.logger.info('Entering')
    return render_template("index.html", banks = bank_list, date=datetime.now().date().strftime("%A %w %b de %Y"), last=last_bal)