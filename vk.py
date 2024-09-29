from flask import Flask, request, render_template,url_for,request,jsonify, redirect,session

import pickle
import time
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 2 for only displaying error messages
from flask_cors import cross_origin
import tensorflow as tf
import firebase_admin 
from firebase_admin import credentials, auth


cred = credentials.Certificate(r"C:\MLProject\twitter-db-3b276-firebase-adminsdk-gn0k2-9b45172f31.json")
firebase_admin.initialize_app(cred)


app = Flask(__name__, template_folder="templates")


# Load the modeln
model = pickle.load(open('twitter_sentiment.pkl', 'rb'))

print("Model Loaded")


# sign up page for
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth.create_user(email=email, password=password)
            if user:
                return redirect(url_for('login'))
        except Exception as e:
            return render_template('signup.html', error='User already exist')
    return render_template('signup.html')
# login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth.get_user_by_email(email)
            if user:
                auth_user = auth.sign_in_with_email_and_password(email, password)
                session['user'] = auth_user['idToken']
                return redirect(url_for('/'))
        except Exception as e:
            return render_template('index.html', error='Invalid email or password')
    return render_template('login.html')

# Mapping between sentiment labels and emojis
sentiment_emoji = {
    "positive": "😃",
    "negative": "😠",
    "neutral": "😐"
}


@app.route('/', endpoint='home')
def home():
	return render_template("index.html")


@app.route("/predict", methods=['GET', 'POST'], endpoint='predict')
@cross_origin()
def predict():
    if request.method == 'POST':
        tweet = request.form['tweet']
        start = time.time()
        prediction = "positive"
        prediction = model.predict([tweet])  # Pass tweet as a list
        end = time.time()
        prediction_time = round(end - start, 2)
        return render_template('resulty.html', prediction=prediction[0], prediction_time=prediction_time, sentiment_emoji=sentiment_emoji)

    elif request.method == 'GET':
        return render_template('predict.html')  # Return a form for GET requests

if __name__ == '__main__':
    app.run(debug=True)