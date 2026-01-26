import customtkinter as ctk
from tkinter import messagebox
from tkinter import Toplevel
from tkcalendar import Calendar
from datetime import datetime
from tkinter.filedialog import askopenfilename
import sys
import os

# Ajustar path para importar db_controller y pdf
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from db_controller import insertar_ORDEN_grua, obtener_sectores, insertar_orden_en_ficha
from ui.principal.modules.pdf import procesar_pdf   # <<=== IMPORTANTE


class ordencompra(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="white")

        # ---- Inicializaciones para manejo de PDF / ítems ----
        self.items_pdf = []          # lista de items extraídos del PDF
        self.items_guardados = set() # índices ya guardados
        self.index_actual = None     # índice del item actualmente cargado
        self.pdf = None              # ruta del PDF actual
        self.pdf_subido = False      # para subir soporte solo una vez

        self.index_actual = 0
        # Diccionario sector → código
        self.sectores = obtener_sectores()
        
        self.activo = {"Activo": 1, "Inactivo": 0}

        # --- TÍTULO ---
        ctk.CTkLabel(
            self, text="Registrar Horas de Grúa 🏗️",
            font=("TT NORMS PRO", 24, "bold"), text_color="#01091F"
        ).pack(pady=(30,20))

        form_frame = ctk.CTkFrame(self, fg_color="white")
        form_frame.pack(expand=True)

        # =============== CAMPOS ===============

        # FECHA
        ctk.CTkLabel(
            form_frame, text="FECHA:",
            font=("TT NORMS PRO",14,"bold"), text_color="#87898F"
        ).grid(row=1, column=0, sticky="e", padx=10, pady=8)
        self.fecha_entry = ctk.CTkEntry(
            form_frame, placeholder_text="YYYY-MM-DD",
            width=250, fg_color="#EFEFEF", text_color="black"
        )
        self.fecha_entry.grid(row=1, column=1, sticky="w", padx=10, pady=8)
        ctk.CTkButton(
            form_frame, text="📅", width=30,
            fg_color="#5E95FF", hover_color="#4780E0",
            command=self.abrir_calendario
        ).grid(row=1, column=2, sticky="w", padx=5)

        # HORAS
        ctk.CTkLabel(
            form_frame, text="HORAS:",
            font=("TT NORMS PRO",14,"bold"), text_color="#87898F"
        ).grid(row=2, column=0, sticky="e", padx=10, pady=8)
        self.hora_inicio = ctk.CTkEntry(
            form_frame, placeholder_text="cantidad de horas",
            width=250, fg_color="#EFEFEF", text_color="black"
        )
        self.hora_inicio.grid(row=2, column=1, columnspan=2, sticky="w", padx=10, pady=8)

        # ORDEN
        ctk.CTkLabel(
            form_frame, text="ORDEN DE COMPRA:",
            font=("TT NORMS PRO",14,"bold"), text_color="#87898F"
        ).grid(row=6, column=0, sticky="e", padx=10, pady=8)
        self.orden_entry = ctk.CTkEntry(
            form_frame, placeholder_text="orden",
            width=250, fg_color="#EFEFEF", text_color="black"
        )
        self.orden_entry.grid(row=6, column=1, columnspan=2, sticky="w", padx=10, pady=8)

        # SECTOR
        ctk.CTkLabel(
            form_frame, text="SECTOR:",
            font=("TT NORMS PRO",14,"bold"), text_color="#87898F"
        ).grid(row=4, column=0, sticky="e", padx=10, pady=8)
        self.sector_combo = ctk.CTkComboBox(
            form_frame, values=list(self.sectores.keys()),
            width=250, fg_color="#EFEFEF", text_color="black"
        )
        self.sector_combo.grid(row=4, column=1, columnspan=2, sticky="w", padx=10, pady=8)

        # TIPO EQUIPO
        ctk.CTkLabel(
            form_frame, text="TIPO DE EQUIPO:",
            font=("TT NORMS PRO",14,"bold"), text_color="#87898F"
        ).grid(row=7, column=0, sticky="e", padx=10, pady=8)
        self.equipo = ctk.CTkComboBox(
            form_frame, values=["GRUA","CANASTA"],
            width=250, fg_color="#EFEFEF", text_color="black"
        )
        self.equipo.grid(row=7, column=1, columnspan=2, sticky="w", padx=10, pady=8)

        # PROVEEDOR
        ctk.CTkLabel(
            form_frame, text="PROVEEDOR:",
            font=("TT NORMS PRO",14,"bold"), text_color="#87898F"
        ).grid(row=9, column=0, sticky="e", padx=10, pady=8)
        self.proveedor_entry = ctk.CTkEntry(
            form_frame, placeholder_text="proveedor",
            width=250, fg_color="#EFEFEF", text_color="black"
        )
        self.proveedor_entry.grid(row=9, column=1, columnspan=2, sticky="w", padx=10, pady=8)

        # CÓDIGO PROVEEDOR
        ctk.CTkLabel(
            form_frame, text="CODIGO PROVEEDOR:",
            font=("TT NORMS PRO",14,"bold"), text_color="#87898F"
        ).grid(row=10, column=0, sticky="e", padx=10, pady=8)
        self.codigo_proveedor_entry = ctk.CTkEntry(
            form_frame, placeholder_text="codigo_proveedor",
            width=250, fg_color="#EFEFEF", text_color="black"
        )
        self.codigo_proveedor_entry.grid(row=10, column=1, columnspan=2, sticky="w", padx=10, pady=8)

        # =============== BOTÓN PDF ===============
        self.btn_pdf = ctk.CTkButton(
            form_frame,
            text="📄 Leer PDF",
            font=("TT NORMS PRO", 16, "bold"),
            fg_color="#D5DDEB",
            hover_color="#AEB5E4",
            text_color="#0C92A9",
            width=150,
            height=40,
            command=self.cargar_pdf
        )
        self.btn_pdf.grid(row=11, column=0, pady=15)

        # =============== BOTONES PRINCIPALES ===============
        self.btn_guardar = ctk.CTkButton(
            form_frame,
            text="💾 Guardar",
            font=("TT NORMS PRO",16,"bold"),
            fg_color="#5FD0DF", text_color='white',
            hover_color="#56C0CE",
            command=self.guardar_registro,
            width=150, height=40
        )
        self.btn_guardar.grid(row=12, column=2, pady=30)

        self.btn_borrar = ctk.CTkButton(
            form_frame,
            text="Borrar Todo",
            font=("TT NORMS PRO",16,"bold"),
            fg_color="#F1F1F4", text_color='#616161',
            hover_color="#EFF0F8",
            command=self.borrar_todo,
            width=150, height=40
        )
        self.btn_borrar.grid(row=12, column=1, pady=30)

    # =========================================================
    # FUNCIÓN PARA CARGAR PDF
    # =========================================================
    def cargar_pdf(self):
        pdf_path = askopenfilename(
            title="Seleccionar orden de compra PDF",
            filetypes=[("Archivos PDF", "*.pdf")]
        )

        if not pdf_path:
            return

        items = procesar_pdf(pdf_path)
        if not items:
            messagebox.showerror("Error", "No se encontraron datos en el PDF.")
            return

        # --- Reiniciamos estado asociado a este PDF ---
        self.items_pdf = items
        self.pdf = pdf_path
        self.index_actual = None
        self.items_guardados = set()
        self.pdf_subido = False

        # Si hay más de un item → seleccionar cuál cargar primero
        if len(items) > 1:
            self.abrir_selector_items()
        else:
            self.index_actual = 0
            self.cargar_item(0)

    # =========================================================
    # SELECCIONAR ITEM
    # =========================================================
    def abrir_selector_items(self):
        win = Toplevel(self)
        win.title("Seleccionar orden del PDF")
        win.geometry("450x350")
        win.configure(bg="#1E1E2F")
        win.grab_set()

        # Título
        ctk.CTkLabel(
            win,
            text="Seleccione el registro a cargar primero",
            font=("TT NORMS PRO", 18, "bold"),
            text_color="#A8C0FF"
        ).pack(pady=(20, 10))

        # Frame contenedor de botones
        frame = ctk.CTkFrame(win, fg_color="#2B2B3A", corner_radius=15)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        for i, item in enumerate(self.items_pdf):
            texto = f"{item['equipo']} — {item['hora_inicio']} horas"
            btn = ctk.CTkButton(
                frame,
                text=texto,
                fg_color="#3A3A5A",
                hover_color="#5E5EC0",
                text_color="white",
                font=("TT NORMS PRO", 14, "bold"),
                corner_radius=10,
                height=45,
                command=lambda idx=i, w=win: self.seleccionar_item(idx, w)
            )
            btn.pack(pady=10, padx=10, fill="x")

        # Botón cancelar opcional
        ctk.CTkButton(
            win,
            text="Cancelar",
            fg_color="#D9534F",
            hover_color="#C9302C",
            text_color="white",
            font=("TT NORMS PRO", 14, "bold"),
            corner_radius=10,
            command=win.destroy
        ).pack(pady=(0, 20))

    def seleccionar_item(self, index, ventana):
        ventana.destroy()
        self.index_actual = index
        self.cargar_item(index)

    # =========================================================
    # CARGAR CAMPOS DE UN ITEM
    # =========================================================
    def cargar_item(self, index):
        item = self.items_pdf[index]

        self.fecha_entry.delete(0, "end")
        self.fecha_entry.insert(0, item.get("fecha_str", ""))

        self.hora_inicio.delete(0, "end")
        self.hora_inicio.insert(0, item.get("hora_inicio", ""))

        self.orden_entry.delete(0, "end")
        self.orden_entry.insert(0, item.get("orden_entry", ""))

        self.equipo.set(item.get("equipo", "").upper())

        self.proveedor_entry.delete(0, "end")
        self.proveedor_entry.insert(0, item.get("proveedor", ""))

        self.codigo_proveedor_entry.delete(0, "end")
        self.codigo_proveedor_entry.insert(0, item.get("codigo_proveedor", ""))

        # Mapear sector
        sector_pdf = item.get("codigo_sector", "").upper()
        for nombre_sector in self.sectores:
            if sector_pdf in nombre_sector.upper():
                self.sector_combo.set(nombre_sector)
                break

        # messagebox.showinfo("OK", f"Se cargó el registro de {item['equipo']}.")

    # =========================================================
    # CARGAR SIGUIENTE ITEM SI EXISTE
    # =========================================================
    def cargar_siguiente_item_si_hay(self):
        """
        Si hay otro ítem del PDF que aún no se ha guardado,
        lo carga automáticamente en el formulario.
        """
        if not self.items_pdf:
            return
        
        print("Items PDF:", len(self.items_pdf))
        print("Items guardados:", len(self.items_guardados))
        # ¿quedan ítems pendientes?
        if len(self.items_pdf) <= len(self.items_guardados):
            # Ya no hay más
            # messagebox.showinfo("Listo", "Se procesaron todos los registros del PDF.")
            return

        # Buscar el primer índice que no esté guardado
        for i in range(len(self.items_pdf)):
            if i not in self.items_guardados:
                messagebox.showinfo(
                    "Cargando siguiente",
                    "Este PDF tiene otro registro.\nNo es necesario volver a cargar, Dar clic en guardar nuevamente"
                )
                self.index_actual = i
                self.cargar_item(i)
                return


    # ventana de cargando
    
    def mostrar_cargando(self, texto="Procesando, por favor espere..."):
        self.win_loading = Toplevel(self)
        self.win_loading.title("Procesando")
        self.win_loading.geometry("350x120")
        self.win_loading.configure(bg="#1E1E2F")
        self.win_loading.transient(self)
        self.win_loading.grab_set()
        self.win_loading.resizable(False, False)

        # Centrar ventana
        x = self.winfo_screenwidth() // 2 - 175
        y = self.winfo_screenheight() // 2 - 60
        self.win_loading.geometry(f"+{x}+{y}")

        frame = ctk.CTkFrame(self.win_loading, fg_color="#1E1E2F")
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(
            frame,
            text=texto,
            font=("TT NORMS PRO", 16, "bold"),
            text_color="white"
        ).pack(pady=(5, 10))

        self.progress = ctk.CTkProgressBar(frame, mode="indeterminate", width=280)
        self.progress.pack(pady=10)
        self.progress.start()

    def cerrar_cargando(self):
        if hasattr(self, "progress"):
            self.progress.stop()
        if hasattr(self, "win_loading") and self.win_loading.winfo_exists():
            self.win_loading.destroy()

    

    # =========================================================
    # GUARDAR + CARGAR AUTOMÁTICAMENTE EL OTRO
    # =========================================================
    def guardar_registro(self):
        # Validaciones rápidas (UI)
        if (not self.fecha_entry.get() or
            not self.hora_inicio.get() or
            not self.sector_combo.get() or
            not self.orden_entry.get()):
            messagebox.showerror("Error", "Complete todos los campos obligatorios")
            return

        if not self.pdf:
            messagebox.showerror("Error", "Debe subir un PDF antes de guardar el registro.")
            return

        # Mostrar ventana de carga
        self.mostrar_cargando("Guardando información...")

        # Ejecutar proceso pesado en segundo plano
        import threading
        
        threading.Thread(
            target=self._guardar_registro_thread,
            daemon=True
        ).start()
        
    def _guardar_registro_thread(self):
        try:
            nombre_sector = self.sector_combo.get()
            codigo_sector = self.sectores.get(nombre_sector)

            fecha_str = self.fecha_entry.get()
            fecha_dt = datetime.strptime(fecha_str, "%Y-%m-%d")

            meses_es = {
                "january": "ENERO","february": "FEBRERO","march": "MARZO",
                "april": "ABRIL","may": "MAYO","june": "JUNIO",
                "july": "JULIO","august": "AGOSTO","september": "SEPTIEMBRE",
                "october": "OCTUBRE","november": "NOVIEMBRE","december": "DICIEMBRE"
            }
            carpeta_mes = meses_es[fecha_dt.strftime("%B").lower()]
            carpeta_año = str(fecha_dt.year)
            datos = {
                "FECHA": fecha_str,
                "ID_SECTOR": codigo_sector,
                "ORDEN_COMPRA": self.orden_entry.get(),
                "HORAS": self.hora_inicio.get(),
                "TIPO_EQUIPO": self.equipo.get(),
                "PROVEEDOR": self.proveedor_entry.get(),
                "CODIGO_PROVEEDOR": self.codigo_proveedor_entry.get(),
                "ACTIVO": 1
            }

            insertar_orden_en_ficha(datos)

            if not insertar_ORDEN_grua(datos):
                raise Exception("Error al insertar en BD")

            # Subir PDF solo una vez
            if not self.pdf_subido:
                self.subir_soporte(
                    "HORAS_GRUA",
                    nombre_sector,
                    carpeta_año,
                    carpeta_mes,
                    self.orden_entry.get()
                )
                self.pdf_subido = True

            # Marcar item guardado
            if self.index_actual is not None:
                self.items_guardados.add(self.index_actual)

            # Volver al hilo principal
            self.after(0, self._guardar_exito)

        except Exception as e:
            self.after(0, lambda: self._guardar_error(str(e)))

    def _guardar_exito(self):
        self.cerrar_cargando()
        messagebox.showinfo("Éxito", "Registro guardado correctamente.")
        self.cargar_siguiente_item_si_hay()

    def _guardar_error(self, error):
        self.cerrar_cargando()
        messagebox.showerror("Error", f"Ocurrió un error:\n{error}")


    def subir_soporte(self, carpeta_inicial, sector,carpeta_año,carpeta_mes, carpeta_nombre):
        from .subir_soporte import verificar_carpeta_sharepoint, seleccionar_archivos
        archivos = [self.pdf]
        if archivos:
            verificar_carpeta_sharepoint(archivos, carpeta_inicial, sector, carpeta_año, carpeta_mes, carpeta_nombre)
            return True
        return False

    def abrir_calendario(self):
        top = Toplevel(self)
        top.title("Seleccionar fecha")
        top.grab_set()

        ancho_ventana = 300
        alto_ventana = 300

        x = (self.winfo_screenwidth() // 2) - (ancho_ventana // 2)
        y = (self.winfo_screenheight() // 2) - (alto_ventana // 2)
        top.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")

        cal = Calendar(top, date_pattern="yyyy-mm-dd")
        cal.pack(padx=10, pady=10, expand=True, fill="both")

        def seleccionar_fecha():
            self.fecha_entry.delete(0, "end")
            self.fecha_entry.insert(0, cal.get_date())
            top.destroy()

        ctk.CTkButton(
            top, text="Seleccionar",
            command=seleccionar_fecha,
            fg_color="#5E95FF", hover_color="#4780E0"
        ).pack(pady=10)

    def borrar_todo(self):
        self.fecha_entry.delete(0,"end")
        self.hora_inicio.delete(0,"end")
        self.orden_entry.delete(0,"end")
        self.proveedor_entry.delete(0,"end")
        self.codigo_proveedor_entry.delete(0,"end")
        self.sector_combo.set("")
        self.equipo.set("")
