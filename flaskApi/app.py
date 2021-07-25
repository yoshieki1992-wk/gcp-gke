from flask import Flask, request, jsonify
import math 
import os

app = Flask(__name__)

@app.route("/")
def default():
    return ""

@app.route("/greetings")
def greetings_function():
    return "Hello World from "+os.environ['HOSTNAME']

@app.route("/square",methods=["POST"])
def square_function():
    num = request.form.get('number', type=int)
    return jsonify({'resultado': math.sqrt(num)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
