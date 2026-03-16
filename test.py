import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    # Maine emoji hata diya hai taaki Linux par koi encoding error na aaye
    return "<h1>Flask Test Successful! PIP and Python are working perfectly!</h1>"

if __name__ == '__main__':
    # Yeh line AWS se directly correct port utha legi
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
