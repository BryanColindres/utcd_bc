import pyodbc
from tkinter import messagebox
from datetime import datetime
from ui.principal.session_manager import get_sesion
# Configuración de la conexión
server = '192.168.100.7'
database = 'GestionControl'
driver = '{ODBC Driver 17 for SQL Server}'  # Ajusta según tu driver instalado
fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ----------------------------------------------------------
# FUNCION PARA OBTENER EL PROVEEDOR MEDIANTE LA ORDEN DE COMPRA
# ----------------------------------------------------------
def obtener_proveedor_por_orden(orden_compra):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT PROVEEDOR FROM HORAS_GRUA_ORDEN_COMPRA WHERE ORDEN_COMPRA = ? AND ACTIVO=1", (orden_compra,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        print("Error obteniendo proveedor por orden de compra:", e)
        return None
# -----------------------------------------------------------
# FUNCION PARA OBTENER ID MEDIANTE EL NOMBRE DEL SECTOR
# -----------------------------------------------------------
def obtener_id_sector_por_nombre(sector_nombre):
    sector = sector_nombre.upper()
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ID_SECTOR FROM HORAS_GRUA_SECTORES WHERE SECTOR = ?", (sector,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        print("Error obteniendo id_sector por nombre:", e)
        return None

# -----------------------------------------------------------
# FUNCIÓN PRINCIPAL DE CONEXIÓN
# -----------------------------------------------------------
def get_connection():
    usuario, contrasena, _ = get_sesion()
    if not usuario or not contrasena or usuario == "vacio":
        raise ValueError("⚠️ No hay sesión activa. Inicia sesión antes de continuar.")
    conn = pyodbc.connect(
        f"DRIVER={driver};SERVER={server};DATABASE={database};UID={usuario};PWD={contrasena}"
    )
    return conn

# -----------------------------------------------------------
# OBTENER ROL ACTUAL
# -----------------------------------------------------------
def obtener_rol():
    try:
        usuario, _, _ = get_sesion()
        print('EL USUARIO DEL ROL ES ',usuario)
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT tipo FROM HORAS_GRUA_SECTORES WHERE usuario = ?", (usuario,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        print("Error obteniendo rol:", e)
        return None

# -----------------------------------------------------------
# OBTENER ID DEL SECTOR ACTUAL
# -----------------------------------------------------------
def obtener_id_sector():
    try:
        usuario, _, _ = get_sesion()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_sector FROM HORAS_GRUA_SECTORES WHERE usuario = ?", (usuario,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        print("Error obteniendo id_sector:", e)
        return None



def get_connection_usuario():
    try:
        usuario, contrasena, rol = get_sesion()
        print(f'la llamada a get usuairo da como usuario{usuario} y contraseña {contrasena}')
        if not usuario or not contrasena:
            raise ValueError("Sesión no iniciada: usuario o contraseña vacíos.")
        
        conn = pyodbc.connect(
            f"DRIVER={driver};SERVER={server};DATABASE={database};UID={usuario};PWD={contrasena}"
        )
        return usuario,contrasena,rol
    except:
        return None, None,None

def get_usuario_actual():
    """Retorna el nombre del usuario actualmente logueado."""
    usuario, _, _ = get_sesion()
    return usuario


def get_fecha_actual():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

import pyodbc
from tkinter import messagebox


def connect_to_sql(usuario, contraseña):
    if usuario == None and contraseña == None:
        return None,None
    """
    Conecta al servidor SQL y devuelve una tupla (conn, rol) si todo va bien.
    Si falla el login, devuelve (None, None).
    """
    conn_str = (
        f"DRIVER={{SQL Server}};"
        f"SERVER=192.168.100.7;"
        f"DATABASE=GestionControl;"
        f"UID={usuario};"
        f"PWD={contraseña};"
    )

    try:
        conn = pyodbc.connect(conn_str)
        rol = obtener_rol()
        return conn, rol

    except pyodbc.Error as e:
        error_msg = str(e)
        if "Login failed" in error_msg:
#            messagebox.showerror("Error de inicio de sesión", "Usuario o contraseña incorrectos.")
            return None, None
        else:
            messagebox.showerror("Error de conexión", f"Error desconocido: {error_msg}")
            return None, None




# ---------------- Funciones para la tabla HorasGrua ----------------
def obtener_horas_grua_completo():
    print('ENTRE AL HORA GRUA COMPLETO')
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
                SELECT            
                    [ID]
                    ,[FECHA_UTILIZACION]
                    ,[SERVICIO_UTILIZADO]
                    ,[UNIDAD_DE_MEDIDA]
                    ,[HORA_DE_INICIO]
                    ,[HORA_FINAL]
                    ,[CANTIDAD_UTILIZADA]
                    ,[JUSTIFICACION]
                    ,[RESPONSABLE]
                    ,[ORDEN_COMPRA]
                    ,tipo_equipo
                    ,[id_Sector]
                    --,[Activo]
                FROM Horas_Grua WHERE ACTIVO = 1
        """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def obtener_horas_grua(id_sector):
    try:
        if not id_sector:
            print("⚠️ No se pudo obtener el id_sector de la sesión.")
            return []
        else:
            print(f'el id para obtener ohoras gruas es')
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT            
                [ID],
                [FECHA_UTILIZACION],
                [SERVICIO_UTILIZADO],
                [UNIDAD_DE_MEDIDA],
                [HORA_DE_INICIO],
                [HORA_FINAL],
                [CANTIDAD_UTILIZADA],
                [JUSTIFICACION],
                [RESPONSABLE],
                [ORDEN_COMPRA],
                --[Activo],
                --[id_Sector],
                tipo_equipo
            FROM Horas_Grua
            WHERE ACTIVO = 1 AND id_sector = ?
        """, (id_sector,))
        
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        print("Error obteniendo horas de grúa:", e)
        return []


