#!/usr/bin/env python
from io import TextIOWrapper
import csv

from flask import Flask, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

# ruta absoluta d'aquesta carpeta
basedir = os.path.abspath(os.path.dirname(__file__)) 

# Create Flaskk app, config the db and load the db object
# http://flask-sqlalchemy.pocoo.org/2.1/quickstart/#a-minimal-application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + basedir + "/../database.db"
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)

    def __repr__(self):
        return "<User: {}>".format(self.username)


@app.route('/', methods=['GET', 'POST'])
def upload_csv():
    if request.method == 'POST':
        csv_file = request.files['file']
        csv_file = TextIOWrapper(csv_file, encoding='utf-8')
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            user = User(username=row[0], email=row[1])
            db.session.add(user)
            db.session.commit()
        return redirect(url_for('upload_csv'))
    return """
            <form method='post' action='/' enctype='multipart/form-data'>
              Upload a csv file: <input type='file' name='file'>
              <input type='submit' value='Upload'>
            </form>
           """

if __name__ == '__main__':
    db.create_all()
    app.run()