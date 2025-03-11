import boto3
import csv
import io
from datetime import datetime
from bs4 import BeautifulSoup

def lambda_handler(event, context):
    if 'Records' not in event:
        return {"error": "El evento no contiene 'Records'. Por favor, proporciona un evento S3 válido."}
    s3_event = event['Records'][0]['s3']
    # Extraer datos del evento S3 (el archivo HTML que se subió)
    s3_event = event['Records'][0]['s3']
    source_bucket = s3_event['bucket']['name']
    source_key = s3_event['object']['key']
    
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=source_bucket, Key=source_key)
    html_content = response['Body'].read().decode('utf-8')
    
    # Procesar el HTML con BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    rows = []
    
    # asumiendo que cada casa está en un <div class="casa">
    casas = soup.find_all('div', class_='casa')
    for casa in casas:
        # Extrae la información; ajusta los selectores a la estructura real
        barrio = casa.find('span', class_='barrio').text.strip() if casa.find('span', class_='barrio') else ''
        valor = casa.find('span', class_='valor').text.strip() if casa.find('span', class_='valor') else ''
        num_habitaciones = casa.find('span', class_='habitaciones').text.strip() if casa.find('span', class_='habitaciones') else ''
        num_banos = casa.find('span', class_='banos').text.strip() if casa.find('span', class_='banos') else ''
        mts2 = casa.find('span', class_='mts2').text.strip() if casa.find('span', class_='mts2') else ''
        # La fecha de descarga será la fecha actual
        fecha_descarga = datetime.utcnow().strftime('%Y-%m-%d')
        rows.append([fecha_descarga, barrio, valor, num_habitaciones, num_banos, mts2])
    
    # Crear el CSV en memoria
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(["FechaDescarga", "Barrio", "Valor", "NumHabitaciones", "NumBanos", "mts2"])
    writer.writerows(rows)
    
    # Guardar el CSV en el bucket de salida
    output_bucket = 'casas-final-pbd'
    csv_key = f"{datetime.utcnow().strftime('%Y-%m-%d')}.csv"
    s3.put_object(Bucket=output_bucket, Key=csv_key, Body=csv_buffer.getvalue(), ContentType='text/csv')
    
    print(f"CSV guardado en s3://{output_bucket}/{csv_key}")
    return {"status": "processed", "csv_key": csv_key}