# ---------------- Eliminar un registro ----------------

from datetime import datetime

def eliminar_horas_grua(id):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    usuario = get_usuario_actual()
    concatenacion = f'Usuario: {usuario} - {fecha}'

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # UPDATE usando parámetros seguros
        cursor.execute("""
            UPDATE HORAS_GRUA
            SET ACTIVO = 0,
                USUARIO_ACTUALIZACION = ?
            WHERE id = ?
        """, (concatenacion, id))

        conn.commit()
        conn.close()
        print(f"Registro {id} eliminado correctamente.")

    except Exception as e:
        print("Error al eliminar:", e)




def verificar_orden_compra(orden_compra):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM HORAS_GRUA_ORDEN_COMPRA WHERE ORDEN_COMPRA = ? AND ACTIVO=1",
            orden_compra
        )
        count = cursor.fetchone()[0]
        conn.close()
        if count > 0:
            return True
        else:
            messagebox.showwarning("Aviso", "La orden de compra no existe en la base de datos.")
            return False
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo verificar la orden de compra:\n{str(e)}")
        return False  # Para evitar insertar si hubo error


def obtener_sectores():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ID_SECTOR,SECTOR FROM HORAS_GRUA_SECTORES")
    rows = cursor.fetchall()
    sectores = {row[1]: row[0] for row in rows}
    conn.close()
    return sectores
# x = obtener_sectores()
# print(x)
# ---------------- Actualizar un registro ----------------
def actualizar_horas_grua(FECHA_UTILIZACION, HORA_DE_INICIO,CANTIDAD_UTILIZADA,HORA_FINAL,JUSTIFICACION,RESPONSABLE,ORDEN_COMPRA,TIPO_EQUIPO,id):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    usuario = get_usuario_actual()
    concatenacion = f'Usuario: {usuario} -  {fecha}'
    try:
        if verificar_orden_compra(ORDEN_COMPRA):
            print("Orden de compra verificada, procediendo con la actualización...")
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE horas_grua SET FECHA_UTILIZACION = ?, HORA_DE_INICIO = ?, CANTIDAD_UTILIZADA =?,HORA_FINAL = ?,JUSTIFICACION=?,RESPONSABLE=?,orden_compra = ?,TIPO_EQUIPO=?,USUARIO_ACTUALIZACION = ? WHERE id = ?",
                FECHA_UTILIZACION, HORA_DE_INICIO,CANTIDAD_UTILIZADA,HORA_FINAL,JUSTIFICACION,RESPONSABLE,ORDEN_COMPRA,TIPO_EQUIPO,concatenacion,id
            )
            conn.commit()
            conn.close()
            print(f"Registro {id} actualizado correctamente.")
            messagebox.showinfo("Éxito", "✅ ¡Registro actualizado correctamente en la Base de Datos!")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo actualizar el registro:\n{str(e)}")
        print("Error al actualizar:", e)
        
        
# ---------------- Insertar un registro ----------------

