import os
import requests
import base64
import logging
import time
import sys
from dotenv import load_dotenv
import os

load_dotenv()




sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from db_controller import sector_id

def send_email(access_token, subject, body, to_addresses, attachment_path=None,cc_addresses =None):
    # Crear una sesión de Microsoft Graph con el token de acceso
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    # Crear el cuerpo del mensaje
    email_message = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "HTML",
                "content": body
            },
            "toRecipients": [],  # Lista vacía inicialmente para agregar los destinatarios
            "ccRecipients": []   # Lista vacía para los destinatarios en CC
        },
        "saveToSentItems": "true"
    }

    # Añadir los destinatarios al mensaje
    if to_addresses:
        for address in to_addresses:
            email_message["message"]["toRecipients"].append({
                "emailAddress": {
                    "address": address
                }
            })
    
        # Añadir destinatarios en CC si se proporciona
    if cc_addresses:
        for address in cc_addresses:
            email_message["message"]["ccRecipients"].append({
            "emailAddress": {
            "address": address
            }
            })

    # Inicializar la lista de adjuntos (vacía por defecto)
    email_message["message"]["attachments"] = []

    # Si se proporciona un archivo para adjuntar
    if attachment_path:
        try:
            # Leer el archivo y codificarlo en Base64
            with open(attachment_path, "rb") as file:
                file_content = file.read()
                encoded_content = base64.b64encode(file_content).decode('utf-8')

            # Obtener el nombre del archivo del path
            filename = os.path.basename(attachment_path)

            # Crear el objeto del adjunto
            attachment = {
                "@odata.type": "#microsoft.graph.fileAttachment",
                "name": filename,
                "contentType": "application/pdf",  # Tipo de contenido
                "contentBytes": encoded_content  # Contenido codificado en Base64
            }

            # Añadir el adjunto al mensaje
            email_message["message"]["attachments"].append(attachment)
        except Exception as e:
            print(f"Error al adjuntar el archivo: {e}")
            return

    # Enviar el correo a través de Microsoft Graph
    # response = requests.post(
    #     f"https://graph.microsoft.com/v1.0/me/sendMail",
    #     headers=headers,
    #     json=email_message
    # )
    url = "https://graph.microsoft.com/v1.0/me/sendMail"
    
    while True:
        try:
            response = requests.post(url, headers=headers, json=email_message)
            response.raise_for_status()
            logging.info("Correo enviado exitosamente.")
            break  # Éxito → salimos del bucle
        except requests.exceptions.SSLError as ssl_error:
            logging.warning("Fallo SSL, intentando sin verificación de certificado...")
            try:
                response = requests.post(url, headers=headers, json=email_message, verify=False)
                response.raise_for_status()
                logging.info("Correo enviado exitosamente (con verificación desactivada).")
                break  # Éxito → salimos del bucle
            except Exception as e:
                logging.error(f"Nuevo error al intentar sin verificación: {e}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error al enviar correo: {e}")
        
        logging.info("Reintentando en 3 segundos...")
        time.sleep(3)  # Esperar antes de reintentar

    # Verificar la respuesta
    if response.status_code == 202:
        print("Correo enviado con éxito.")
        return True
    else:
        print(f"Error al enviar el correo: {response.status_code}, {response.text}")
        return False


def generar_tabla_html(sector,orden_compra):
    html = f"""<html> <body>
    <p>Buen dia, </p>
    <p>Estimados Ingenieros: </p>
    <p>Reciban un cordial saludo. Deseando éxitos en sus labores diarias, informando que que el sector {sector} ha alcanzado el 70% en horas grua en la orden de compra {orden_compra}:</p>
    """
    html += """
    <p>Quedamos a la orden como parte del equipo de la Dirección de Planeación y Gestión del Desempeño, para futuras colaboraciones que puedan aportar a la mejora de los indicadores estratégicos a nivel de Empresa.</p>
    <p>Saludos cordiales.</p>
    </body>
    </html>
    """
    html += """
    <div style="font-family: Calibri; font-size: 14pt; color: #000000;">
        <p><strong>Bryan Colindres</strong><br>
        <strong>Gestión de la Información</strong><br>
        UTCD - ENEE<br>
        <a href="mailto:bryan.colindres@enee.hn">bryan.colindres@enee.hn</a><br>
        Tel: +504 31626792</p>
    </div>
    """
     # Firma al final del correo
    return html



def obtener_token():
    client_id = os.getenv("AZURE_CLIENT_ID")
    client_secret = os.getenv("AZURE_CLIENT_SECRET")
    tenant_id = os.getenv("AZURE_TENANT_ID")

    username = os.getenv("USUARIO")
    password = os.getenv("CONTRASENA")
    access_token = ''
    print(f"Usuario para token: {username}")
    print(f"Client ID: {client_id}")
    print(f"Tenant ID: {tenant_id}")

    # URL para obtener el token de acceso usando ROPC
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    
    # Parámetros para obtener el token de acceso
    token_data = {
        'grant_type': 'password',  # Usamos 'password' para el flujo ROPC
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'User.Read Mail.Send',  # Los permisos delegados que necesitas
        'username': username,
        'password': password
        }
            
    # Solicitar el token de acceso
    response = requests.post(token_url, data=token_data)

    # Verificar si la solicitud fue exitosa
    if response.status_code == 200:
        access_token = response.json()['access_token']
        #print("Token de acceso obtenido:", access_token)
    else:
        print("Error al obtener el token. Código de error:", response.status_code)
        #print(response.json())
    return access_token

def obtener_correos_por_sector(cursor, sector):
    """
    Obtiene los correos (coordinador y líder) para un sector desde la tabla SECTORESUTCD
    """
    query = """
        SELECT Cargo, Correo
        FROM [192.168.104.84].[GESTIONCONTROL].dbo.SECTORESUTC
        WHERE Sector = ?
    """
    cursor.execute(query, (sector,))
    rows = cursor.fetchall()

    # Separar correos según cargo
    to_addresses = []
    cc_addresses = ["bryan.colindres@eneeutcd.hn","cristian.umanzor@eneeutcd.hn"]

    for cargo, correo in rows:
        to_addresses.append(correo)


    return to_addresses, cc_addresses

# ---------------- enviar correo ----------------

def envia_correo(sector,orden_compra):
    print('hola entre a la funcion de enviar correo')
    try:
        access_token = obtener_token()
    except:
        print('token fallo')
    #sector_obtenido = sector_id(sector).SECTOR
    sector_obtenido = sector
    print(f"Sector obtenido: {sector_obtenido}")
    if not access_token:
        print("No se pudo obtener el token de acceso. Abortando envío de correo.")
        return False
    else:
        print("Token de acceso obtenido correctamente.")
        body = generar_tabla_html(sector_obtenido,orden_compra)
        to_addresses = ["bryan.colindres@eneeutcd.hn"]
        cc_addresses = ["bryan.colindres@eneeutcd.hn"]
        
        send_email(access_token, "Horas grua: Límite alcanzado", body, to_addresses, attachment_path=None,cc_addresses=None)
        return True

