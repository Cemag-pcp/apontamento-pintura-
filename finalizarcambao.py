from flask import Flask, render_template, request, jsonify,redirect, url_for,flash
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import time
from gspread_formatting import CellFormat, format_cell_range
from app import app

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
    table1 = table1.values.tolist()

    return(table1)

@app.route('/finalizar-cambao')
def outra_rota():

    table = planilha_finalizar_cambao()



    return render_template("finalizar_cambao.html", table=table)