from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
import requests
import os

API_KEY = os.environ["API_KEY"]
IMG_URL = "https://image.tmdb.org/t/p/w500"
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
        rating = db.Column(db.Integer, nullable=True)
        ranking = db.Column(db.String(250), nullable=True)
        review = db.Column(db.String(250), nullable=True)
        img_url = db.Column(db.String(250), nullable=False)

    db.create_all()


class RateMovieForm(FlaskForm):
    update_rating = StringField("Your Rating Out of 10, e.g. 7.5")
    update_review = StringField("Your Review")
    submit = SubmitField('Done')


class AddMovie(FlaskForm):
    movie_title = StringField("Movie Title")
    submit = SubmitField("Add Movie")


@app.route("/")
def home():
    all_movies = db.session.query(Movies).order_by(Movies.rating.desc()).all()
    for movie in all_movies:
        movie.ranking = all_movies.index(movie)+1
    return render_template("index.html", movies=all_movies)


@app.route("/update", methods=["GET", "POST"])
def update():
    form = RateMovieForm()
    mov_id = request.args.get("id")
    mov_obj = Movies.query.get(mov_id)
    mov_tit = mov_obj.title
    if form.validate_on_submit():
        movie_id = request.args.get("id")
        movie_to_update = Movies.query.get(movie_id)
        movie_to_update.review = form.update_review.data
        movie_to_update.rating = form.update_rating.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", form=form, name=mov_tit)


@app.route('/delete')
def delete():
    movie_id = request.args.get("id")
    movie_delete = Movies.query.get(movie_id)
    db.session.delete(movie_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/add', methods=["GET", "POST"])
def add():
    form = AddMovie()
    if form.validate_on_submit():
        parameters = {
            "api_key": API_KEY,
            "language": "en-CA",
            "query": form.movie_title.data,
        }
        response = requests.get("https://api.themoviedb.org/3/search/movie?", params=parameters)
        response.raise_for_status()
        movie_list = response.json()["results"]
        return render_template('select.html', movie_list=movie_list)
    return render_template('add.html', form=form)


@app.route('/new')
def new():
    movie_id = request.args.get("id")
    params = {
        "api_key": API_KEY,
        "language": "en-CA",
    }
    response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?", params=params)
    response.raise_for_status()
    movie_desc = response.json()
    new_movie = Movies(title=movie_desc["original_title"],
                       year=movie_desc["release_date"][:4],
                       description=movie_desc["overview"],
                       img_url=f"{IMG_URL}{movie_desc['poster_path']}"
                       )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for("update", id=new_movie.id))


if __name__ == '__main__':
    app.run(debug=True)
