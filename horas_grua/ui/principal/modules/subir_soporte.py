import os
import base64
import requests
from tkinter import messagebox, filedialog, Tk

# URLs de Power Automate (asegúrate que tus flujos estén activados)
def links_flows():
    retorno = {}
    retorno['FLOW_CREATE_FOLDER'] = "https://defaultc1b22713e01544978af7ac76803fda.c5.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/f4f0e6b7cb434d92b87c2d1ca5f8938b/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=oUOqUECnj2kK705yHSrA9xNMvgjgP2muX0k5zUkgFWY"
    retorno['FLOW_UPLOAD_FILE'] = "https://defaultc1b22713e01544978af7ac76803fda.c5.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/ecbf32c567c5427ea50f28270f4f3b5f/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=DXdDtmE5iYZpvdy0ZaqDjuN7nkt4azpY-1G2mAvPCOA"
    return retorno



def seleccionar_archivos():
    """Abre un cuadro de diálogo para seleccionar archivos múltiples."""
    root = Tk()
    root.withdraw()  # Oculta la ventana principal de Tkinter
    rutas = filedialog.askopenfilenames(
        title="Selecciona los archivos que deseas subir",
        filetypes=[("Todos los archivos", "*.*")]
    )
    root.destroy()
    return list(rutas)


def verificar_carpeta_sharepoint(selected_files,carpeta_inicial, sector, carpeta_año, carpeta_mes, carpeta_nombre):
    """Verifica o crea la carpeta y luego sube los archivos seleccionados."""

    FLOW_LINKS = links_flows()
    FLOW_CREATE_FOLDER = FLOW_LINKS['FLOW_CREATE_FOLDER']
    FLOW_UPLOAD_FILE = FLOW_LINKS['FLOW_UPLOAD_FILE']
    payload_folder = {
        "sector": sector,
        "mes": carpeta_mes,
        "carpeta_final": carpeta_nombre,
        "carpeta_inicial": carpeta_inicial
    }

    headers = {"Content-Type": "application/json"}

    try:
        response_folder = requests.post(FLOW_CREATE_FOLDER, json=payload_folder, headers=headers)

        if response_folder.status_code == 200:
            print("✅ Carpeta creada o ya existente. Llamando a subir archivos...")
            subir_archivos_sharepoint(selected_files,carpeta_inicial, sector, carpeta_año, carpeta_mes, carpeta_nombre, headers,FLOW_UPLOAD_FILE)
        else:
            print("❌ Error al crear carpeta:", response_folder.text)
            messagebox.showerror("Error", f"No se pudo crear la carpeta:\n{response_folder.text}")
    except Exception as e:
        messagebox.showerror("Error", f"Error al conectar con PO:\n{str(e)}") #PO es Power Automate


def subir_archivos_sharepoint(selected_files,carpeta_inicial, sector, carpeta_año, carpeta_mes, carpeta_nombre, headers,FLOW_UPLOAD_FILE):
    """Sube los archivos seleccionados a SharePoint usando un flujo Power Automate."""
    if not selected_files:
        messagebox.showwarning("Advertencia", "No se seleccionaron archivos para subir.")
        return
    
    errores = []
    exitos = 0

    for archivo in selected_files:
        try:
            with open(archivo, "rb") as f:
                file_bytes = f.read()
                file_base64 = base64.b64encode(file_bytes).decode("utf-8")
            
            payload_file = {
                "folderPath": f"Documentos compartidos/{carpeta_inicial}/{sector}/{carpeta_año}/{carpeta_mes}/{carpeta_nombre}",
                "filename": os.path.basename(archivo),
                "filecontent": file_base64
            }

            response_file = requests.post(FLOW_UPLOAD_FILE, json=payload_file, headers=headers)

            if response_file.status_code == 200:
                exitos += 1
                print(f"✅ Archivo subido: {os.path.basename(archivo)}")
            else:
                errores.append(f"{os.path.basename(archivo)} → {response_file.text}")

        except Exception as e:
            errores.append(f"{os.path.basename(archivo)} → {str(e)}")

    if errores:
        print("❌ Algunos archivos no se pudieron subir:", errores)
        messagebox.showerror(
            "Errores al subir archivos",
            f"Se subieron {exitos} archivos, pero ocurrieron errores:\n\n" + "\n".join(errores)
        )
    else:
        messagebox.showinfo("Éxito", f"Todos los archivos ({exitos}) fueron subidos correctamente.")


# === Punto de inicio del script ===
# if __name__ == "__main__":
    # carpeta_nombre = 'carpeta'
    # carpeta_mes = 'abril'
    # sector = 'tegus'
    # carpeta_inicial = 'HORAS_GRUA'
#     archivos = seleccionar_archivos()
#     if archivos:
#         verificar_carpeta_sharepoint(archivos, carpeta_inicial, sector, carpeta_mes, carpeta_nombre)
#     else:
#         messagebox.showinfo("Información", "No se seleccionaron archivos.")
