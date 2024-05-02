from flask import Flask, request
import textwrap
import google.generativeai as genai
from IPython.display import Markdown
import PIL.Image
import os 
from google.oauth2 import service_account

GOOGLE_API_KEY=os.getenv('apikey')
genai.configure(api_key=GOOGLE_API_KEY)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'key.json'
credentials = service_account.Credentials.from_service_account_file(
    'key.json', scopes=['https://www.googleapis.com/auth/cloud-platform']
)
def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))
app = Flask(__name__)

@app.route('/api/respond', methods=['GET', 'POST'])
def get_respond():
    if request.method == 'POST':
        Prompt = request.get_json()['prompt']
    else:
        Prompt = request.args.get('prompt')
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(Prompt, stream=True)
    response.resolve()
    return response.text

@app.route('/api/recommend', methods=['GET', 'POST'])
def get_recommend():
    if request.method == 'POST':
        Prompt = request.get_json()['prompt']
    else:
        Prompt = request.args.get('prompt')
    model = genai.GenerativeModel('gemini-pro-vision')
    img = PIL.Image.open(r'image\menu.jpeg')
    with open('prompt.txt', 'r') as f:
        text = f.read()
    response = model.generate_content([text+Prompt,img])
    response.resolve()
    return response.text

if __name__ == '__main__':
    app.run(debug=True)