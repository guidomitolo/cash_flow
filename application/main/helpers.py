from openpyxl import load_workbook
from datetime import datetime as dt
import datetime
import re
import json
import os

from application import current_app as app
from application import db
from flask_login import current_user
from application.models import Account

def check_db(data_input):

    query = Account.query.all()
    all_db = [[line.bank, line.account_n, line.timestamp, line.detail ,line.flow, line.bal] for line in query]

    data_submitted = []

    for row_data in data_input[::-1]:
        if all_db:
            if row_data in all_db:
                pass
            else:
                account = Account(bank= row_data[0],
                    account_n= row_data[1],
                    timestamp =  row_data[2],
                    detail =  row_data[3],
                    flow =  row_data[4],
                    bal= row_data[5],
                    user_id= current_user.id
                )
                db.session.add(account)
                data_submitted.append([row_data[0],
                    row_data[1],
                    row_data[2].date(),
                    row_data[3],
                    row_data[4],
                    row_data[5]]
                )
        else:
            account = Account(bank= row_data[0],
                account_n= row_data[1],
                timestamp =  row_data[2],
                detail =  row_data[3],
                flow =  row_data[4],
                bal= row_data[5],
                user_id= current_user.id
            )
            db.session.add(account)
            data_submitted.append([row_data[0],
                row_data[1],
                row_data[2].date(),
                row_data[3],
                row_data[4],
                row_data[5]]
            )
    db.session.commit()
    return data_submitted

def read_data(loaded_file):

    workbook = load_workbook(filename=loaded_file, data_only=True)
    sheet = workbook.active
    print(f'Sheet Total Rows: {sheet.max_row}\nSheet Total Columns: {sheet.max_column}')

    # patterns and regex
    p_account = "cuenta(?= única|:)"
    p_account_num = "\d+-+\d+/+\d"
    regex_account = re.compile(p_account, flags = re.IGNORECASE)
    regex_account_num = re.compile(p_account_num, flags = re.IGNORECASE)

    # get account num
    for i in range(1,10):
        for j in range(1,40):
            if re.search(regex_account, str(sheet.cell(row=j, column=i).value)):
                account_num = re.search(regex_account_num, str(sheet.cell(row=j, column=i).value)).group()
                print(f'Account num.: {account_num}')

    # search for table vertex
    for i, row in enumerate(sheet.iter_rows(values_only=True)):
        row_list = [str(col).lower() if col != None else None for col in row]
        if 'fecha' in row_list:
            for col in row_list:
                if col != None and 'saldo' in col:
                    apex_r = i
                    apex_c = row_list.index('fecha')
                    col_len = sum(elem is not None for elem in row_list)

    # table row length
    row_len = 0
    for row in sheet.iter_rows(values_only=True):
        if isinstance(row[apex_c], dt):
            row_len= row_len+1
        else:
            try:
                dt.strptime(str(row[apex_c]), '%d/%m/%Y')
                row_len= row_len+1
            except:
                pass

    print(f'Table Rows: {row_len}\nTable Columns: {col_len}')
    table = dict()

    # populate the table
    header = []
    for i, row in enumerate(list(sheet.rows)[apex_r:(apex_r + row_len + 1)]):
        if i == 0:
            for j, col in enumerate(row[apex_c : col_len + 1]):
                if col.value is not None and ' ' in col.value:
                    col.value = col.value.replace(' ','_')
                header.append(col.value)
                table[col.value] = []
        if i > 0:
            for j, col in enumerate(row[apex_c : col_len + 1]):
                if isinstance(col.value, dt):
                    table[header[j]].append(col.value.strftime('%d/%m/%Y'))
                else:
                    cell = " ".join(str(col.value).strip().split())
                    table[header[j]].append(cell)

    bancos = []
    cuentas = []
    date = []
    description = []
    balance = []
    flow = []
    
    if len(account_num) == 13:
        banco = 'BAPRO'
    elif len(account_num) == 11:
        banco = 'BBVA'
    elif len(account_num) == 12:
        banco = 'Santander'

    bancos += [banco for i in range(len(table['Fecha']))]
    cuentas += [account_num for i in range(len(table['Fecha']))]
    date += [datetime.datetime.strptime(date, '%d/%m/%Y') for date in table['Fecha']]

    if 'Concepto' in table.keys():
        description += table['Concepto']
    elif 'Descripción' in table.keys():
        description += table['Descripción']
        # Consolidate in flow the expenses registered in other accounts
        for row in range(len(table['Descripción'])):
            if 'LEY 25413' in table['Descripción'][row]:
                table['Cuenta_sueldo'][row] = table['Importe_cuenta_corriente_pesos'][row]

    if 'Importe' in table.keys():
        flow += [float(num.replace('.','').replace(',','.')) if num != 'None' else 0 for num in table['Importe']]
    elif 'Cuenta_sueldo' in table.keys():
        flow += [float(num.replace('.','').replace(',','.')) if num != 'None' else 0 for num in table['Cuenta_sueldo']]

    if 'Saldo' in table.keys():
        balance += [float(num.replace('.','').replace(',','.')) if num is not None else 0 for num in table['Saldo']]
    elif 'Saldo_pesos' in table.keys():
        balance += [float(num.replace('.','').replace(',','.')) if num is not None else 0 for num in table['Saldo_pesos']]

    data_output = []
    skip = []

    for column in range(len(date)):
        row = []
        for line in [bancos, cuentas, date, description, flow, balance]:
            # save the place of the list with the element 'TRASPASO'
            if 'TRASPASO' in str(line[column]):
                skip.append(column)
            row.append(line[column])
        data_output.append(row)
    
    # erase the lists with the element 'TRASPASO' and update the index
    for i, erase in enumerate(skip):
        data_output.remove(data_output[erase-i])

    os.remove(loaded_file)

    return check_db(data_output)