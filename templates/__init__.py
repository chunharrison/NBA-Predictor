from flask import Flask

app = Flask(__name__,
    static_folder = './public',
    template_folder="./static")

from templates.home.views import home_blueprint
from templates.predictions.views import predictions_blueprint
from templates.actual.views import actual_blueprint
# register the blueprints
app.register_blueprint(home_blueprint)
app.register_blueprint(predictions_blueprint)
app.register_blueprint(actual_blueprint)
