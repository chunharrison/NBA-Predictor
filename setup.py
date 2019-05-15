from flask import Flask

app = Flask(__name__)

if __name__ == '__main__':
    from templates import app
    #Load this config object for development mode
    app.config.from_object('configurations.DevelopmentConfig')
    app.run()