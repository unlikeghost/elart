from flask.helpers import flash
from . import errors_bp
from flask import url_for
from flask import redirect

@errors_bp.app_errorhandler(401)
def error_401(error):

    return redirect(url_for('public.index'))


@errors_bp.app_errorhandler(404)
def error_404(e):

    flash("Tenemos errores en este momento", "error")

    return redirect(url_for('public.index'))