def sobrepasa24horas(orden_compra, id_sector, tipo_equipo,fecha_utilizacion):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT SUM(DATEDIFF(MINUTE, HORA_DE_INICIO, HORA_FINAL)) / 60.0 as TotalHoras
            FROM HORAS_GRUA
            WHERE orden_compra = ? AND id_Sector = ? AND tipo_equipo = ? AND Activo = 1 AND FECHA_UTILIZACION = ?
            """,
            orden_compra, id_sector, tipo_equipo,fecha_utilizacion
        )
        total_horas = cursor.fetchone()[0] or 0
        conn.close()
        return total_horas > 24
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo verificar las horas utilizadas:\n{str(e)}")
        return False  # Para evitar insertar si hubo error

def existe_registro(datos):
    """
    Verifica si ya existe un registro idéntico en la tabla horas_grua
    Retorna True si existe, False si no
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT COUNT(*) FROM horas_grua
            WHERE FECHA_UTILIZACION = ?
              AND SERVICIO_UTILIZADO = ?
              AND UNIDAD_DE_MEDIDA = ?
              AND HORA_DE_INICIO = ?
              AND HORA_FINAL = ?
              AND CANTIDAD_UTILIZADA = ?
              AND ORDEN_COMPRA = ?
              AND Activo = 1
              AND TIPO_EQUIPO = ?
            """,
            datos["FECHA_UTILIZACION"],
            datos["SERVICIO_UTILIZADO"],
            datos["UNIDAD_DE_MEDIDA"],
            datos["HORA_DE_INICIO"],
            datos["HORA_FINAL"],
            datos["CANTIDAD_UTILIZADA"],
            datos["ORDEN_COMPRA"],
            datos["TIPO_EQUIPO"]
        )
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    except Exception as e:
        if 'date and/or' in e:
            messagebox.showerror("Error", f"No se pudo verificar, revisar la Fecha ingresada")
        else:   
            messagebox.showerror("Error", f"No se pudo verificar el registro:\n{str(e)}")
        return True  # Para evitar insertar si hubo error

def insertar_hora_grua(datos):
    """
    Inserta un registro en la tabla horas_grua si no existe previamente
    """
    if existe_registro(datos):
        messagebox.showwarning("Aviso", "Ya existe un registro idéntico en la base de datos.")
        return False
    if sobrepasa24horas(datos["ORDEN_COMPRA"], datos["ID_SECTOR"], datos["TIPO_EQUIPO"],datos["FECHA_UTILIZACION"]):
        messagebox.showwarning("Aviso", "La cantidad de horas utilizadas para esta orden de compra ya supera las 24 horas en el mismo día. No se puede agregar más horas para esta orden en este día.")
        return False

    try:
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        usuario = get_usuario_actual()
        concatenacion = f'Usuario: {usuario} -  {fecha}'
        conn = get_connection()
        cursor = conn.cursor()
        print('los datos que se van a insertar son ',datos)
        cursor.execute(
            """
            INSERT INTO horas_grua 
            (FECHA_UTILIZACION, SERVICIO_UTILIZADO, UNIDAD_DE_MEDIDA, HORA_DE_INICIO, HORA_FINAL, CANTIDAD_UTILIZADA, JUSTIFICACION, RESPONSABLE,ID_SECTOR,ORDEN_COMPRA,ACTIVO,USUARIO_ACTUALIZACION,TIPO_EQUIPO) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?,?,?,1,?,?)
            """,
            datos["FECHA_UTILIZACION"],
            datos["SERVICIO_UTILIZADO"],
            datos["UNIDAD_DE_MEDIDA"],
            datos["HORA_DE_INICIO"],
            datos["HORA_FINAL"],
            datos["CANTIDAD_UTILIZADA"],
            datos["JUSTIFICACION"],
            datos["RESPONSABLE"],
            datos["ID_SECTOR"],
            datos["ORDEN_COMPRA"],
            concatenacion,
            datos["TIPO_EQUIPO"]
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar el registro:\n{str(e)}")
        return False

def existe_orden(datos):
    """
    Verifica si ya existe una orden idéntico en la tabla horas_grua
    Retorna True si existe, False si no
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT COUNT(*) FROM HORAS_GRUA_ORDEN_COMPRA
            WHERE ORDEN_COMPRA = ? and CODIGO_PROVEEDOR = ? AND TIPO_EQUIPO = ?
              AND Activo = 1
            """,(
            datos["ORDEN_COMPRA"],
            datos["CODIGO_PROVEEDOR"],
            datos["TIPO_EQUIPO"]
            )
        )
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo verificar el registro:\n{str(e)}")
        return True  # Para evitar insertar si hubo error

def insertar_ORDEN_grua(datos):
    """
    Inserta un registro en la tabla horas_grua si no existe previamente
    """
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    usuario = get_usuario_actual()
    concatenacion = f'Usuario: {usuario} - {fecha}'
    if existe_orden(datos):
        messagebox.showwarning("Aviso", "Ya existe una orden idéntica en la base de datos.")
        return False

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO HORAS_GRUA_ORDEN_COMPRA 
            (FECHA, ID_SECTOR, ORDEN_COMPRA, CANTIDAD_HORAS,TIPO_EQUIPO,PROVEEDOR,CODIGO_PROVEEDOR,usuario_actualizacion,ACTIVO) 
            VALUES (?, ?, ?, ?, ?,?,?,?,1)
            """,
            datos["FECHA"],
            datos["ID_SECTOR"],
            datos["ORDEN_COMPRA"],
            datos["HORAS"],
            datos["TIPO_EQUIPO"],
            datos["PROVEEDOR"],
            datos["CODIGO_PROVEEDOR"],
            concatenacion
        )
        conn.commit()
        conn.close()
        return True
        messagebox.showinfo("Éxito", "✅ ¡Registro guardado correctamente en la Base de Datos!")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar el registro:\n{str(e)}")


def existe_orden_evaluacion(datos):
    """
    Verifica si ya existe una orden idéntico en la tabla horas_grua
    Retorna True si existe, False si no
    """
    try:   
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT COUNT(*) FROM HORAS_GRUA_evaluacion
            WHERE orden_info = ? and codigo_proveedor = ? AND TIPO_EQUIPO = ?
            """,(
            datos["ORDEN_COMPRA"],
            datos["CODIGO_PROVEEDOR"],
            datos["TIPO_EQUIPO"]
            )
        )
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo verificar el registro:\n{str(e)}")
        return True  # Para evitar insertar si hubo error

def insertar_orden_en_ficha(datos):
    """
    Inserta un registro en la tabla horas_grua si no existe previamente
    """
    print('ENTRE A INSERTAR ORDEN EN FICHA')
    try:
        if existe_orden_evaluacion(datos):
            #messagebox.showwarning("Aviso", "Ya existe una orden idéntica en la base de datos.")
            return False     
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO HORAS_GRUA_evaluacion 
            (nombre_proveedor, orden_info, horas_compra,completado,codigo_proveedor,tipo_equipo) 
            VALUES (?, ?, ?,'NO',?,?)
            """,
            datos["PROVEEDOR"],
            datos["ORDEN_COMPRA"],
            datos["HORAS"],
            datos["CODIGO_PROVEEDOR"],
            datos["TIPO_EQUIPO"]
        )
        conn.commit()
        conn.close()
        print("Registro guardado correctamente en la Base de Datos.")
    except Exception as e:
        print("Error al guardar el registro:\n", str(e))


