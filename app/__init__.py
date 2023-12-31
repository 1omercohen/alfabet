from flask import Flask
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from app.models import User

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:admin@localhost:5432/alfabet'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'secret'

    from app.models import db
    db.init_app(app)

    jwt = JWTManager(app)

    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return user.id

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        user_id = jwt_data["identity"]
        return User.query.get(user_id)

    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    swagger = Swagger(app=app, template_file="openapi.yml", config={
        "headers": [
        ],
        "specs": [
            {
                "endpoint": "/openapi",
                "route": '/{}.yml'.format("openapi"),
                "rule_filter": lambda rule: True,  # all in
                "model_filter": lambda tag: True,  # all in
            }
        ],
        "static_url_path": "/flasgger_static",
        # "static_folder": "static",  # must be set by user
        "swagger_ui": True,
        "specs_route": "/docs/"
    })

    return app
