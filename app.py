from flask import Flask, render_template, request, jsonify,redirect, url_for,flash, Blueprint
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import time
from gspread_formatting import CellFormat, format_cell_range
from finalizarcambao import finalizarcambao_bp
import datetime
import cachetools

app = Flask(__name__)
app.secret_key = "apontamentopintura"
app.register_blueprint(finalizarcambao_bp)

cache_get_sheet = cachetools.LRUCache(maxsize=128)
cache_tipos_tinta = cachetools.LRUCache(maxsize=128)
cache_producao_finalizada = cachetools.LRUCache(maxsize=128)


def resetar_cache(cache):

    """
    Função para limpar caches (não precisar fazer
    requisição sempre que atualizar a página).
    """
    cache.clear()


@cachetools.cached(cache_get_sheet)
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
    list1 = wks.get()
    cabecalho = wks.row_values(1)

    table = pd.DataFrame(list1)
    table = table.iloc[1:,:8]
    table = table.set_axis(cabecalho, axis=1)

    table = table.drop_duplicates()

    table = table.drop(table.index[0])

    table.reset_index(drop=True)

    table['PROD.'] = ''

    table['CAMBÃO'] = ''

    table = table[['DATA DA CARGA','CODIGO', 'DESCRICAO', 'QT_ITENS', 'COR', 'PROD.','CAMBÃO']]
        
    df_tipo = tiposTinta()
    tabela_quantidade_apontada = producao_finalizada()

    table = table.merge(df_tipo[['CODIGO','TIPO']], how='left', on='CODIGO').drop_duplicates()
    
    table['VALOR_UNICO'] = table['DATA DA CARGA'] + table['CODIGO']

    table = table.merge(tabela_quantidade_apontada[['VALOR_UNICO','QT APONT.']], how='left', on='VALOR_UNICO')
    
    table['QT APONT.'] = table['QT APONT.'].fillna(0).astype(int)
    table['QT_ITENS'] = table['QT_ITENS'].astype(int)
    
    table['restante'] = table['QT_ITENS'] - table['QT APONT.']

    table['QT_ITENS'] = table['restante']
    
    table = table[table['QT_ITENS'] > 0]

    values = table.values.tolist()

    return values , table


@cachetools.cached(cache_tipos_tinta)
def tiposTinta():
    
    scope = ['https://www.googleapis.com/auth/spreadsheets',
            "https://www.googleapis.com/auth/drive"]

    credentials = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
    sa = gspread.service_account('service_account.json')    

    name_sheet = 'BASE COM TIPO'
    worksheet = 'BASE COM TIPO'
    sh = sa.open(name_sheet)
    wks = sh.worksheet(worksheet)
    list1 = wks.get()
    cabecalho = wks.row_values(1)

    table = pd.DataFrame(list1)
    table = table.iloc[1:,:]
    table_com_tipo = table.set_axis(cabecalho, axis=1)

    return table_com_tipo


@cachetools.cached(cache_producao_finalizada)
def producao_finalizada():
    
    scope = ['https://www.googleapis.com/auth/spreadsheets',
            "https://www.googleapis.com/auth/drive"]

    credentials = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
    client = gspread.authorize(credentials)
    sa = gspread.service_account('service_account.json')    

    name_sheet = 'Base ordens de produçao finalizada'
    worksheet = 'Pintura'
    sh = sa.open(name_sheet)
    wks = sh.worksheet(worksheet)
    list1 = wks.get()
    cabecalho = wks.row_values(1)

    table = pd.DataFrame(list1)
    table = table.iloc[1:,:]
    table = table.set_axis(cabecalho, axis=1)
    
    table['QT APONT.'] = table['QT APONT.'].astype(int)
    table['QT PLAN.'] = table['QT PLAN.'].astype(int)

    tabela_quantidade_apontada = table.groupby(['DATA DA CARGA','CODIGO','COR']).sum()[['QT APONT.']].reset_index()
    tabela_quantidade_apontada['VALOR_UNICO'] = tabela_quantidade_apontada['DATA DA CARGA'] + tabela_quantidade_apontada['CODIGO']

    return tabela_quantidade_apontada


