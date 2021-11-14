from flask.helpers import flash
from . import errors_bp
from flask import url_for
from flask import redirect
from flask import render_template

@errors_bp.app_errorhandler(401)
def error_401(error):

    return redirect(url_for('public.index'))


@errors_bp.errorhandler(404)
def resource_not_found(e):

    flash("Tenemos errores en este momento", "error")

    return redirect(url_for('public.index'), code=404)