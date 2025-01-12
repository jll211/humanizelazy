from functools import wraps
from flask import request, Blueprint, session, redirect, url_for
from abilities import flask_app_authenticator

auth = Blueprint('auth', __name__)

def auth_required(protected_routes=[]):
    def decorator():
        def decorated_view():
            if request.endpoint not in protected_routes or request.endpoint == 'static':
                return None
            return flask_app_authenticator(
                allowed_domains=None,
                allowed_users=None,
                logo_path=None,
                app_title="My App",
                custom_styles={
                    "global": "font-family: 'Manrope', sans-serif; background-color: #F9F9F9;",
                    "card": "border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.04); background-color: white; padding: 2rem;",
                    "logo": "max-width: 200px; height: auto;",
                    "title": "font-size: 2.5rem; font-weight: 700; color: #2C3639; margin-bottom: 1rem;",
                    "input": "border-radius: 10px; border: 1px solid rgba(0,0,0,0.05); padding: 0.8rem 1rem; width: 100%; margin-bottom: 1rem;",
                    "button": "background-color: #A27B5C; color: white; border-radius: 10px; padding: 0.8rem 1.5rem; width: 100%; font-weight: 500; transition: all 0.3s ease; border: none; cursor: pointer; margin-bottom: 1rem;",
                    "google_button": "background-color: white; color: #2C3639; border: 1px solid rgba(0,0,0,0.05); border-radius: 10px; padding: 0.8rem 1.5rem; width: 100%; font-weight: 500; transition: all 0.3s ease; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 0.5rem;"
                },
                session_expiry=None
            )()
        return decorated_view
    return decorator

@auth.route("/logout", methods=['POST'])
def logout_route():
    session.clear()
    return redirect(url_for('routes.landing_route'))