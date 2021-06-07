from pdflib import Document
from datetime import datetime
from pathlib import Path
import locale
import re
import os

from application import current_app as app
from application import db
from flask_login import current_user
from application.main.models import Credit, CreditStatement, CreditTaxes


locale.setlocale(locale.LC_TIME, '')

app_dir = os.path.abspath(os.path.dirname(__file__))
temp_dir = os.path.join(Path(app_dir).parent,'temp/')


def credit_db(data_input, taxes, close_date, due_date, statement_sum):

    app.logger.info('LOADING ELEMENTS')
    submission = []
    show_taxes = []

    query_statement = CreditStatement.query.filter(
        CreditStatement.user_id == current_user.id,
        CreditStatement.close_date == close_date,
        CreditStatement.due_date == due_date,
        CreditStatement.ars == statement_sum[0],
        CreditStatement.usd == statement_sum[1]
    ).all()

    if not query_statement:
        new_statement = CreditStatement(
            user_id = current_user.id,
            close_date = close_date,
            due_date = due_date,
            ars = statement_sum[0],
            usd = statement_sum[1]
        )
        db.session.add(new_statement)
        db.session.commit()

        query_statement = new_statement.id

    # look if there are any purchase to the corresponding statement
    query = Credit.query.filter(Credit.user_id == current_user.id, Credit.statement == query_statement).all()
   
    if not query:
        for tax in taxes:
            credit_insert = CreditTaxes(statement = query_statement, type=tax[1], amount=tax[2], currency=tax[3])
            db.session.add(credit_insert)

            show_taxes.append(
                [
                    tax[1],
                    tax[2],
                    tax[3], 
                ]
            )

        for row_data in data_input[::-1]:
            credit_insert = Credit(
                user_id= current_user.id,
                statement = query_statement,
                card_code = row_data[0],
                timestamp = row_data[1],
                transaction = row_data[2], 
                share = row_data[3], 
                purchase = row_data[4],
                currency = row_data[5],
            )
            db.session.add(credit_insert)

            submission.append(
                [
                    current_user.id,
                    query_statement,
                    row_data[0],
                    row_data[1],
                    row_data[2], 
                    row_data[3], 
                    row_data[4],
                    row_data[5],
                ]
            )
    db.session.commit()
    return submission, show_taxes, due_date, close_date


def load_PDF(loaded_file):

    app.logger.info('LOADING PDF')
    doc = Document(loaded_file)
    text = ''
    for page in doc:
        text += ' \n'.join(page.lines).strip()

    with open(f"{temp_dir}temp.txt", 'w') as file:
        file.write(text)
        file.close()
    
    os.remove(loaded_file)

    return read_lines()


