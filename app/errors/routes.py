from . import errors_bp
from flask import url_for
from flask import redirect
from flask import render_template

@errors_bp.app_errorhandler(401)
def error_401(error):

    return redirect(url_for('public.index'))