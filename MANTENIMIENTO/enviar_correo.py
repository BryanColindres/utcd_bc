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


def generar_tabla_html(data):
    """
    Genera el cuerpo HTML del correo con:
    - Tabla con índice, circuito, interrupciones (6 meses),
      horas de interrupción (6 meses), último mantenimiento,
      clientes actuales y detalle de ubicaciones
    - Mensaje institucional generado automáticamente

    Parámetro:
        data (list[dict]): Lista de registros. Cada registro puede usar claves
        en distintos formatos según la consulta SQL.

    Retorna:
        str: HTML completo como string
    """

    def v(d, *keys, default=''):
        """Devuelve el primer valor no None para una lista de posibles keys (case-insensitive)."""
        for k in keys:
            if k in d and d[k] is not None:
                return d[k]
            alt = k.capitalize()
            if alt in d and d[alt] is not None:
                return d[alt]
        for key in d.keys():
            if key.lower() in [kk.lower() for kk in keys] and d.get(key) is not None:
                return d.get(key)
        return default

    def fmt_int(x):
        try:
            return f"{int(round(float(x))):,}".replace(".", ",")
        except Exception:
            return "0"

    def fmt_float(x, dec=2):
        try:
            return f"{float(x):,.{dec}f}".replace(",", "X").replace(",", ".").replace("X", ".")
        except Exception:
            return "0.00"

    html = """
    <html>
    <body style="font-family: Calibri, Arial, sans-serif; font-size: 12pt; color: #000;">
        <p>Buen día,</p>

        <p>Estimados ingenieros:</p>

        <p>
            Reciban un cordial saludo. Con el objetivo de aportar a la adecuada gestión
            del plan de mantenimiento, se presenta un resumen de los circuitos que no
            registran mantenimiento programado en los últimos seis meses.
        </p>

        <p>
            Se indica la cantidad de interrupciones ocurridas en el período,
            la duración acumulada de las interrupciones (horas),
            la fecha del último mantenimiento registrado,
            la cantidad de clientes actuales por circuito
            y el detalle de los reconectadores o interruptores asociados.
        </p>

        <table border="0" cellpadding="0" cellspacing="0"
               style="border-collapse: collapse; width: 100%; max-width: 1050px;">
            <thead>
                <tr>
                    <th style="padding:10px 8px; background:#f2f2f2; border:1px solid #ddd;">No.</th>
                    <th style="padding:10px 8px; background:#f2f2f2; border:1px solid #ddd;">Circuito</th>
                    <th style="padding:10px 8px; background:#f2f2f2; border:1px solid #ddd; text-align:right;">
                        Frecuencia (6 meses)
                    </th>
                    <th style="padding:10px 8px; background:#f2f2f2; border:1px solid #ddd; text-align:right;">
                        Duración Horas (6 meses)
                    </th>
                    <th style="padding:10px 8px; background:#f2f2f2; border:1px solid #ddd;">
                        Último mantenimiento
                    </th>
                    <th style="padding:10px 8px; background:#f2f2f2; border:1px solid #ddd; text-align:right;">
                        Clientes (mes actual)
                    </th>
                    <th style="padding:10px 8px; background:#f2f2f2; border:1px solid #ddd;">
                        Detalle interrupciones (frecuencia, duración)
                    </th>
                </tr>
            </thead>
            <tbody>
    """

    if not data:
        html += """
            <tr>
                <td colspan="7" style="padding:12px; border:1px solid #ddd;">
                    No se encontraron registros para el período indicado.
                </td>
            </tr>
        """
    else:
        for idx, item in enumerate(data, start=1):
            circuito = v(item, 'circuito', 'Circuito', default='')
            interrupciones = v(
                item,
                'Interrupciones_6_meses',
                'Interrupciones',
                'Total_ubicaciones_reportadas',
                'numero_registros',
                default=0
            )
            horas = v(
                item,
                'Horas_interrupcion_6_meses',
                'Horas_interrupcion_6m',
                'horas_interrupcion',
                default=0
            )
            ultimo = v(item, 'Ultimo_mantenimiento', 'ultimo_mantenimiento', default='SIN REGISTRO')
            clientes = v(item, 'Clientes_actuales', 'clientes_actuales', 'Clientes', default=0)
            detalle = v(item, 'Equipos_detalle', 'equipos_detalle', default='SIN DETALLE')

            html += f"""
                <tr>
                    <td style="padding:8px; border:1px solid #eee;">{idx}</td>
                    <td style="padding:8px; border:1px solid #eee;">{circuito}</td>
                    <td style="padding:8px; border:1px solid #eee; text-align:right;">
                        {fmt_int(interrupciones)}
                    </td>
                    <td style="padding:8px; border:1px solid #eee; text-align:right;">
                        {fmt_float(horas, 2)}
                    </td>
                    <td style="padding:8px; border:1px solid #eee;">
                        {ultimo if str(ultimo).strip() else 'SIN REGISTRO'}
                    </td>
                    <td style="padding:8px; border:1px solid #eee; text-align:right;">
                        {fmt_int(clientes)}
                    </td>
                    <td style="padding:8px; border:1px solid #eee; white-space:normal;">
                        {detalle if str(detalle).strip() else 'SIN DETALLE'}
                    </td>
                </tr>
            """

    html += """
            </tbody>
        </table>

        <p style="margin-top:12px;">
            La información presentada es generada automáticamente con el propósito
            de apoyar la toma de decisiones operativas basadas en datos
            y la adecuada gestión del plan de mantenimiento anual.
        </p>

        <p>
            Quedamos atentos desde la Dirección de Planeación y Gestión del Desempeño
            para cualquier consulta adicional.
        </p>

        <div style="font-family: Calibri; font-size: 11pt; margin-top: 12px;">
            <strong>Control de Gestión</strong><br>
            bryan.colindres@eneeutcd.hn – 3162-6792<br>
            Analista de Gestión de la Información
        </div>
    </body>
    </html>
    """

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

