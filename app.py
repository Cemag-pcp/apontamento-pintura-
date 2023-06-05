from flask import Flask, render_template, request, jsonify,redirect, url_for,flash, Blueprint
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import time
from gspread_formatting import CellFormat, format_cell_range
from finalizarcambao import finalizarcambao_bp

app = Flask(__name__)
app.secret_key = "apontamentopintura"

app.register_blueprint(finalizarcambao_bp)

@app.route('/')
def gerar_cambao():

    scope = ['https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive"]
    
    credentials = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
    client = gspread.authorize(credentials)
    sa = gspread.service_account('service_account.json')    

    name_sheet = 'Base gerador de ordem de producao'
    worksheet = 'Pintura'
    sh = sa.open(name_sheet)
    wks = sh.worksheet(worksheet)
    list1 = wks.get_all_records()
    table = pd.DataFrame(list1)
    table = table.drop_duplicates()

    return render_template('gerar_cambao.html')

if __name__ == '__main__':
    app.run(debug=True)