def hhmm_a_decimal(hhmm):
    """Convierte 'HH:MM' a número decimal (horas)."""
    if not hhmm:
        return 0
    if isinstance(hhmm, (int, float)):
        return float(hhmm)
    if isinstance(hhmm, str):
        try:
            h, m = hhmm.split(":")
            return float(h) + float(m)/60
        except:
            # Si no tiene ':', intenta convertir directo
            return float(hhmm)
    return float(hhmm)


def horas_para_grafico(id_sector, orden_compra,datos,equipo = None):
    """"
    Verificar sino se ha pasado del 70% de horas disponibles
    """
    def validacion():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            f"""
            DECLARE @suma DECIMAL(10,2);
            DECLARE @total DECIMAL(10,2);
            DECLARE @resultado DECIMAL(10,4);
            DECLARE @disponible DECIMAL(10,2);
            DECLARE @horas INT;
            DECLARE @minutos INT;
            DECLARE @hhmm VARCHAR(10);

            -- Sumar las horas utilizadas (convertidas a decimal)
            SELECT @suma = SUM(DATEDIFF(MINUTE, CAST('00:00' AS TIME), cantidad_utilizada)) / 60.0
            FROM HORAS_GRUA
            WHERE id_Sector = {id_sector} AND orden_compra = '{orden_compra}' AND tipo_equipo = '{equipo}' AND Activo = 1;

            -- Cantidad total autorizada
            SELECT @total = cantidad_horas
            FROM HORAS_GRUA_ORDEN_COMPRA
            WHERE id_Sector = {id_sector} AND orden_compra = '{orden_compra}' AND tipo_equipo = '{equipo}' AND Activo = 1;

            -- Calcular proporción
            IF @total IS NOT NULL AND @total <> 0
                SET @resultado = @suma / @total;
            ELSE
                SET @resultado = 0;

            -- Disponible en decimal
            SET @disponible = ISNULL(@total,0) - ISNULL(@suma,0);

            -- Convertir disponible a HH:MM
            SET @horas = FLOOR(@disponible);
            SET @minutos = ROUND((@disponible - @horas) * 60,0);
            SET @hhmm = CONCAT(@horas, ':', RIGHT('0' + CAST(@minutos AS VARCHAR(2)), 2));

            -- Mostrar resultados
            SELECT 
                ISNULL(@suma,0) AS Total_Usado,
                ISNULL(@total,0) AS Total_Autorizado,
                ISNULL(@resultado,0) AS Proporcion_Usado,
                @disponible AS Disponible_Decimal,
                @hhmm AS Disponible_HHMM;
            """
        )
        row = cursor.fetchone()
        conn.commit()
        conn.close()
        if row is None:
            return None
        # nombres de columnas según tu SELECT
        columnas = ["Total_Usado", "Total_Autorizado", "Proporcion_Usado", "Disponible_Decimal", "Disponible_HHMM"]
        return dict(zip(columnas, row))
    try:
        c = validacion()
        print(c)
        return c
    except Exception as e:
        print("Error horas_para_grafico:", e)
        return None
    

def completado_orden(orden_compra,equipo):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"""
        select completado from HORAS_GRUA_evaluacion
        where orden_info = '{orden_compra}' and tipo_equipo = '{equipo}'
        """
    )
    result = cursor.fetchone()
    conn.commit()
    conn.close()
    return result.completado

def info_orden(orden_compra):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"""
        select nombre_proveedor, horas_compra, orden_info from HORAS_GRUA_evaluacion
        where orden_info = '{orden_compra}'
        """
    )
    result = cursor.fetchone()
    conn.commit()
    conn.close()
    return result


def obtener_proveedor_codigo(orden_compra,equipo):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"""
        select proveedor from HORAS_GRUA_ORDEN_COMPRA
        where orden_compra = '{orden_compra}'  and tipo_equipo = '{equipo}'
        """
    )
    result = cursor.fetchone()
    conn.commit()
    conn.close()
    if result:
        return result.proveedor
    else:
        return None

def obtener_datos_sectores(sector):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"""
        select SUPERVISOR,CENTRO_COSTO,sector from HORAS_GRUA_SECTORES
        where id_sector = '{sector}' 
        """
    )
    result = cursor.fetchone()
    conn.commit()
    conn.close()
    if not result:
        return None, None, None

    return result[0], result[1], result[2]

def obtener_responsable_sector(sector):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"""
        select RESPONSABLE from [HORAS_GRUA_RESPONSABLES_SECTORES]
        where id_sector = '{sector}' 
        """
    )
    rows  = cursor.fetchall()
    conn.commit()
    conn.close()
    # 👇 CONVERSIÓN CLAVE
    responsables = [str(row[0]) for row in rows]

    return responsables


def obtener_supervisor_sector(sector):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"""
        select SUPERVISOR from HORAS_GRUA_SECTORES
        where id_sector = '{sector}' 
        """
    )
    rows  = cursor.fetchall()
    conn.commit()
    conn.close()
    # 👇 CONVERSIÓN CLAVE
    responsables = [str(row[0]) for row in rows]

    return responsables

