from flask import Flask, render_template, request
from PIL import Image
import textwrap
from IPython.display import Markdown

import google.generativeai as genai

from flask import Flask, render_template, request, jsonify
from PIL import Image
import textwrap
import google.generativeai as genai


app = Flask(__name__)

genai.configure(api_key='AIzaSyCNcRduSwjtHmgAIlEZw9WjO5byORPsv64')
model = genai.GenerativeModel('gemini-pro-vision')

def to_markdown(text):
    text = text.replace('•', '  *')
    return textwrap.indent(text, '> ', predicate=lambda _: True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        description = request.form['description']
        prediction = predict(file, description)
        return render_template('index.html', prediction=prediction)
    else:
        return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    file = request.files['file']
    description = request.form['description']
    img = Image.open(file)
    # Use the provided description in the request
    response = model.generate_content([description, img], stream=True)
    response.resolve()
    prediction = to_markdown(response.text)
    return prediction

if __name__ == '__main__':
    app.run(debug=True)
