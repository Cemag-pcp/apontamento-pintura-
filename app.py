from flask import Flask, render_template, request, jsonify,redirect, url_for,flash
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import time
from gspread_formatting import CellFormat, format_cell_range

app = Flask(__name__)
app.secret_key = "apontamentopintura"

@app.route('/')
def gerar_cambao():

    def get_sheet_data_gerar():

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

        table = table.drop(table.index[0])

        table.reset_index(drop=True)

        table['PROD.'] = ''

        table['CAMBÃO'] = ''

        table['TIPO'] = ''

        table = table[['CODIGO', 'DESCRICAO', 'QT_ITENS', 'COR', 'PROD.']]

        values = table.values.tolist()

        return values , table
    
    sheet_data, table = get_sheet_data_gerar()

    print(table)

    return render_template('gerar_cambao.html', sheet_data=sheet_data)

@app.route('/finalizarcambao')
def finalizar_cambao():
    
    scope = ['https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive"]
    
    credentials = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
    client = gspread.authorize(credentials)
    sa = gspread.service_account('service_account.json')    

    name_sheet1 = 'Base ordens de produçao finalizada'
    worksheet1 = 'Pintura'
    sh1 = sa.open(name_sheet1)
    wks1 = sh1.worksheet(worksheet1)
    list2 = wks1.get_all_records()
    table1 = pd.DataFrame(list2)
    return render_template('finalizar_cambao.html')

if __name__ == '__main__':
    app.run(debug=True)