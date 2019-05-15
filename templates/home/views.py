from flask import render_template, Blueprint

# crate a blueprint for prediction page
home_blueprint = Blueprint('home', __name__)

@home_blueprint.route('/')
def index():
    return render_template("index.html")