#ME FALTA VER LO DEL EQUIPO QUE NO SE DE DONDE SACARLO POR QUE TIENE QUE SER ESPECIFICO EL QUE TRAE YA

def actualizar_completado_orden(data):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        print('LOS DATOS QUE LLEGAN A ACTUALIZAR ORDEN SON ', data)

        # Extraer la orden (antes usabas .spit en lugar de .split)
        orden_info_raw = data.get("orden_info", "")
        orden_num = orden_info_raw.split(' - ', 1)[0].strip()

        # Preparar parámetros en el mismo orden de los placeholders "?"
        params = (
            data.get("servicio_tercerizado"),
            data.get("disponible"),
            data.get("sin_fallas"),
            # convertir a int si la columna es numérica; si no, dejar como string
            int(data.get("veces_no")) if str(data.get("veces_no")).isdigit() else data.get("veces_no"),
            data.get("especificaciones"),
            data.get("calificacion"),
            data.get("observaciones"),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            orden_num,
            data.get("tipo_equipo")
        )

        sql = """
        UPDATE HORAS_GRUA_evaluacion
        SET servicio_tercerizado = ?,
            disponible = ?,
            sin_fallas = ?,
            veces_no = ?,
            especificaciones = ?,
            calificacion = ?,
            observaciones = ?,
            fecha_completado = ?,
            completado = 'SI'
        WHERE orden_info = ? AND tipo_equipo = ?
        """

        cursor.execute(sql, params)
        conn.commit()

        # Opcional: comprobar filas afectadas
        if cursor.rowcount == 0:
            print("ATENCIÓN: la actualización no afectó filas. Verifica orden_info/tipo_equipo.")
            return False

        return True

    except Exception as e:
        # Aquí podrías usar logging en vez de print
        print("ERROR al actualizar orden:", type(e).__name__, e)
        if conn:
            conn.rollback()
        return False

    finally:
        if conn:
            conn.close()
            
def validacion_(id_sector, orden_compra):
    conn = get_connection()
    cursor = conn.cursor()

    es_admin = obtener_rol() == "admin"

    sql = """
    DECLARE @suma DECIMAL(10,2);
    DECLARE @total DECIMAL(10,2);
    DECLARE @resultado DECIMAL(10,4);
    DECLARE @disponible DECIMAL(10,2);
    DECLARE @horas INT;
    DECLARE @minutos INT;
    DECLARE @hhmm VARCHAR(10);

    -- Sumar horas utilizadas
    SELECT @suma =
        SUM(DATEDIFF(MINUTE, '00:00', cantidad_utilizada)) / 60.0
    FROM HORAS_GRUA
    WHERE orden_compra = ?
      AND Activo = 1
    """

    params = [orden_compra]

    if not es_admin:
        sql += " AND id_Sector = ?"
        params.append(id_sector)

    sql += """

    -- Total autorizado
    SELECT @total = cantidad_horas
    FROM HORAS_GRUA_ORDEN_COMPRA
    WHERE orden_compra = ?
      AND Activo = 1
    """

    params.append(orden_compra)

    if not es_admin:
        sql += " AND id_Sector = ?"
        params.append(id_sector)

    sql += """

    -- Proporción
    IF @total IS NOT NULL AND @total <> 0
        SET @resultado = @suma / @total;
    ELSE
        SET @resultado = 0;

    -- Disponible
    SET @disponible = ISNULL(@total,0) - ISNULL(@suma,0);

    -- Convertir a HH:MM seguro
    SET @horas = FLOOR(@disponible);
    SET @minutos = FLOOR((@disponible - @horas) * 60);

    IF @minutos = 60
    BEGIN
        SET @horas = @horas + 1;
        SET @minutos = 0;
    END

    SET @hhmm = CONCAT(@horas, ':', RIGHT('0' + CAST(@minutos AS VARCHAR(2)), 2));

    SELECT
        ISNULL(@suma,0) AS Total_Usado,
        ISNULL(@total,0) AS Total_Autorizado,
        ISNULL(@resultado,0) AS Proporcion_Usado,
        @disponible AS Disponible_Decimal,
        @hhmm AS Disponible_HHMM;
    """

    cursor.execute(sql, params)
    row = cursor.fetchone()

    conn.close()

    return row.Disponible_HHMM if row else "0:00"


