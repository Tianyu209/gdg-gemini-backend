from flask import Flask, request, jsonify
import textwrap
import google.generativeai as genai
from IPython.display import Markdown
import os 
from google.oauth2 import service_account
import cv2
import base64
from PIL import Image
import numpy as np
import io 
GOOGLE_API_KEY=os.getenv('api')
genai.configure(api_key=GOOGLE_API_KEY)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'key.json'
credentials = service_account.Credentials.from_service_account_file(
    'key.json', scopes=['https://www.googleapis.com/auth/cloud-platform']
)
model = genai.GenerativeModel('gemini-pro-vision') 
chat = model.start_chat(history=[])

def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))
app = Flask(__name__)

def base642img(base64_string):
    imgdata = base64.b64decode(str(base64_string))
    img = Image.open(io.BytesIO(imgdata))
    opencv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    cv2.imwrite('output.jpg', opencv_img)
    return

@app.route('/api/respond', methods=['GET', 'POST'])
def get_respond():
    if request.method == 'POST':
        Prompt = request.get_json()['prompt']
    else:
        Prompt = request.args.get('prompt')
        
    response = chat.send_message(Prompt, stream=True,generation_config=genai.types.GenerationConfig(
        candidate_count=1,
        max_output_tokens=50,
        temperature=1.0))
    response.resolve()
    new = jsonify(response.text)
    new.headers.add('Access-Control-Allow-Origin','http://localhost:3000')
    return new

@app.route('/api/recommend', methods=['GET', 'POST'])
def get_recommend():
    base64_string = request.args.get('base64')
    #img = base642img(base64_string)
    if request.method == 'POST':
        Prompt = request.get_json()['prompt']
    else:
        Prompt = request.args.get('prompt')
    img = Image.open(r'output.jpg')
    with open('prompt.txt', 'r') as f:
        text = f.read()
    #chat.send_message(text+Prompt,stream=True)
    response = chat.generate_content([text+Prompt,img],generation_config=genai.types.GenerationConfig(
        candidate_count=1,
        max_output_tokens=50,
        temperature=1.0))
    response.resolve()
    new = jsonify(response.text)
    new.headers.add('Access-Control-Allow-Origin','http://localhost:3000')
    return new

if __name__ == '__main__':
    app.run(debug=True)