from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>System Test Successful: High-Frequency Bot Server is Live! 🚀</h1>"

if __name__ == '__main__':
    # AWS ke liye host '0.0.0.0' aur port 8080 hona zaroori hai
    app.run(host='0.0.0.0', port=8080)
