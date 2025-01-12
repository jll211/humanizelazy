from flask import render_template, session, Blueprint, redirect, url_for, make_response
from functools import wraps

routes = Blueprint('routes', __name__)

def with_sidebar(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return render_template(f.__name__.replace('_route', '.html'), with_sidebar=True)
    return decorated_function

@routes.route("/")
def landing_route():
    return render_template("landing.html", with_sidebar=False)

@routes.route("/home_logged_in")
def home_logged_in_route():
    return render_template("home_logged_in.html", with_sidebar=True)