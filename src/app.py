"""Used to render the 'Meal Tracker' application"""

import time
import os
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError


app = Flask(__name__)

if os.getenv("ENV") == "testing":
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "mysql+pymysql://root:password@mysql-test/test_meals"
    )
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:password@mysql/meals"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Meal(db.Model):
    """Used to create a table that has 3 columns: an id as a primary key, 
    the description of a meal, and the rating of a meal."""

    __tablename__ = "meals"
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(1000))
    rating = db.Column(db.String(50))


def add_meal(description, rating):
    """Add a meal to the database"""
    new_meal = Meal(description=description, rating=rating)  # Missing rating here
    db.session.add(new_meal)
    db.session.commit()


@app.route("/", methods=["GET", "POST"])
def home():
    """Renders home page based on what meals  have been previously selected"""
    meal_list = Meal.query.all()
    # Rating options 
    ratings = ["Nasty", "Didn't really like it", "Okay", "Pretty Good", "DELICIOUS"]

    return render_template(
        "index.html",
        ratings=ratings,
        meal_list=meal_list,
    )


@app.route("/add", methods=["GET", "POST"])
def add():
    """Adds a food and rating to the database"""
    meal = request.form.get("meal")
    rating = request.form.get("rating")
    if meal and rating:
        add_meal(description=meal, rating=rating)
    return redirect("/")


@app.route("/delete/<int:id>", methods=["GET", "POST"])
def delete(id):
    """Deletes a meal from the stored meals"""
    meal = Meal.query.get(id)
    db.session.delete(meal)
    db.session.commit()
    return redirect("/")


if __name__ == "__main__":
    with app.app_context():
        for _ in range(10):
            try:
                with db.engine.connect() as connection:
                    connection.execute(db.text('SELECT 1'))
                break
            except OperationalError:
                print("Database not ready, retrying in 2s...")
                time.sleep(2)
        else:
            print("Could not connect to database after 5 tries. Exiting.")
            exit(1)

    app.run(host="0.0.0.0", port=5000, debug=True)
