from flask import Flask, render_template, request, jsonify,redirect, url_for,flash, Blueprint
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import time
from gspread_formatting import CellFormat, format_cell_range
from datetime import datetime

finalizarcambao_bp = Blueprint('finalizarcambao', __name__)

def planilha_finalizar_cambao():
    
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
    
    table1 = table1[table1['STATUS'] == '']
    table1 = table1[['CODIGO', 'PEÇA', 'COR', 'QT APONT.', 'CAMBÃO', 'TIPO', 'DATA DA CARGA', 'id']]

    table1_list = table1.values.tolist()

    return(table1_list, table1)

def att_dados(lista_id):

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
    
    table1 = table1[table1['STATUS'] == '']
    table1 = table1[['CODIGO', 'PEÇA', 'COR', 'QT APONT.', 'CAMBÃO', 'TIPO', 'DATA DA CARGA', 'id']]

    lista_id = list(map(int, lista_id))
    
    for id in lista_id:
        wks1.update("L" + str(id + 1), 'OK')

@finalizarcambao_bp.route('/finalizar-cambao', methods=['GET','POST'])
def finalizar_cambao():

    if request.method == 'POST':

        data_filter = request.form.get('data_filter')

        if data_filter == '':
            table, table1 = planilha_finalizar_cambao()
        else:
            data_filter = datetime.strptime(data_filter, "%Y-%m-%d").strftime("%d/%m/%Y")
            
            table, table1 = planilha_finalizar_cambao()
            table = table1[table1['DATA DA CARGA'] == data_filter].values.tolist()

        return render_template("finalizar_cambao.html", table=table)

    table, table1 = planilha_finalizar_cambao()

    return render_template("finalizar_cambao.html", table=table)

@finalizarcambao_bp.route('/tratar_dados', methods=['POST','GET'])
def tratar_dados():

    # Obtém os dados enviados na requisição
    table_data = request.get_json()

    df = pd.DataFrame(table_data)

    df = df[df['status'] != '']
    
    print(df)

    lista_id = df['id'].values.tolist() 

    print(lista_id)

    att_dados(lista_id)

    return jsonify({"message": "Dados recebidos com sucesso"})
