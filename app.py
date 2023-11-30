# Import library for ReGex, SQLite, and Pandas
import re
import sqlite3
import pandas as pd

# Import library for Flask
from flask import Flask, jsonify
from flask import request
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from

# Define Swagger UI description
app = Flask(__name__)
app.json_encoder = LazyJSONEncoder
# swagger_template = dict(
# info = {
#     'title': LazyString(lambda: 'API Documentation for Data Processing and Modeling'),
#     'version': LazyString(lambda: '1.0.0'),
#     'description': LazyString(lambda: 'Dokumentasi API untuk Data Processing dan Modeling'),
#     },
#     host = LazyString(lambda: request.host)
# )
swagger_template = {
    'info' : {
        'title': 'API Documentation for Data Processing and Modeling',
        'version': '1.0.0',
        'description': 'Dokumentasi API untuk Data Processing dan Modeling',
        },
    'host' : '127.0.0.1:5000'
}
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'docs',
            "route": '/docs.json',
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}
swagger = Swagger(app, template=swagger_template,             
                  config=swagger_config)

# buka koneksi sqlite
conn = sqlite3.connect('data/gold_challenge.db', check_same_thread=False)

# membuat table
# buat kolom text dan text_clean dengan tipe data varchar
conn.execute('''CREATE TABLE IF NOT EXISTS data (text varchar(255), text_clean varchar(255));''')

# membuat endpoint pertama text-processing
@swag_from("docs/text_processing.yml", methods=['POST'])
@app.route('/text-processing', methods=['POST'])
def text_processing():

    # ambil text
    text = request.form.get('text')
    
    # proses cleansing menggunakan regex
    text_clean = re.sub(r'[^a-zA-Z0-9]', ' ', text)

    # input hasil cleansing ke database
    conn.execute("INSERT INTO data (text, text_clean) VALUES (?, ?)", (text, text_clean))
    conn.commit()

    # response akhir API berbentuk json
    json_response = {
        'status_code': 200,
        'description': "Teks yang sudah diproses",
        'data': text_clean,
    }
    response_data = jsonify(json_response)
    return response_data

# Buat endpoint untuk "upload file CSV"
@swag_from("docs/text_processing_file.yml", methods=['POST'])
@app.route('/text-processing-file', methods=['POST'])
def text_processing_file():

    # upload file
    file = request.files.getlist('file')[0]

    # import file kemudian jadikan dataframe menggunakan pandas
    df = pd.read_csv(file, encoding="latin-1")

    # ambil kolom teks dari file dalam format list
    # texts = df.text.to_list()
    texts = df['Tweet'].to_list()

    # looping list text nya
    cleaned_text = []
    for original_text in texts:

        # proses cleansing data
        text_clean = re.sub(r'[^a-zA-Z0-9]', ' ', original_text) # ditambahin cleansing ini.

        # input hasil cleansing ke database
        conn.execute("INSERT INTO data (text, text_clean) VALUES (?, ?)", (original_text, text_clean))
        conn.commit()

        # tambahkan list output di variable text_clean ke dalam kolom database kolom text_clean
        cleaned_text.append(text_clean)
    
    # response API berbentuk json
    json_response = {
        'status_code': 200,
        'description': "Teks yang sudah diproses",
        'data': cleaned_text,
    }
    response_data = jsonify(json_response)
    return response_data

if __name__ == '__main__':
   app.run()