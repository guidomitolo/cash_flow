from application.models import User
from application.auth.forms import LoginForm, RegistrationForm
from application.auth import bp
from application import login_manager, db

from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, login_required, current_user

from werkzeug.urls import url_parse

import logging

logger = logging.getLogger(__name__)

@bp.route('/login', methods=["GET","POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(username=form.username.data).first()        

        if user is None or not user.check_password(form.password.data):
            flash('Username/password inválidos')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)

        # if any, capture url with 'next' arg
        next_page = request.args.get('next')

        # if not 'next' redirect nonetheless to index
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')

        return redirect(next_page)
    
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Te has deslogueado")
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        user.set_password(form.password.data)

        login_user(user)
        logger.info('Nuevo usuario registrado!')

        next_page = request.args.get('next')

        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    return render_template('auth/register.html', title='Register', form=form)