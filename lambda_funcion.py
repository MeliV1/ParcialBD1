import requests
import boto3
from datetime import datetime

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    # Se guarda en el bucket s3
    bucket_name = 'landing-casas-pbd'
    # Genera la fecha actual (en UTC o ajusta a tu zona horaria)
    date_str = datetime.utcnow().strftime('%Y-%m-%d')
    
    # Itera sobre las páginas de 1 a 10
    for page in range(1, 11):
        url = f'https://casas.mitula.com.co/find?operationType=sell&propertyType=mitula_studio_apartment&geoId=mitula-CO-poblacion-0000014156&text=Bogot%C3%A1%2C++%28Cundinamarca%29'
        response = requests.get(url)
        
        if response.status_code == 200:
            # Define la clave del objeto en S3, se puede incluir el número de página
            file_key = f'{date_str}-page-{page}.html'
            s3.put_object(
                Bucket=bucket_name,
                Key=file_key,
                Body=response.text,
                ContentType='text/html'
            )
            print(f"Página {page} guardada en S3 como {file_key}")
        else:
            print(f"Error al descargar la página {page}: {response.status_code}")
    
    return {"status": "completed"}