def validacion_admin(orden_compra,equipo):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"""
        DECLARE @suma DECIMAL(10,2);
        DECLARE @total DECIMAL(10,2);
        DECLARE @resultado DECIMAL(10,4);
        DECLARE @disponible DECIMAL(10,2);
        DECLARE @horas INT;
        DECLARE @minutos INT;
        DECLARE @hhmm VARCHAR(10);

        -- Sumar las horas utilizadas (convertidas a decimal)
        SELECT @suma = SUM(DATEDIFF(MINUTE, CAST('00:00' AS TIME), cantidad_utilizada)) / 60.0
        FROM HORAS_GRUA
        WHERE  orden_compra = '{orden_compra}' AND Activo = 1 AND tipo_equipo = '{equipo}';

        -- Cantidad total autorizada
        SELECT @total = cantidad_horas
        FROM HORAS_GRUA_ORDEN_COMPRA
        WHERE  orden_compra = '{orden_compra}' AND Activo = 1 AND tipo_equipo = '{equipo}';

        -- Calcular proporción
        IF @total IS NOT NULL AND @total <> 0
            SET @resultado = @suma / @total;
        ELSE
            SET @resultado = 0;

        -- Disponible en decimal
        SET @disponible = ISNULL(@total,0) - ISNULL(@suma,0);

        -- Convertir disponible a HH:MM
        SET @horas = FLOOR(@disponible);
        SET @minutos = ROUND((@disponible - @horas) * 60,0);
        SET @hhmm = CONCAT(@horas, ':', RIGHT('0' + CAST(@minutos AS VARCHAR(2)), 2));

        -- Mostrar resultados
        SELECT 
            ISNULL(@suma,0) AS Total_Usado,
            ISNULL(@total,0) AS Total_Autorizado,
            ISNULL(@resultado,0) AS Proporcion_Usado,
            @disponible AS Disponible_Decimal,
            @hhmm AS Disponible_HHMM;
        """
    )
    result = cursor.fetchone()
    conn.commit()
    conn.close()
    return result.Disponible_HHMM


def validar_horas_disponibles(id_sector, orden_compra,datos):
    """"
    Verificar sino se ha pasado del 70% de horas disponibles
    """
    equipo = datos['TIPO_EQUIPO']
    def validacion():
        conn = get_connection()
        cursor = conn.cursor()

        es_admin = obtener_rol() == 'admin'

        sql = """
        DECLARE @suma DECIMAL(10,2);
        DECLARE @total DECIMAL(10,2);
        DECLARE @resultado DECIMAL(10,4);
        DECLARE @disponible DECIMAL(10,2);
        DECLARE @horas INT;
        DECLARE @minutos INT;
        DECLARE @hhmm VARCHAR(10);

        SELECT @suma =
            SUM(DATEDIFF(MINUTE, '00:00', cantidad_utilizada)) / 60.0
        FROM HORAS_GRUA
        WHERE orden_compra = ?
        AND tipo_equipo = ?
        AND Activo = 1
        """

        params = [orden_compra, equipo]

        if not es_admin:
            sql += " AND id_Sector = ?"
            params.append(id_sector)

        sql += """

        SELECT @total = cantidad_horas
        FROM HORAS_GRUA_ORDEN_COMPRA
        WHERE orden_compra = ?
        AND tipo_equipo = ?
        AND Activo = 1
        """

        params.extend([orden_compra, equipo])

        if not es_admin:
            sql += " AND id_Sector = ?"
            params.append(id_sector)

        sql += """

        IF @total IS NOT NULL AND @total <> 0
            SET @resultado = @suma / @total;
        ELSE
            SET @resultado = 0;

        SET @disponible = ISNULL(@total,0) - ISNULL(@suma,0);

        SET @horas = FLOOR(@disponible);
        SET @minutos = FLOOR((@disponible - @horas) * 60);

        IF @minutos = 60
        BEGIN
            SET @horas = @horas + 1;
            SET @minutos = 0;
        END

        SET @hhmm = CONCAT(@horas, ':', RIGHT('0' + CAST(@minutos AS VARCHAR(2)), 2));

        SELECT
            ISNULL(@suma,0) AS Total_Usado,
            ISNULL(@total,0) AS Total_Autorizado,
            ISNULL(@resultado,0) AS Proporcion_Usado,
            @disponible AS Disponible_Decimal,
            @hhmm AS Disponible_HHMM;
        """

        cursor.execute(sql, params)
        result = cursor.fetchone()

        conn.close()
        return result

    try:
        resultado = validacion()
        completo = completado_orden(orden_compra,equipo)
        proporcion = float(resultado.Proporcion_Usado)
        print("Resultado de la validación:", resultado)
        print("Proporción usada:", proporcion)
        print("Completado orden:", completo)
        
        if proporcion >=0.7 and completo == 'NO':
            messagebox.showerror("Error", "Debe completar la evaluación de la orden de compra antes de registrar más horas.")
            return ['completar','insertar_datos']
        
        
        if resultado and resultado.Proporcion_Usado is not None:
            print(f"Proporción usada: {proporcion:.4f}")
            if proporcion > 1:
                messagebox.showerror("Error", "Ha excedido las horas disponibles en este sector y orden de compra. No se puede registrar más horas.")
                return False
            hora_dispo = hhmm_a_decimal(resultado.Disponible_HHMM)
            cantidad = hhmm_a_decimal(datos["CANTIDAD_UTILIZADA"])
            print(datos["CANTIDAD_UTILIZADA"], resultado.Disponible_HHMM,cantidad,hora_dispo)
            if  cantidad > hora_dispo:
                print(f"Cantidad a registrar: {datos['CANTIDAD_UTILIZADA']}, Disponible: {resultado.Disponible_Decimal}")
                messagebox.showerror("Error", f"La cantidad de horas a registrar ({datos['CANTIDAD_UTILIZADA']} h) excede las horas disponibles ({resultado.Disponible_HHMM} h) para esta orden de compra.")
                return False
            if proporcion >= 0.7 and int(proporcion) <1:
                if insertar_hora_grua(datos): 
                    # print("Registro insertado, verificando correo..."  )           
                    # if correo_enviado(id_sector, orden_compra,equipo):
                    #     resultado = validacion()
                    #     print('el resultaod es',resultado)
                    resultado = validacion()
                    messagebox.showinfo(
                        "Éxito",
                        f"✅ Registro guardado correctamente! "
                        f"Quedan menos del 70% de horas disponibles ({resultado.Disponible_HHMM} h) "
                        f"para la orden de compra {orden_compra}-{equipo}. "
                        f"El correo de notificación ya se ha enviado para esta orden."
                    )
                    if resultado.Proporcion_Usado == 1:
                        messagebox.showwarning("Advertencia","Ha alcanzado el 100% de las horas disponibles en este sector y orden de compra. No se pueden registrar más horas.")
                    return False
                    # else:
                    #     resultado = validacion()
                    #     print(f'voy a enviar correo nuevo {resultado}')
                    #     messagebox.showinfo(
                    #         "Éxito",
                    #         f"✅ Registro guardado correctamente! ")
                    #     messagebox.showinfo("Aviso", "Ha alcanzado el 70% de las horas disponibles en este sector y orden de compra. Se enviará un correo de notificación.")
                    #     insertado = insertar_correo(id_sector, orden_compra,equipo)
                    #     return insertado
            if proporcion < 0.7:
                if insertar_hora_grua(datos):
                    resultado = validacion()
                    print('el resulrado anes de propocuon es',resultado)
                    messagebox.showinfo(
                        "Éxito",
                        f"✅ Registro guardado correctamente! "
                        f"Quedan {resultado.Disponible_HHMM} h disponibles para la orden de compra {orden_compra}."
                    )
                    if resultado.Proporcion_Usado >= 0.7:
                        return ['validar_correo',resultado]
                        # if correo_enviado(id_sector, orden_compra,equipo):
                        #     messagebox.showinfo("Aviso", "Quedan menos del 70% de horas disponibles, el correo de notificación ya se ha enviado para esta orden.")
                        #     if resultado.Proporcion_Usado == 1:
                        #         messagebox.showwarning("Advertencia","Ha alcanzado el 100% de las horas disponibles en este sector y orden de compra. No se pueden registrar más horas.")
                        #     return False
                        # else:
                        #     messagebox.showwarning("Advertencia", "⚠️ Ha alcanzado el 70% de las horas disponibles en este sector y orden de compra. Se enviará un correo de notificación.")
                        #     #insertado = insertar_correo(id_sector, orden_compra,equipo)
                        #     #print('el insertado es',insertado)
                        #     return True
                    else:
                        return False
            else:
                if resultado.Proporcion_Usado == 1:
                    messagebox.showwarning("Advertencia","Ha alcanzado el 100% de las horas disponibles en este sector y orden de compra. No se pueden registrar más horas.")
                return False
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo validar las horas disponibles:\n{str(e)}")
        return False
    