def obtener_conexion_sql_server_global():
    import pyodbc

    server = "192.168.100.7"
    database = "GestionControl"
    username = "bdc01755"
    password = "Honduras2026"

    connection_string = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password}"
    )
    connection = pyodbc.connect(connection_string)
    cursor = connection.cursor()
    return cursor

def obtener_circuitos_sin_mantenimiento(cursor, meses=6):
    """
    Obtiene los circuitos que no han tenido mantenimiento (registro 16) en los últimos 'meses'
    trayendo también la fecha del último mantenimiento (si existe), clientes actuales,
    número de interrupciones y el detalle de ubicaciones (equipos_detalle).
    """
    meses = int(meses)

    query = f"""
WITH interrupciones AS (
    SELECT 
        B.Circuito,
        COUNT(*) AS Numero_registros,
        SUM(CASE WHEN UPPER(LTRIM(RTRIM(B.tipo_interruptor))) = 'RESTAURADOR' THEN 1 ELSE 0 END) AS Num_interruptores,
        SUM(CASE WHEN UPPER(LTRIM(RTRIM(B.tipo_interruptor))) = 'INTERRUPTOR' THEN 1 ELSE 0 END) AS Num_circuito_completo
    FROM GestionControl.dbo.BITACORA_SCADA B
    WHERE B.Fecha_apertura > DATEADD(MONTH, -6, GETDATE())
      AND B.Registro_interrupcion != 19
    GROUP BY B.Circuito
),

-- ===================== HORAS DE INTERRUPCIÓN (6 MESES) =====================
horas_por_circuito AS (
    SELECT
        B.Circuito,
        SUM(ISNULL(B.tiempo_horas, 0)) AS Horas_interrupcion_6m
    FROM GestionControl.dbo.BITACORA_SCADA B
    WHERE B.Fecha_apertura > DATEADD(MONTH, -6, GETDATE())
      AND B.Registro_interrupcion != 19
    GROUP BY B.Circuito
),

-- ===================== UBICACIONES / EQUIPOS (CON HORAS) =====================
ubicaciones_por_circuito AS (
    SELECT
        B.Circuito,
        COALESCE(
            NULLIF(LTRIM(RTRIM(
                CASE 
                    WHEN UPPER(LTRIM(RTRIM(B.Tipo_interruptor))) = 'INTERRUPTOR' 
                        THEN B.equipo_opero 
                    ELSE B.ubicacion 
                END
            )), ''), 'SIN_UBICACION') AS ubicacion_usada,
        COUNT(*) AS cnt,
        SUM(ISNULL(B.tiempo_horas, 0)) AS horas_cnt
    FROM GestionControl.dbo.BITACORA_SCADA B
    WHERE B.Fecha_apertura > DATEADD(MONTH, -6, GETDATE())
      AND B.Registro_interrupcion != 19
    GROUP BY B.Circuito,
             CASE 
                WHEN UPPER(LTRIM(RTRIM(B.Tipo_interruptor))) = 'INTERRUPTOR' 
                    THEN B.equipo_opero 
                ELSE B.ubicacion 
             END
),

-- ===================== DETALLE LEGIBLE DE EQUIPOS =====================
equipos_agg AS (
    SELECT
        Circuito,
        STRING_AGG(
            CONCAT(
                ubicacion_usada,
                ' (', cnt, ', ',
                ROUND(horas_cnt, 2), ' h)'
            ),
            ', '
        ) WITHIN GROUP (ORDER BY horas_cnt DESC, cnt DESC, ubicacion_usada) AS Equipos_detalle
    FROM ubicaciones_por_circuito
    GROUP BY Circuito
),

equipos_counts AS (
    SELECT
        Circuito,
        SUM(cnt) AS Total_ubicaciones_reportadas
    FROM ubicaciones_por_circuito
    GROUP BY Circuito
),

-- ===================== ÚLTIMOS MANTENIMIENTOS =====================
ultimo_gestion AS (
    SELECT 
        Circuito,
        MAX(Fecha_apertura) AS Ultimo_mant_gestion
    FROM GestionControl.dbo.BITACORA_SCADA
    WHERE Registro_interrupcion in ('16','45')
    GROUP BY Circuito
),

ultimo_calidad AS (
    SELECT 
        Circuito,
        MAX(Fecha_apertura) AS Ultimo_mant_calidad
    FROM CalidadEnergia.dbo.BITACORA_SCADA
    WHERE Registro_interrupcion in ('16','45')
    GROUP BY Circuito
),

-- ===================== CLIENTES =====================
clientes_actuales AS (
    SELECT
        Circuito,
        SUM(Clientes) AS Clientes
    FROM GestionControl.dbo.CLIENTES_CIRCUITO
    WHERE [Año] = YEAR(GETDATE())
      AND [Mes] = MONTH(GETDATE())
    GROUP BY Circuito
),

-- ===================== CIRCUITOS SIN MANTENIMIENTO RECIENTE =====================
sin_mant_reciente AS (
    SELECT 
        i.Circuito,
        i.Numero_registros,
        COALESCE(ug.Ultimo_mant_gestion, uc.Ultimo_mant_calidad) AS Ultimo_mantenimiento
    FROM interrupciones i
    LEFT JOIN ultimo_gestion ug ON ug.Circuito = i.Circuito
    LEFT JOIN ultimo_calidad uc ON uc.Circuito = i.Circuito
    WHERE NOT EXISTS (
        SELECT 1
        FROM GestionControl.dbo.BITACORA_SCADA b2
        WHERE b2.Circuito = i.Circuito
          AND b2.Registro_interrupcion IN ('16','45')
          AND b2.Fecha_apertura > DATEADD(MONTH, -6, GETDATE())
    )
      AND NOT EXISTS (
        SELECT 1
        FROM CalidadEnergia.dbo.BITACORA_SCADA b3
        WHERE b3.Circuito = i.Circuito
          AND b3.Registro_interrupcion IN ('16','45')
          AND b3.Fecha_apertura > DATEADD(MONTH, -6, GETDATE())
    )
)

-- ===================== RESULTADO FINAL =====================
SELECT 
    s.Circuito,
    ISNULL(ec.Total_ubicaciones_reportadas, 0) AS Interrupciones_6_meses,
    ISNULL(ROUND(h.Horas_interrupcion_6m, 2), 0) AS Horas_interrupcion_6_meses,
    IIF(
        s.Ultimo_mantenimiento IS NOT NULL, 
        CONVERT(varchar(10), s.Ultimo_mantenimiento, 103), 
        'SIN REGISTRO'
    ) AS Ultimo_mantenimiento,
    ISNULL(c.Clientes, 0) AS Clientes_actuales,
    ISNULL(ea.Equipos_detalle, 'SIN DETALLE') AS Equipos_detalle
FROM sin_mant_reciente s
LEFT JOIN clientes_actuales c ON c.Circuito = s.Circuito
LEFT JOIN equipos_agg ea ON ea.Circuito = s.Circuito
LEFT JOIN equipos_counts ec ON ec.Circuito = s.Circuito
LEFT JOIN horas_por_circuito h ON h.Circuito = s.Circuito
WHERE ISNULL(c.Clientes, 0) <> 0
ORDER BY s.Numero_registros DESC;
    """

    try:
        cursor.execute(query)
        rows = cursor.fetchall()
    except Exception as e:
        print(f"[obtener_circuitos_sin_mantenimiento] Error ejecutando query: {e}")
        return []

    data = []

    for i, row in enumerate(rows, start=1):
        try:
            circuito = row[0] if len(row) > 0 else ''

            interrupciones = int(row[1]) if len(row) > 1 and row[1] is not None else 0

            horas_interrupcion = float(row[2]) if len(row) > 2 and row[2] is not None else 0.0

            ultimo_mantenimiento = row[3] if len(row) > 3 and row[3] is not None else 'SIN REGISTRO'

            clientes_actuales = int(row[4]) if len(row) > 4 and row[4] is not None else 0

            equipos_detalle = row[5] if len(row) > 5 and row[5] is not None else 'SIN DETALLE'

            data.append({
                'circuito': circuito,
                'numero_registros': interrupciones,   # usado por HTML
                'horas_interrupcion': horas_interrupcion,
                'ultimo_mantenimiento': ultimo_mantenimiento,
                'clientes_actuales': clientes_actuales,
                'equipos_detalle': equipos_detalle
            })

        except Exception as e:
            print(f"[obtener_circuitos_sin_mantenimiento] Error procesando fila #{i} {row}: {e}")
            continue


    return data

