from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = "supersecret"
CORS(app)  # ← to umożliwia połączenia z localhosta z poziomu JS w PHP

from app import routes


