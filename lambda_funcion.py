import requests
import boto3
import datetime

def lambda_handler(event, context):
    # Nombre del bucket de destino
    BUCKET_NAME = "landing-casas-pbd"
    
    # URL base con los parámetros fijos
    BASE_URL = "https://casas.mitula.com.co/find?operationType=sell&propertyType=mitula_studio_apartment&text=Bogot%C3%A1"
    
    s3_client = boto3.client("s3")
    
    # Obtener la fecha actual para formar el nombre de los archivos
    today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    
    # Headers para evitar caché y simular un navegador real
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache"
    }
    
    # Iterar por las primeras 10 páginas y guardarlas individualmente
    for page in range(1, 11):
        if page == 1:
            url = BASE_URL
        else:
            url = f"{BASE_URL}&page={page}"
            
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            # Definir el nombre del archivo en S3
            file_key = f"{today}-page-{page}.html"
            s3_client.put_object(
                Bucket=BUCKET_NAME,
                Key=file_key,
                Body=response.text.encode("utf-8"),
                ContentType="text/html"
            )
            print(f"Página {page} guardada en s3://{BUCKET_NAME}/{file_key}")
        else:
            print(f"Error al descargar la página {page}: {response.status_code}")
    
    return {
        "statusCode": 200,
        "body": f"Páginas guardadas en s3://{BUCKET_NAME}/"
    }
