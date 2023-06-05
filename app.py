from flask import Flask, render_template, request, jsonify,redirect, url_for,flash
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import time
from gspread_formatting import CellFormat, format_cell_range
import datetime

app = Flask(__name__)
app.secret_key = "apontamentopintura"

@app.route('/', methods=['GET','POST'])
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

        table = table[['DATA DA CARGA','CODIGO', 'DESCRICAO', 'QT_ITENS', 'COR', 'PROD.']]
        
        values = table.values.tolist()

        return values , table
    
    if request.method == 'POST':
        filtro_data = request.form.get('filtro_data')
        filtro_cor = request.form.get('filtro_cor')

        hoje = datetime.datetime.today().strftime("%d/%m/%Y")

        sheet_data, table = get_sheet_data_gerar()

        if filtro_data == '':
            table = table[table['DATA DA CARGA'] == hoje]
            cores = table['COR'].drop_duplicates().values.tolist()

        else:
            filtro_data = datetime.datetime.strptime(filtro_data, "%Y-%m-%d").strftime("%d/%m/%Y")
            table = table[table['DATA DA CARGA'] == filtro_data]
        
            cores = table['COR'].drop_duplicates().values.tolist()

        if filtro_cor != 'Todas':
            table = table[table['COR'] == filtro_cor]
        else:
            pass 

        sheet_data = table.values.tolist()

        return render_template('gerar_cambao.html', sheet_data=sheet_data,cores=cores)

    sheet_data, table = get_sheet_data_gerar()

    hoje = datetime.datetime.today().strftime("%d/%m/%Y")

    table = table[table['DATA DA CARGA'] == hoje]
    cores = table['COR'].drop_duplicates().values.tolist()

    sheet_data = table.values.tolist()

    return render_template('gerar_cambao.html', sheet_data=sheet_data,cores=cores)

@app.route('/send_gerar', methods=['GET','POST'])
def gerar_planilha():

    dados = request.get_json()
    
    table_final = pd.DataFrame(dados)

    table_final['UNICO'] = ''

    table_final['SETOR'] = 'Pintura'

    table_final = table_final[table_final['prod'] != '']

    for i in range(len(table_final)):
        if table_final['tipo'][i] == '':
            table_final['tipo'][i] = 'PO'

    print(table_final)

    return 'Planilha gerada com sucesso!'

if __name__ == '__main__':
    app.run(debug=True)