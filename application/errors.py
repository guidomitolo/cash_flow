from flask import render_template
from application import current_app as app
from application import db

@app.errorhandler(404)
def not_found_error(error):
    app.logger.error('Not found Error.')
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    app.logger.error('Database Error.')
    return render_template('500.html'), 500