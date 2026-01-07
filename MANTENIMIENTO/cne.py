import requests

# URL de la API
url = "https://appcnd.enee.hn:3200/odsprd/wwv_flow.ajax?p_context=operador-del-sistema-ods/otr/10169039891698"

# Encabezados necesarios (puedes añadir o modificar según sea necesario)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "x-requested-with": "XMLHttpRequest",
    "Referer": "https://appcnd.enee.hn:3200/odsprd/ods_prd/r/operador-del-sistema-ods/otr"
}

# Cookies (asegúrate de incluir las cookies necesarias)
cookies = {
    "ORA_WWV_APP_100": "ORA_WWV-rmXGrRcQqPC0cF-XjLyrHsjx",  # ejemplo, usa tu cookie real
    "_gid": "GA1.2.1700898230.1765827736",
    "_gat_gtag_UA_204664957_1": "1",
    "_ga_SBQCZXQBP1": "GS2.1.s1765827735$o275$g0$t1765827743$j52$l0$h0",
    "_ga_W2WLFNWXVS": "GS2.1.s1765827735$o281$g1$t1765827754$j41$l0$h0",
    "_ga": "GA1.1.2124344841.1736864501.1736864501"
}

# Datos a enviar en el cuerpo de la solicitud (ajustar según los parámetros necesarios)
data = {
    # Agrega los parámetros que la API requiere
    "param1": "value1",
    "param2": "value2",
    # ...
}

# Realizar la solicitud POST
response = requests.post(url, headers=headers, cookies=cookies, data=data)

# Verificar el estado de la respuesta
if response.status_code == 200:
    print("Solicitud exitosa")
    print(response.json())  # O response.text, dependiendo de la respuesta
else:
    print(f"Error: {response.status_code}")
    print(response.text)