def read_lines():

    with open(f"{temp_dir}temp.txt", 'r') as file:
        document = file.readlines()
        file.close()

    os.remove(f"{temp_dir}temp.txt")

    app.logger.info('READING LINES')
    consumos = []
    cards = {}
    taxes = []
    comprobante = False

    for row in range(len(document[:])):
        if "CIERRE ACTUAL" in document[row]:
            close_date_row = document[row]
        if "VENCIMIENTO" in document[row]:
            due_date_row = document[row+1]
        if "COMPROBANTE" in document[row]:
            # evitar repetición del header
            if not comprobante:
                comprobante = True
                continue
        # revisar si luego del saldo en pesos hay saldo en dolares
        if "SU PAGO EN USD" in document[row]:
            continue
        elif "SU PAGO EN PESOS" in document[row]:
            continue
        try:
            item = document[row].split()[0]
            date = datetime.strptime(item, "%d.%m.%y")
            if "IVA" in document[row] or "IIBB" in document[row] or "DB.RG" in document[row] or "IMPUESTO" in document[row]:
                saldo = document[row]
                taxes.append(document[row])
            else:
                consumos.append(document[row])
        except:
            if "Tarjeta" in document[row]:
                cards[f"{document[row].split()[1]}"] = consumos
                consumos = []
            if "SALDO ACTUAL" in document[row]:
                result = document[row]
                break

    app.logger.info('READING ELEMENTS')
    # luego leo los renglones
    row = close_date_row.split()
    for i in range(len(row)):
        if ':' in row[i]:
            close_date = f"{row[i+1]} {row[i+2]} {row[i+3]}"

    close_date = datetime.strptime(close_date, "%d %b %y")

    row = due_date_row.split()[1:]
    found = False
    for i in range(len(row)):
        if row[i].isdigit() and not found:
            due_date = f"{row[i]} {row[i+1]} {row[i+2]}"
            found = True

    due_date = datetime.strptime(due_date, "%d %b %y")

    result = result.split()
    statement_sum = []

    count = 0
    for i in range(len(result)):
        if "," in result[i]:
            count += 1
            numero = result[i].replace(',','.')
            # iterar string y descartar cualquier cosa que no sea numero o punto
            monto = ''
            first_dot = False
            for digito in numero[::-1]:
                if digito.isdigit() == True:
                    monto += digito
                # dejar solo el primer punto para poder obtener el float
                if first_dot is False and digito == '.':
                    monto += digito
                    first_dot = True
            # si no transforma a float, dejar str vacío
            try:
                statement_sum.append(float(monto[::-1]))
            except:
                statement_sum.append('')

    # si hay solo pesos, agregar None
    if count == 1:
        statement_sum.append(None)

    total_taxes = []
    moneda = ''
    pattern = "(IMPUESTO DE SELLOS)|(DB.RG 4815)|(DB.IMPUESTO PAIS)|(IIBB PERCEP-CABA)|(IVA RG 4240)"
    
    for i in range(len(taxes)):
        row_taxes = []
        # cut row to extract datetime, currency and amount
        row = taxes[i].split()
        date = datetime.strptime(row[0], "%d.%m.%y")
        row_taxes.append(date)

        regex = re.search(pattern, taxes[i])
        if regex:
            row_taxes.append(regex.group())


        # # todos los strings de numeros tienen dos decimales separados por coma
        if "," in row[-1]:
            numero = row[-1].replace(',','.')
            # iterar string y descartar cualquier cosa que no sea numero o punto
            monto = ''
            first_dot = False
            for digito in numero[::-1]:
                if digito.isdigit() == True:
                    monto += digito
                # dejar solo el primer punto para poder obtener el float
                if first_dot is False and digito == '.':
                    monto += digito
                    first_dot = True
            # si no transforma a float, dejar str
            try:
                row_taxes.append(float(monto[::-1]))
            except:
                pass


        if 'USD' in taxes[i]:
            row_taxes.append('USD')
        else:
            row_taxes.append('ARS')

        total_taxes.append(row_taxes)


    data = []
    for key, value in cards.items():
        for j, row in enumerate(value):
            transaccion = ''
            elements = row.split()
            moneda = ''
            line = []
            line.append(key)

            if 'USD' in elements:
                moneda = 'USD'
            else:
                moneda = 'ARS'

            if 'Cuota' in elements:
                index = elements.index('Cuota')
                cuota = elements[index + 1]
                pass
            else:
                cuota = ''

            for i in range(len(elements)):
                try:
                    date = datetime.strptime(elements[i], "%d.%m.%y")
                    line.append(date)
                except:
                    pass
                
                if i > 1:
                    if elements[i] != 'Cuota' and  "," not in elements[i]:
                        transaccion += f"{elements[i]} "
                
                # # todos los strings de numeros tienen dos decimales separados por coma
                if "," in elements[i]:
                    numero = elements[i].replace(',','.')
                    # iterar string y descartar cualquier cosa que no sea numero o punto
                    monto = ''
                    first_dot = False
                    for digito in numero[::-1]:
                        if digito.isdigit() == True:
                            monto += digito
                        # dejar solo el primer punto para poder obtener el float
                        if first_dot is False and digito == '.':
                            monto += digito
                            first_dot = True
                    # si no transforma a float, dejar str
                    try:
                        monto = float(monto[::-1])
                    except:
                        pass

            line.append(transaccion[:-1])
            line.append(cuota)
            line.append(monto)
            line.append(moneda)

            data.append(line)
 
    
    return credit_db(data, total_taxes, close_date, due_date, statement_sum)