@app.route('/', methods=['GET','POST'])
def gerar_cambao():

    if request.method == 'POST':
        filtro_data = request.form.get('filtro_data')
        filtro_cor = request.form.get('filtro_cor')
        filtro_tipo = request.form.get('filtro_tipo')

        print(filtro_tipo)

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

        if filtro_tipo != 'Todos':
            table = table.loc[(table['TIPO'] == filtro_tipo) | (table['TIPO'] == 'PÓ,PU') | (table['TIPO'] == 'PU,PÓ')]
        else:
            pass 

        # if filtro_tipo == 'PU':
        #     table['QUANTIDADE PROD.'] = ''
        # else:
        #     table['QUANTIDADE PROD.'] = table['QT_ITENS']

        print(table)

        sheet_data = table.values.tolist()

        return render_template('gerar_cambao.html', sheet_data=sheet_data,cores=cores, filtro_tipo=filtro_tipo)

    sheet_data, table = get_sheet_data_gerar()

    hoje = datetime.datetime.today().strftime("%d/%m/%Y")

    table = table[table['DATA DA CARGA'] == hoje]
    table = table.fillna('')
    cores = table['COR'].drop_duplicates().values.tolist()

    sheet_data = table.values.tolist()

    filtro_tipo = None

    return render_template('gerar_cambao.html', sheet_data=sheet_data,cores=cores, filtro_tipo=filtro_tipo)


@app.route('/send_gerar', methods=['GET','POST'])
def gerar_planilha():

    dados = request.get_json()
    
    table_final = pd.DataFrame(dados)

    table_final['setor'] = 'Pintura'

    table_final['flag'] = ''

    table_final['flag'] = table_final['codigo'] + table_final['data'] + table_final['cambao']

    table_final['flag'] = table_final['flag'].replace('/','',regex=True)

    table_final['data finalizada'] = datetime.datetime.today().strftime("%d/%m/%Y")

    table_final = table_final[table_final['prod'] != '']

    table_final.reset_index(drop=True)

    for i in range(len(table_final)):
        try:
            if table_final['tipo'][i] == '':
                table_final['tipo'][i] = 'PÓ'
        except:
            pass

    table_final = table_final[['flag','codigo', 'descricao', 'qt_itens', 'cor', 'prod','cambao','tipo','data','data finalizada','setor']]

    table_final['prod'] = table_final['prod'].astype(int)
    try:
        table_final['cambao'] = table_final['cambao'].astype(int)
    except:
        pass
    
    table_final['qt_itens'] = table_final['qt_itens'].astype(int)

    lista_final = table_final.values.tolist()

    print(table_final)

    scope = ['https://www.googleapis.com/auth/spreadsheets',
                "https://www.googleapis.com/auth/drive"]

    credentials = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
    client = gspread.authorize(credentials)
    sa = gspread.service_account('service_account.json')    

    name_sheet = 'Base ordens de produçao finalizada'
    worksheet = 'Pintura'
    sh = sa.open(name_sheet)
    wks = sh.worksheet(worksheet)

    wks.append_rows(lista_final)

    resetar_cache(cache_get_sheet)
    resetar_cache(cache_tipos_tinta)
    resetar_cache(cache_producao_finalizada)

    return 'Planilha gerada com sucesso!'


@app.route('/limpar-caches', methods=['GET','POST'])
def limpar_caches():

    resetar_cache(cache_get_sheet)
    resetar_cache(cache_tipos_tinta)
    resetar_cache(cache_producao_finalizada)

    return redirect(url_for("gerar_cambao"))
    


if __name__ == '__main__':
    app.run(debug=True)