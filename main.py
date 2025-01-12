import json
import logging
import os
from flask import Flask, url_for, request, session, Response
from gunicorn.app.base import BaseApplication
from routes import routes as routes_blueprint
from authentication import auth, auth_required
from models import db, User
from abilities import apply_sqlite_migrations, llm

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__, static_folder='static')
    app.secret_key = 'supersecretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'
    db.init_app(app)

    with app.app_context():
        apply_sqlite_migrations(db.engine, db.Model, 'migrations')

    app.register_blueprint(routes_blueprint)
    app.register_blueprint(auth)

    # Set up authentication only for protected routes
    app.before_request(auth_required(['routes.home_logged_in_route', 'routes.home_logged_in_route'])())

    @app.after_request
    def create_or_update_user(response):
        if 'user' in session and 'user_email' in session['user']:
            email = session['user']['user_email']
            profile_picture = session['user'].get('photo_url')
            with app.app_context():
                user = User.query.filter_by(email=email).first()
                if not user:
                    new_user = User(email=email, profile_picture=profile_picture)
                    db.session.add(new_user)
                    db.session.commit()
                    logging.info(f"Created new user: {email}")
                elif user.profile_picture != profile_picture:
                    user.profile_picture = profile_picture
                    db.session.commit()
                    logging.info(f"Updated profile picture for user: {email}")
        return response
    
    @app.route('/api/humanize', methods=['POST'])
    def humanize_text():
        data = request.get_json()
        original_text = data.get('text', '')
        text_type = data.get('text_type', 'standard')
        
        # Prepare the prompt
        prompt = """You are an expert AI assistant specializing in humanizing and improving German-language texts...
        
        Here is the original German text you need to humanize:
        
        <original_text>
        {original_text}
        </original_text>
        
        The type of text you are working with is:
        
        <text_type>
        {text_type}
        </text_type>
        """.format(original_text=original_text, text_type=text_type)
        
        # Define response schema
        response_schema = {
            'type': 'object',
            'properties': {
                'humanized_text': {'type': 'string'},
                'humanization_strategy': {'type': 'string'},
                'explanation': {'type': 'string'}
            },
            'required': ['humanized_text', 'humanization_strategy', 'explanation']
        }
        
        # Call LLM
        try:
            response = llm(
                prompt=prompt,
                response_schema=response_schema,
                image_url=None,
                model='claude-3-5-sonnet',
                temperature=0.7
            )
            
            # Stream the response back to the client
            def generate():
                yield 'data: ' + json.dumps(response) + '\n\n'
            
            return Response(generate(), mimetype='text/event-stream')
        except Exception as e:
            logging.error(f"Error calling LLM: {str(e)}")
            return {'error': 'Failed to process text'}, 500
    
    return app

app = create_app()

class StandaloneApplication(BaseApplication):
    def __init__(self, app, options=None):
        self.application = app
        self.options = options or {}
        super().__init__()

    def load_config(self):
        # Apply configuration to Gunicorn
        for key, value in self.options.items():
            if key in self.cfg.settings and value is not None:
                self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

if __name__ == "__main__":
    options = {
        "bind": "0.0.0.0:8080",
        "loglevel": "info",
        "accesslog": "-",
        "timeout": 120,
        "preload": True,
        "workers": 2,
        "worker_class": "gthread",
        "threads": 10,
        "max_requests": 300,
        "max_requests_jitter": 50
    }
    StandaloneApplication(app, options).run()