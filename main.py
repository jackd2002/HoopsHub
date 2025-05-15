import os
from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-key-for-dev')
db = SQLAlchemy(app)


MVP_LIST = {
    1955: "Bob Pettit", 1956: "Bob Pettit", 1957: "Bob Cousy", 1958: "Bill Russell",
    1959: "Bob Pettit", 1960: "Wilt Chamberlain", 1961: "Bill Russell", 1962: "Bill Russell",
    1963: "Bill Russell", 1964: "Oscar Robertson", 1965: "Bill Russell", 1966: "Wilt Chamberlain",
    1967: "Wilt Chamberlain", 1968: "Wilt Chamberlain", 1969: "Wes Unseld", 1970: "Willis Reed",
    1971: "Kareem Abdul-Jabbar", 1972: "Kareem Abdul-Jabbar", 1973: "Dave Cowens",
    1974: "Kareem Abdul-Jabbar", 1975: "Bob McAdoo", 1976: "Kareem Abdul-Jabbar",
    1977: "Kareem Abdul-Jabbar", 1978: "Bill Walton", 1979: "Moses Malone", 1980: "Kareem Abdul-Jabbar",
    1981: "Julius Erving", 1982: "Moses Malone", 1983: "Moses Malone", 1984: "Larry Bird",
    1985: "Larry Bird", 1986: "Larry Bird", 1987: "Magic Johnson", 1988: "Michael Jordan",
    1989: "Magic Johnson", 1990: "Magic Johnson", 1991: "Michael Jordan", 1992: "Michael Jordan",
    1993: "Charles Barkley", 1994: "Hakeem Olajuwon", 1995: "David Robinson", 1996: "Michael Jordan",
    1997: "Karl Malone", 1998: "Michael Jordan", 1999: "Karl Malone", 2000: "Shaquille O'Neal",
    2001: "Allen Iverson", 2002: "Tim Duncan", 2003: "Tim Duncan", 2004: "Kevin Garnett",
    2005: "Steve Nash", 2006: "Steve Nash", 2007: "Dirk Nowitzki", 2008: "Kobe Bryant",
    2009: "LeBron James", 2010: "LeBron James", 2011: "Derrick Rose", 2012: "LeBron James",
    2013: "LeBron James", 2014: "Kevin Durant", 2015: "Stephen Curry", 2016: "Stephen Curry",
    2017: "Russell Westbrook", 2018: "James Harden", 2019: "Giannis Antetokounmpo",
    2020: "Giannis Antetokounmpo", 2021: "Nikola Jokic", 2022: "Nikola Jokic",
    2023: "Joel Embiid", 2024: "Nikola Jokic", 2025: ""
}

class MVPForm(FlaskForm):
    name = StringField("Enter MVP Name", validators=[DataRequired()])
    submit = SubmitField("Submit")




@app.route('/')
def index():
    espn_news_url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/news"
    response = requests.get(espn_news_url)
    news_data = response.json().get('articles', [])

    # Get headline, description, image & link
    news_items = []
    for article in news_data:
        news_items.append({
            'headline': article.get('headline'),
            'description': article.get('description'),
            'image': article.get('images', [{}])[0].get('url'),
            'link': article.get('links', {}).get('web', {}).get('href')
        })

    return render_template('index.html', news_items=news_items)











@app.route('/mvp', methods=['GET', 'POST'])
def mvps():
    form = MVPForm()
    if 'guesses' not in session:
        session['guesses'] = []

    last_guess = None

    if form.validate_on_submit():
        guess = form.name.data.strip().lower()
        matched = False
        for player in set(MVP_LIST.values()):
            if player.lower() == guess:
                matched = True
                if player not in session['guesses']:
                    session['guesses'].append(player)
                    last_guess = player.lower()
        session.modified = True
        # Redirect to avoid form resubmission
        return redirect(url_for('mvps'))

    display_data = []
    for year in range(1955, 2026):
        player_name = MVP_LIST.get(year, "")
        highlight = player_name in session['guesses']
        display_data.append((year, player_name if highlight else "", player_name))

    # Pass the guesses list (lowercase) for JS validation
    guesses_lower = [g.lower() for g in session['guesses']]
    valid_names = list(set(MVP_LIST.values()))

    return render_template('mvps.html',
                           form=form,
                           display_data=display_data,
                           last_guess=last_guess,
                           guesses=guesses_lower,
                           MVP_LIST=valid_names)

@app.route('/reset')
def reset():
    session.pop('guesses', None)
    return redirect(url_for('mvps'))

if __name__ == '__main__':
    app.run(debug=True)


class FanVoteForm(FlaskForm):
    name = StringField("Your Name", validators=[DataRequired()])
    mvp = StringField("MVP Pick", validators=[DataRequired()])
    coy = StringField("Coach of the Year", validators=[DataRequired()])
    roy = StringField("Rookie of the Year", validators=[DataRequired()])
    submit = SubmitField("Submit Vote")


class FanVote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    mvp = db.Column(db.String(100), nullable=False)
    coy = db.Column(db.String(100), nullable=False)
    roy = db.Column(db.String(100), nullable=False)




@app.route('/fan-voting', methods=['GET', 'POST'])
def fan_voting():
    form = FanVoteForm()
    if form.validate_on_submit():
        vote = FanVote(
            name=form.name.data,
            mvp=form.mvp.data,
            coy=form.coy.data,
            roy=form.roy.data
        )
        db.session.add(vote)
        db.session.commit()
        flash(f"Thanks for voting, {form.name.data}!", "success")
        return redirect(url_for('fan_voting'))
    return render_template('fan_voting.html', form=form)
