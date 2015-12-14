from flask import render_template

from metrics_app import app


@app.route('/')
def index():
    return render_template('data_index.html')
