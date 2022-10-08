from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///all-time-movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

with app.app_context():
    class Movies(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(250), unique=True, nullable=False)
        year = db.Column(db.String(4), nullable=False)
        description = db.Column(db.String(250), nullable=False)
        rating = db.Column(db.String(250), nullable=False)
        ranking = db.Column(db.String(250), nullable=False)
        review = db.Column(db.String(250), nullable=False)
        img_url = db.Column(db.String(250), nullable=False)

    db.create_all()
    # new_movie = Movies(
    #     title="Phone Booth",
    #     year=2002,
    #     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an"
    #                 "extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation "
    #                 "with the caller leads to a jaw-dropping climax.",
    #     rating=7.3,
    #     ranking=10,
    #     review="My favourite character was the caller.",
    #     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
    # )
    # db.session.add(new_movie)
    # db.session.commit()


class RateMovieForm(FlaskForm):
    update_rating = StringField("Your Rating Out of 10, e.g. 7.5")
    update_review = StringField("Your Review")
    submit = SubmitField('Done')


@app.route("/")
def home():
    all_movies = db.session.query(Movies).all()
    return render_template("index.html", movies=all_movies)


@app.route("/update/<id>", methods=["GET", "POST"])
def update(id):
    form = RateMovieForm()
    if form.validate_on_submit():
        print(True)
        movie_to_update = Movies.query.filter_by(id=id).first()
        movie_to_update.review = form.update_review.data
        movie_to_update.rating = form.update_rating.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", form=form, id=id)


if __name__ == '__main__':
    app.run(debug=True)
