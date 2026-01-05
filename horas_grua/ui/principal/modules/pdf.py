import re
import pdfplumber
import json
from datetime import datetime
import os
import sys

# # Ajustar path para importar db_controller
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
# from db_controller import obtener_id_sector_por_nombre


# ------------------------------
# LIMPIEZA BÁSICA
# ------------------------------

def limpiar_texto(txt):
    txt = txt.replace("/", "")
    txt = re.sub(r"\bSECTOR\b", "", txt, flags=re.IGNORECASE)
    txt = re.sub(r"\s+", " ", txt)
    return txt.strip()

def convertir_fecha(fecha_ddmmyyyy):
    return datetime.strptime(fecha_ddmmyyyy, "%d.%m.%Y").strftime("%Y-%m-%d")


# ------------------------------
# EXTRAER FECHA DE ORDEN
# ------------------------------

def extraer_fecha_orden(texto):
    m = re.search(r"Fecha:\s*(\d{2}\.\d{2}\.\d{4})", texto)
    return m.group(1) if m else None


# ------------------------------
# EXTRAER PROVEEDOR (CORREGIDO)
# ------------------------------

def extraer_proveedor(texto):
    m = re.search(r"Proveedor:\s*(.+)", texto)
    proveedor = ""

    if m:
        prov_line = m.group(1).strip()

        prov_line = re.split(
            r"RTN:|Dirección:|Ciudad:|Código Proveedor|Área solicitante|Contrato|Fecha:",
            prov_line
        )[0]

        proveedor = prov_line.replace("/", " ")
        proveedor = re.sub(r"\s+", " ", proveedor).strip()

    # Código de proveedor (funciona aunque venga en otra línea)
    codigo = re.search(r"Proveedor:\s*(\d+)", texto, re.IGNORECASE)
    if codigo:
        codigo = codigo.group(1)
    else:
        codigo = ""

    return proveedor, codigo   # ← VA AQUÍ, fuera del else


# ------------------------------
# EXTRAER LOS ITEMS DE LA ORDEN
# ------------------------------

def extraer_items(texto):

    patron = re.compile(
        r"(00010|00020)\s+([A-ZÁÉÍÓÚÑ0-9 .\-\n]+?)\s+(\d+(?:\.\d+)?)\s+H\s+(\d{2}\.\d{2}\.\d{4})\s+Sector\s+(.+?)\s*/",
        re.IGNORECASE | re.DOTALL
    )

    items = []
    for m in patron.finditer(texto):
        codigo = m.group(1)
        descripcion = limpiar_texto(m.group(2))
        horas = m.group(3)
        fecha_item = m.group(4)
        sector = limpiar_texto(m.group(5))

        # Detectar tipo de servicio
        desc_upper = descripcion.upper()
        if "GRUA" in desc_upper:
            tipo_servicio = "GRUA"
        elif "CANASTA" in desc_upper:
            tipo_servicio = "CANASTA"
        else:
            tipo_servicio = ""

        items.append({
            "equipo": tipo_servicio,
            "hora_inicio": horas,
            "codigo_sector": sector.upper()
        })

    return items


# ------------------------------
# PROCESAR PDF COMPLETO
# ------------------------------

def procesar_pdf(pdf_path):
    texto = ""

    with pdfplumber.open(pdf_path) as pdf:
        for p in pdf.pages:
            texto += "\n" + p.extract_text()
    #print(texto)
    fecha_raw = extraer_fecha_orden(texto)
    fecha_orden = convertir_fecha(fecha_raw) if fecha_raw else None

    proveedor, codigo_proveedor = extraer_proveedor(texto)
    items = extraer_items(texto)
    numero_compra = extraer_numero_compra(texto)  # ← NUEVO

    for item in items:
        item["fecha_str"] = fecha_orden
        item["proveedor"] = proveedor
        item["codigo_proveedor"] = codigo_proveedor
        item["orden_entry"] = numero_compra  # ← NUEVO

    return items

# ------------------------------
# EXTRAER NÚMERO DE COMPRA
# ------------------------------

def extraer_numero_compra(texto):
    m = re.search(r"N[uú]mero[: ]+(\d{7,12})", texto, re.IGNORECASE)
    return m.group(1) if m else ""


# ------------------------------
# EJECUTAR
# ------------------------------

#resultado = procesar_pdf(r"C:\Users\bryan.colindres\Downloads\4400008069 orden de compra con horas grua y horas canasta.PDF")
#print(json.dumps(resultado, indent=2, ensure_ascii=False))