def correo_enviado(id_sector, orden_compra,equipo):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            f"""
            SELECT * FROM HORAS_GRUA_CORREO WHERE id_Sector = {id_sector}  and orden_compra = {orden_compra} and tipo_equipo = '{equipo}'
            """
        )
        result = cursor.fetchone()
        print("Resultado de la consulta de correo:", result)
        conn.commit()
        conn.close()

        
        
        if result:
            print(f"Correo marcado como enviado para sector {id_sector} y orden {orden_compra} - {equipo}.")
            return True  # Ya se envió correo
        else:
            print('el correo no ha sido enviado')
            return False  # No se ha enviado correo
    except Exception as e:
        print("Error al validar si ya se envió correo:", e)

def insertar_correo(id_sector, orden_compra,equipo):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            f"""
            INSERT INTO HORAS_GRUA_CORREO (ID_SECTOR, ORDEN_COMPRA, CORREO,tipo_equipo) 
            VALUES (?, ?, 1,?)
            """,
            id_sector,
            orden_compra,
            equipo
        )
        conn.commit()
        conn.close()
        return True  # Correo marcado como enviado
    except Exception as e:
        print("Error al marcar correo como enviado:", e)
        messagebox.showerror("Error", f"No se pudo registrar en la base de datos el correo:\n{str(e)}")
        return False




    # ------------------- OBTENER CC PARA CORREO -------------
def obtener_cc():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Agregamos comillas simples a 'Todos' porque es un valor de texto en SQL
    query = "SELECT correo FROM Horas_grua_personas_correo WHERE sector = 'todos'"
    
    cursor.execute(query)
    
    # 2. Extraemos solo el string del correo de cada tupla en el resultado
    # fetchall() devuelve una lista de tuplas como [('correo1@hn',), ('correo2@hn',)]
    resultado = cursor.fetchall()
    cc_correo = [fila[0] for fila in resultado]
    
    cursor.close()
    conn.close()
    
    return cc_correo

def obtener_correo(id):
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Agregamos comillas simples a 'Todos' porque es un valor de texto en SQL
    query = f"SELECT correo FROM Horas_grua_personas_correo WHERE id  = {id}"
    
    cursor.execute(query)
    
    # 2. Extraemos solo el string del correo de cada tupla en el resultado
    # fetchall() devuelve una lista de tuplas como [('correo1@hn',), ('correo2@hn',)]
    resultado = cursor.fetchall()
    cc_correo = [fila[0] for fila in resultado]
    
    cursor.close()
    conn.close()
    
    return cc_correo
    # ------------------- OBTENER SECTOR -------------------

