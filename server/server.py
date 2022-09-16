from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return """"""

@app.route("/list_of_points.txt")
def points():
    return "0 0 0"

if __name__ == "__main__":
    app.run(debug=True)