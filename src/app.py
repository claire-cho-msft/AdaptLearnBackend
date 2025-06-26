from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "Hello, World!"

@app.route("/<doc>")
def document(doc):
    return f"{doc}"

if __name__ == "__main__":
    app.run()