def sector_id(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT SECTOR FROM HORAS_GRUA_SECTORES where ID_SECTOR={id}")
    resultado = cursor.fetchone()
    conn.close()
    return resultado

# ---------------- Funciones para la tabla HORAS_GRUA_ORDEN_COMPRA 
# -----------------------------------------------------------
# OBTENER ORDEN DE COMPRA POR SECTOR
# -----------------------------------------------------------
import pandas as pd
def obtener_orden_compra(id_sector):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        rol = obtener_rol()
        if rol == 'admin':
            print('es admin')
            cursor.execute("""
                SELECT orden_compra,tipo_equipo
                FROM horas_grua_orden_compra
                WHERE activo = 1
            """)
        else:
            cursor.execute("""
                SELECT orden_compra,tipo_equipo
                FROM horas_grua_orden_compra
                WHERE id_sector = ?
                and activo = 1
            """, (id_sector,))
        rows = cursor.fetchall()
        conn.close()
        print('las rows son',rows)
        # Convertimos en lista simple (no diccionarios)
        data = [{"orden_compra": row[0], "tipo_equipo": row[1]} for row in rows]
        df = pd.DataFrame(data)
        return df

    except Exception as e:
        print("Error obteniendo orden de compra:", e)
        return []


# d = obtener_orden_compra(2)
# print(d['orden_compra'].tolist())
def obtener_orden_compra_completo():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT orden_compra
            FROM horas_grua_orden_compra
            where activo = 1
        """)
        rows = cursor.fetchall()
        conn.close()

        # Convertimos en lista simple (no diccionarios)
        data = [row[0] for row in rows]
        return data

    except Exception as e:
        print("Error obteniendo orden de compra:", e)
        return []

def obtener_orden_compra_activos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM HORAS_GRUA_ORDEN_COMPRA")
    rows = cursor.fetchall()
    conn.close()
    return rows

def obtener_orden_compra_activos_todas_ordenes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT orden_compra FROM HORAS_GRUA_ORDEN_COMPRA")
    rows = cursor.fetchall()
    lista = [str(row[0]) for row in rows]
    conn.close()
    return lista

def eliminar_orden_compra(id_sector):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    usuario = get_usuario_actual()
    concatenacion = f'Usuario: {usuario} - {fecha}'

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # UPDATE usando parámetros seguros
        cursor.execute("""
            UPDATE HORAS_GRUA_ORDEN_COMPRA
            SET ACTIVO = 0,
                USUARIO_ACTUALIZACION = ?
            WHERE id = ?
        """, (concatenacion, id_sector))

        conn.commit()
        conn.close()
        messagebox.showinfo("Exito","Registro eliminado")
        print(f"Registro {id_sector} eliminado correctamente.")

    except Exception as e:
        messagebox.showerror("Error", "Error al eliminar")
        print("Error al eliminar:", e)

def actualizar_orden_compra(FECHA, ID_SECTOR, ORDEN_COMPRA, CANTIDAD_HORAS, TIPO_EQUIPO, ACTIVO, orden_original):
    try:
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        usuario = get_usuario_actual()
        concatenacion = f'Usuario: {usuario} -  {fecha}'
        print(f"Actualizando orden {orden_original} con fecha {FECHA} y sector {ID_SECTOR}")
        
        # Asegurarse de tipos correctos
        ID_SECTOR = int(ID_SECTOR)
        CANTIDAD_HORAS = int(CANTIDAD_HORAS)
        ACTIVO = int(ACTIVO)
        ORDEN_COMPRA = str(ORDEN_COMPRA)
        orden_original = str(orden_original)
        TIPO_EQUIPO = str(TIPO_EQUIPO)
        FECHA = str(FECHA)  # o datetime.date compatible

        conn = get_connection()
        cursor = conn.cursor()

        usuario_actual = concatenacion

        sql = """
        UPDATE HORAS_GRUA_ORDEN_COMPRA
        SET FECHA = ?, 
            ID_SECTOR = ?, 
            ORDEN_COMPRA = ?, 
            CANTIDAD_HORAS = ?, 
            TIPO_EQUIPO = ?, 
            ACTIVO = ?, 
            USUARIO_ACTUALIZACION = ?
        WHERE ORDEN_COMPRA = ?
        """

        valores = (
            FECHA,
            ID_SECTOR,
            ORDEN_COMPRA,
            CANTIDAD_HORAS,
            TIPO_EQUIPO,
            ACTIVO,
            usuario_actual,
            orden_original
        )

        cursor.execute(sql, valores)

        sql_2 = """
        UPDATE HORAS_GRUA
        SET ORDEN_COMPRA = ?, 
            USUARIO_ACTUALIZACION = ?
        WHERE ORDEN_COMPRA = ?
        """

        valores_2 = (
            ORDEN_COMPRA,
            usuario_actual,
            orden_original
        )    
        cursor.execute(sql_2, valores_2)
        conn.commit()
        conn.close()

        print(f"✅ Registro {orden_original} actualizado correctamente.")
        messagebox.showinfo("Éxito", "✅ ¡Registro actualizado correctamente en la Base de Datos!")

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo actualizar el registro:\n{str(e)}")
        print("❌ Error al actualizar:", e)



