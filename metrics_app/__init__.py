"""
Initalize Flask App
"""
from flask import Flask
from flask.ext.script import Manager

app = Flask(__name__)
manager = Manager(app)

import views
import metrics_collector


@manager.command
def metricsrunner():
    metrics_collector.main()