# ---------------- enviar correo ----------------

def envia_correo():
    print('hola entre a la funcion de enviar correo')
    try:
        access_token = obtener_token()
    except:
        print('token fallo')
    #sector_obtenido = sector
    if not access_token:
        print("No se pudo obtener el token de acceso. Abortando envío de correo.")
        return False
    else:
        cursor_global = obtener_conexion_sql_server_global()
        print("Token de acceso obtenido correctamente.")
        data = obtener_circuitos_sin_mantenimiento(cursor_global, meses=6)
        body = generar_tabla_html(data)
        to_addresses = ["bryan.colindres@eneeutcd.hn"]
        cc_addresses = None
        # cc_addresses = ["elmer.bustillo@eneeutcd.hn","edwin.carrasco@eneeutcd.hn","daniel.garcia@eneeutcd.hn","laura.munguia@eneeutcd.hn","monica.rodriguez@eneeutcd.hn","larissa.aceituno@eneeutcd.hn","bryan.colindres@eneeutcd.hn","cristian.umanzor@eneeutcd.hn","david.rosales@eneeutcd.hn"]
        
        send_email(access_token, "CIRCUITOS SIN MANTENIMIENTO EN LOS ULTIMOS 6 MESES", body, to_addresses, attachment_path=None,cc_addresses=cc_addresses)
        return True

if __name__ == "__main__":
    envia_correo()
