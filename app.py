import os
# Install necessary libraries
os.system('pip install -r requirements.txt')

import os
from flask import Flask, render_template, request
from flask_httpauth import HTTPBasicAuth
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
import mysql.connector
from mysql.connector import Error
import logging
import nltk

nltk.download('stopwords')
nltk.download('punkt') 

from nltk.corpus import stopwords
import string
from nltk.stem import PorterStemmer

nltk.download('stopwords')

app = Flask(__name__)
auth = HTTPBasicAuth()

USERS = {'your_username': 'your_password'}  # Replace with your desired username and password

@auth.verify_password
def verify_password(username, password):
    return USERS.get(username) == password

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC


def load_models():
    try:
        data_processing = transform_text  
        vect = pickle.load(open('vect.pkl', 'rb'))
        svc = pickle.load(open('svc.pkl', 'rb'))
        return data_processing, vect, svc
    except Exception as e:
        logging.error(f"Error loading models: {e}")
        return None, None, None

def create_connection():
    try:
        host = os.environ.get('DB_HOST', 'host.docker.internal')
        user = os.environ.get('DB_USER', 'root')  # give your user
        password = os.environ.get('DB_PASSWORD', '1010') # give your password
        database = os.environ.get('DB_NAME', 'movie_review') # give your db name

        print(f"Connecting to MySQL: {user}@{host}/{database}")

        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        if connection.is_connected():
            logging.info("Connected to MySQL database")
            return connection, True
    except Error as e:
        logging.error(f"Error connecting to MySQL: {e}")
        return None, False


def close_connection(connection):
    if connection.is_connected():
        connection.close()
        logging.info("Connection closed")

def log_prediction(connection, text, prediction):
    try:
        cursor = connection.cursor()

        # Creating a table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                input_text TEXT,
                prediction_result VARCHAR(10)
            )
        """)

        # Convert prediction to "Positive" or "Negative"
        prediction = "Positive" if prediction == 1 else "Negative"

        # Insert prediction record
        cursor.execute("""
            INSERT INTO predictions (input_text, prediction_result)
            VALUES (%s, %s)
        """, (text, prediction))

        connection.commit()  # Commit the changes to the database
        logging.info("Prediction logged successfully")

    except Error as e:
        logging.error(f"Error logging prediction: {e}")

    finally:
        cursor.close()


def transform_text(text):
    if not text or not text.strip():
        return []  # Return an empty list if the input text is empty or contains only spaces

    text = text.lower()
    text = nltk.word_tokenize(text)

    y = []
    for i in text:
        if i.isalnum():
            y.append(i)

    text = y[:]
    y.clear()

    for i in text:
        if i not in stopwords.words('english') and i not in string.punctuation:
            y.append(i)

    text = y[:]
    y.clear()

    ps = PorterStemmer()
    return [ps.stem(i) for i in text]

@app.route('/', methods=['GET', 'POST'])
@auth.login_required  
def index():
    connection, connected = create_connection()

    if request.method == 'POST':
        data_processing, vect, svc = load_models()

        if any(model is None for model in [data_processing, vect, svc]):
            return render_template('index.html', connected=connected, prediction_error="Error loading models. Check if model files exist.")

        text = request.form['text']

        # Preprocess the input text using the custom transformation function
        processed_text = data_processing(text)

        if not processed_text:
            return render_template('index.html', connected=connected, prediction_error="Invalid input. Please enter a valid movie review.")

        vectorized_text = vect.transform([' '.join(processed_text)])

        # Make prediction using the SVM model
        prediction = svc.predict(vectorized_text)[0]

        # Log the prediction in MySQL database
        if connected:
            log_prediction(connection, text, prediction)

        sentiment = "Positive" if prediction == 1 else "Negative"

        return render_template('index.html', connected=connected, prediction=sentiment, input_text=text)

    return render_template('index.html', connected=connected)

@app.route('/predictions')
@auth.login_required  
def predictions():
    connection, connected = create_connection()

    if connected:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM predictions ORDER BY id DESC")
        predictions_data = cursor.fetchall()
        connection.close()

        return render_template('predictions.html', connected=connected, predictions=predictions_data)

    return render_template('predictions.html', connected=connected, predictions=None)

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True, host='0.0.0.0')
