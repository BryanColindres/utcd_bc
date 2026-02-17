import customtkinter as ctk
from tkinter import messagebox
from tkinter import Toplevel
from tkcalendar import Calendar
from datetime import datetime
import sys
import os
from .enviar_correo import envia_correo
from .ficha_evaluacion_grua import EvaluacionProveedorModal

# Ajustar path para importar db_controller
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from db_controller import insertar_hora_grua,validar_horas_disponibles,obtener_orden_compra,correo_enviado,obtener_sectores,obtener_id_sector,validacion_,obtener_rol,obtener_orden_compra_completo,validacion_admin,info_orden,insertar_correo,completado_orden,obtener_responsable_sector,obtener_supervisor_sector

class RegistrarHoras(ctk.CTkFrame):
    
    def __init__(self, parent):
        
        self.rol = obtener_rol()
        self.id_sector= obtener_id_sector() # valor fijo por ahora
        # en __init__ o al inicio de la clase
        self.mensaje_abierto = False
        super().__init__(parent, fg_color="white")

        # Título principal
        ctk.CTkLabel(self, text="Registrar Horas de Grúa 🏗️", font=("TT NORMS PRO", 24, "bold"), text_color="#01091F").pack(pady=(30,20))

        # --- Contenedor para centrar el formulario ---
        form_frame = ctk.CTkFrame(self, fg_color="white")
        form_frame.pack(expand=True)  # Esto centra verticalmente
        form_frame.grid_columnconfigure(0, weight=1)  # Opcional, para centrar columnas si usas grid dentro

        # SERVICIO y UNIDAD DE MEDIDA (fijos)
        ctk.CTkLabel(form_frame, text="SERVICIO UTILIZADO:", font=("TT NORMS PRO",14,"bold"),text_color="#87898F").grid(row=1, column=0, sticky="e", padx=10, pady=8)
        ctk.CTkLabel(form_frame, text="1. Horas de grúa", font=("TT NORMS PRO",14), fg_color="#EFEFEF", text_color="#87898F", corner_radius=8, width=250, height=30).grid(row=1, column=1, columnspan=2, sticky="w", padx=10, pady=8)

        ctk.CTkLabel(form_frame, text="UNIDAD DE MEDIDA:", font=("TT NORMS PRO",14,"bold"),text_color="#87898F").grid(row=2, column=0, sticky="e", padx=10, pady=8)
        ctk.CTkLabel(form_frame, text="Horas", font=("TT NORMS PRO",14), fg_color="#EFEFEF", text_color="#87898F", corner_radius=8, width=250, height=30).grid(row=2, column=1, columnspan=2, sticky="w", padx=10, pady=8)

        # FECHA con botón para calendario
        ctk.CTkLabel(form_frame, text="FECHA DE UTILIZACION:", font=("TT NORMS PRO",14,"bold"),text_color="#87898F").grid(row=3, column=0, sticky="e", padx=10, pady=8)
        self.fecha_entry = ctk.CTkEntry(form_frame, placeholder_text="YYYY-MM-DD", width=250, fg_color="#EFEFEF", text_color="black")
        self.fecha_entry.grid(row=3, column=1, sticky="w", padx=10, pady=8)
        ctk.CTkButton(form_frame, text="📅", width=30, fg_color="#5E95FF", hover_color="#4780E0", command=self.abrir_calendario).grid(row=3, column=2, sticky="w", padx=5)
        #self.fecha_entry.bind("<FocusOut>", lambda e: self.validar_fecha(self.fecha_entry))
        
        # HORA DE INICIO y HORA FINAL
        ctk.CTkLabel(form_frame, text="HORA DE INICIO (HH:MM):", font=("TT NORMS PRO",14,"bold"),text_color="#87898F").grid(row=4, column=0, sticky="e", padx=10, pady=8)
        self.hora_inicio = ctk.CTkEntry(form_frame, placeholder_text="HH:MM", width=250, fg_color="#EFEFEF", text_color="#87898F")
        self.hora_inicio.grid(row=4, column=1, columnspan=2, sticky="w", padx=10, pady=8)
        self.hora_inicio.bind("<FocusOut>", lambda e: self.validar_hora(self.hora_inicio))

        ctk.CTkLabel(form_frame, text="HORA FINAL (HH:MM):", font=("TT NORMS PRO",14,"bold"),text_color="#87898F").grid(row=5, column=0, sticky="e", padx=10, pady=8)
        self.hora_final = ctk.CTkEntry(form_frame, placeholder_text="HH:MM", width=250, fg_color="#EFEFEF", text_color="#87898F")
        self.hora_final.grid(row=5, column=1, columnspan=2, sticky="w", padx=10, pady=8)
        self.hora_final.bind("<FocusOut>", lambda e: self.validar_hora(self.hora_final))

        self.hora_inicio.bind("<KeyRelease>", lambda e: self.calcular_cantidad())
        self.hora_final.bind("<KeyRelease>", lambda e: self.calcular_cantidad())
        # CANTIDAD USADA
        ctk.CTkLabel(form_frame, text="CANTIDAD UTILIZADA:", font=("TT NORMS PRO",14,"bold"),text_color="#87898F").grid(row=6, column=0, sticky="e", padx=10, pady=8)
        self.cantidad_entry = ctk.CTkEntry(form_frame, width=250, fg_color="#EFEFEF", text_color="#87898F", state="disabled")
        self.cantidad_entry.grid(row=6, column=1, columnspan=2, sticky="w", padx=10, pady=8)

        # JUSTIFICACION
        ctk.CTkLabel(form_frame, text="JUSTIFICACION:", font=("TT NORMS PRO",14,"bold"),text_color="#87898F").grid(row=7, column=0, sticky="ne", padx=10, pady=8)
        self.just_entry = ctk.CTkTextbox(form_frame, width=400, height=100, fg_color="#EFEFEF", text_color="#87898F")
        self.just_entry.grid(row=7, column=1, columnspan=2, sticky="w", padx=10, pady=8)

        # RESPONSABLE
        ctk.CTkLabel(form_frame, text="RESPONSABLE:", font=("TT NORMS PRO",14,"bold"),text_color="#87898F").grid(row=8, column=0, sticky="e", padx=10, pady=8)
        self.resp_entry = ctk.CTkComboBox(form_frame, values=self.obtener_responsables(), width=250, fg_color="#EFEFEF", text_color="#87898F",state="readonly")
        self.resp_entry.grid(row=8, column=1, columnspan=2, sticky="w", padx=10, pady=8)

        # ORDEN COMPRA
        ctk.CTkLabel(form_frame, text="ORDEN DE COMPRA:", font=("TT NORMS PRO",14,"bold"),text_color="#87898F").grid(row=9, column=0, sticky="e", padx=10, pady=8)
        self.orden_entry = ctk.CTkComboBox(form_frame, values=self.ordenes_compras_(), width=280, fg_color="#EFEFEF",text_color="#87898F",state="readonly")
        self.orden_entry.grid(row=9, column=1, columnspan=2, sticky="w", padx=10, pady=8)

        # BOTONES
        self.btn_guardar = ctk.CTkButton(form_frame, text="💾 Guardar", font=("TT NORMS PRO",16,"bold"), fg_color="#5FD0DF",text_color='white' ,hover_color="#56C0CE", command=self.guardar_registro, width=150,height=40)
        self.btn_guardar.grid(row=10, column=1, pady=30)
        self.btn_borrar = ctk.CTkButton(form_frame, text="Borrar Todo", font=("TT NORMS PRO",16,"bold"), fg_color="#F1F1F4",text_color='#616161', hover_color="#EFF0F8", command=self.borrar_todo, width=150,height=40)
        self.btn_borrar.grid(row=10, column=0, pady=30)

    def obtener_responsables(self):
        supervisores = obtener_responsable_sector(self.id_sector)
        return supervisores
    
    def ordenes_compras_(self):
        print("Sector ID en registrar horas:", self.id_sector)

        # Obtener data
        self.data = obtener_orden_compra(self.id_sector)

        # Validar si es None o está vacío
        if self.data is None or len(self.data) == 0:
            print("No existen órdenes de compra para este sector.")
            return ["SIN ÓRDENES DISPONIBLES"]

        # Validar si las columnas existen
        required_cols = {"orden_compra", "tipo_equipo"}
        if not required_cols.issubset(set(self.data.columns)):
            print("ERROR: La consulta no devolvió las columnas necesarias:", self.data.columns)
            return ["ERROR: Datos incompletos"]

        # Convertir datos a listas
        self.ordenes = self.data["orden_compra"].astype(str).tolist()
        self.tipo_equipo = self.data["tipo_equipo"].astype(str).tolist()

        print("Órdenes a mostrar:", self.ordenes)

        x = []
        for i in range(len(self.data)):
            orden = self.ordenes[i]
            equipo = self.tipo_equipo[i]
            try:
                val = validacion_admin(orden, equipo)
            except Exception as e:
                print(f"Error validando orden {orden}: {e}")
                val = "N/D"

            c = f"{orden} - Equipo: {equipo} - Disponible: {val}"
            x.append(c)

        return x

    # ---------------- FUNCIONES ----------------

    def abrir_modal_evaluacion(self, orden, proveedor, horas,equipo):
        def recibir(data):
            print("Datos recibidos de evaluación:", data)
        EvaluacionProveedorModal(self, orden, proveedor, horas,equipo, callback=recibir)

    def abrir_calendario(self):
        # Crear ventana emergente
        top = Toplevel(self)
        top.title("Seleccionar fecha")

        # Forzar que se muestre arriba y sin posibilidad de interacción con la ventana principal
        top.grab_set()

        # --- Medidas de la ventana calendario ---
        ancho_ventana = 300
        alto_ventana = 300

        # Obtener dimensiones de la pantalla
        ancho_pantalla = self.winfo_screenwidth()
        alto_pantalla = self.winfo_screenheight()

        # Calcular posición para centrar
        x = (ancho_pantalla // 2) - (ancho_ventana // 2)
        y = (alto_pantalla // 2) - (alto_ventana // 2)

        # Posicionar ventana al centro
        top.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")

        # Crear calendario
        cal = Calendar(top 
                       ,date_pattern="yyyy-mm-dd"
                       ,maxdate=datetime.today()
                       )
        cal.pack(padx=10, pady=10, expand=True, fill="both")

        # Botón seleccionar
        def seleccionar_fecha():
            self.fecha_entry.delete(0, "end")
            self.fecha_entry.insert(0, cal.get_date())
            top.destroy()

        ctk.CTkButton(
            top,
            text="Seleccionar",
            command=seleccionar_fecha,
            fg_color="#5E95FF",
            hover_color="#4780E0"
        ).pack(pady=10)


    # def validar_fecha(self, entry):
    #     fecha_texto = entry.get().strip()
    #     if not fecha_texto:
    #         # Permitir campo vacío sin error
    #         entry.configure(fg_color="#EFEFEF")
    #         return
        
    #     try:
    #         fecha = datetime.strptime(fecha_texto, "%Y-%m-%d")
    #         # opcional: validar que no sea fecha futura
    #         hoy = datetime.today().date()
    #         if fecha > hoy:
    #             entry.configure(fg_color="#FDEDEC")
    #             if not getattr(self, "mensaje_abierto", False):
    #                 self.mensaje_abierto = True
    #                 messagebox.showerror("Error", "La fecha no puede ser futura")
    #                 self.mensaje_abierto = False
    #             return
            
    #         # Fecha válida
    #         entry.configure(fg_color="#EFEFEF")

    #     except ValueError:
    #         entry.configure(fg_color="#FDEDEC")
    #         if not getattr(self, "mensaje_abierto", False):
    #             self.mensaje_abierto = True
    #             messagebox.showerror("Error", "Ingrese la fecha en formato YYYY-MM-DD")
    #             self.mensaje_abierto = False


    def validar_hora(self, entry):
        hora_str = entry.get().strip()
        if not hora_str:
            return  # permitir vacío
        try:
            # validar formato 24h
            h, m = map(int, hora_str.split(":"))
            if h < 0 or h > 23 or m < 0 or m > 59:
                raise ValueError
            entry.configure(fg_color="#EFEFEF")
        except (ValueError, IndexError):
            entry.configure(fg_color="#FDEDEC")
            if not self.mensaje_abierto:
                self.mensaje_abierto = True
                messagebox.showerror("Error", "Formato de hora incorrecto (HH:MM 24h)")
                self.mensaje_abierto = False


    def calcular_cantidad(self):
        if self.hora_inicio.get() and self.hora_final.get():
            try:
                inicio = datetime.strptime(self.hora_inicio.get(), "%H:%M")
                final = datetime.strptime(self.hora_final.get(), "%H:%M")
                delta = (final - inicio).total_seconds() / 3600  # decimal
                self.cantidad_entry.configure(state="normal")
                
                if delta <= 0:
                    self.cantidad_entry.delete(0, "end")
                    self.cantidad_entry.insert(0, "ERROR")
                else:
                    # Convertir decimal a HH:MM para mostrar
                    horas = int(delta)
                    minutos = round((delta - horas) * 60)
                    hhmm = f"{horas:02d}:{minutos:02d}"
                    
                    self.cantidad_entry.delete(0, "end")
                    self.cantidad_entry.insert(0, hhmm)
                
                self.cantidad_entry.configure(state="disabled")
                # Guardar delta decimal en un atributo interno
            except:
                pass

    def validar_fecha(self, entry):
        fecha_texto = entry.get().strip()
        if not fecha_texto:
            # Permitir campo vacío sin error
            entry.configure(fg_color="#EFEFEF")
            return 
        try:
            fecha = datetime.strptime(fecha_texto, "%Y-%m-%d")
            # opcional: validar que no sea fecha futura
            hoy = datetime.today().date()
            print("Fecha ingresada:", fecha.date(), "Fecha actual:", hoy)
            if fecha.date() > hoy:
                entry.configure(fg_color="#FDEDEC")
                if not getattr(self, "mensaje_abierto", False):
                    self.mensaje_abierto = True
                    messagebox.showerror("Error", "La fecha no puede ser futura")
                    self.mensaje_abierto = False
                    return "error"
            
            # Fecha válida
            entry.configure(fg_color="#EFEFEF")
            return "ok"
            
            # Fecha válida
        except:
                entry.configure(fg_color="#FDEDEC")
                if not getattr(self, "mensaje_abierto", False):
                    self.mensaje_abierto = True
                    messagebox.showerror("Error", "Ingrese la fecha en formato YYYY-MM-DD")
                    self.mensaje_abierto = False
                    return "error"

    def guardar_registro(self):
        # Verificar campos obligatorios vacíos
        if not self.fecha_entry.get() or not self.hora_inicio.get() or not self.hora_final.get() \
            or not self.resp_entry.get() or not self.just_entry.get("1.0","end-1c"):
            messagebox.showerror("Error","Complete todos los campos obligatorios")
            return 
        mensaje_error = self.validar_fecha(self.fecha_entry)
        if mensaje_error == "error":
            return
        # Verificar errores de validación visual (color de fondo)
        campos_error = []
        if self.fecha_entry.cget("fg_color") == "#FDEDEC":
            campos_error.append("Fecha")
        if self.hora_inicio.cget("fg_color") == "#FDEDEC":
            campos_error.append("Hora de inicio")
        if self.hora_final.cget("fg_color") == "#FDEDEC":
            campos_error.append("Hora final")
        if self.cantidad_entry.get() == "ERROR":
            campos_error.append("Cantidad de horas")

        if campos_error:
            messagebox.showerror("Error", f"Corrija los siguientes campos: {', '.join(campos_error)}")
            return

        # Si todo está bien, continuar con validación de horas disponibles
        orden_completa = self.orden_entry.get()
        orden_solo = orden_completa.split(" - ")[0]  # toma solo '1531535'
        equipo = orden_completa.split(" - ")[1].replace("Equipo: ","")  # toma solo 'Camión Grúa'
        datos = {
            "FECHA_UTILIZACION": self.fecha_entry.get(),
            "SERVICIO_UTILIZADO": "1. Horas de grúa",
            "UNIDAD_DE_MEDIDA": "Horas",
            "HORA_DE_INICIO": self.hora_inicio.get(),
            "HORA_FINAL": self.hora_final.get(),
            "CANTIDAD_UTILIZADA": self.cantidad_entry.get(),
            "JUSTIFICACION": self.just_entry.get("1.0","end-1c"),
            "RESPONSABLE": self.resp_entry.get(),
            "ORDEN_COMPRA": orden_solo,
            "ID_SECTOR": self.id_sector,
            "TIPO_EQUIPO": equipo
        }
        
        informacion = info_orden(orden_solo)
        nombre_proveedor = informacion.nombre_proveedor
        horas_compra = informacion.horas_compra
        supervisor = obtener_supervisor_sector(self.id_sector)
        try:
            validacion = validar_horas_disponibles(id_sector=self.id_sector, orden_compra=orden_solo, datos=datos)
            if not validacion:
                return
            if validacion is False:
                return
            if validacion[0] == 'completar':
                bandera_insercion = validacion[1]
                self.completar_evaluacion(orden_solo, nombre_proveedor, supervisor, horas_compra,equipo, datos,bandera_insercion)
                return
            if validacion[0] == 'validar_correo':
                try:
                    resultado = validacion[1]
                    if correo_enviado(self.id_sector, orden_solo,equipo):
                        messagebox.showinfo("Aviso", "Quedan menos del 70% de horas disponibles, el correo de notificación ya se ha enviado para esta orden.")
                        if resultado.Proporcion_Usado == 1:
                            messagebox.showwarning("Advertencia","Ha alcanzado el 100% de las horas disponibles en este sector y orden de compra. No se pueden registrar más horas.")
                        return 
                    else:
                        messagebox.showwarning("Advertencia", "⚠️ Ha alcanzado el 70% de las horas disponibles en este sector y orden de compra. Debes completar la evaluación para mandar correo de alerta.")
                        #insertado = insertar_correo(id_sector, orden_compra,equipo)
                        #print('el insertado es',insertado)
                        print('antes de verificar completo')
                        completo = completado_orden(orden_solo,equipo)
                        if completo == 'NO':
                            print('abrir modal')
                            self.completar_evaluacion(orden_solo, nombre_proveedor, horas_compra,equipo, datos,bandera='no_insertar')
                            return
                except Exception as e:
                    print(f"[guardar_registro] Error verificando correo_enviado: {e}")
            elif validacion:
                # Antes de llamar a envia_correo sin adjunto, confirmar que el correo
                # no haya sido ya enviado o marcado como pendiente por validar_horas_disponibles.
                try:
                    ya_enviado = correo_enviado(self.id_sector, orden_solo, equipo)
                except Exception as e_ce:
                    print(f"[guardar_registro] Error verificando correo_enviado: {e_ce}")
                    # Por seguridad asumimos que NO se ha enviado para intentar el envío
                    ya_enviado = False

                if ya_enviado:
                    # Si ya se envió previamente, informar y no volver a enviar
                    return
                    #messagebox.showinfo("Información", "Notificación sobre horas ya fue enviada previamente para esta orden.")
                else:
                    try:
                        enviado_ok = envia_correo(sector=self.id_sector, orden_compra=orden_solo)
                        if enviado_ok:
                            messagebox.showinfo("Éxito", "Correo enviado correctamente.")
                        else:
                            messagebox.showwarning("Aviso", "No se pudo enviar el correo. Verifique la configuración.")
                    except Exception as e_send:
                        print(f"[guardar_registro] Error enviando correo: {e_send}")
                        messagebox.showerror("Error", "No se pudo enviar el correo, por favor contacte al administrador.")

            self.ordenes_compras_()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el registro:\n{str(e)}")



    def completar_evaluacion(self,orden_solo, nombre_proveedor, supervisor, horas_compra,equipo, datos,bandera):
        # Abrir modal y esperar hasta que el usuario lo cierre.
        # Guardamos el resultado en self.modal_result vía callback.
        self.modal_result = None

        def recibir(result):
            """
            result: dict esperado:
                {'datos': {...}, 'archivo': '/ruta/al/archivo.docx' or None, 'actualizado': True/False}
            """
            print("Callback modal recibió:", result)
            self.modal_result = result

        modal = EvaluacionProveedorModal(self, orden_solo, nombre_proveedor, supervisor, horas_compra, equipo, callback=recibir)
        self.wait_window(modal)  # Espera hasta que el modal se cierre

        # Después del cierre del modal: revisamos self.modal_result
        mr = getattr(self, "modal_result", None)

        # Si no devolvió nada o archivo es None → el usuario no completó la evaluación
        if not mr or not mr.get("archivo") or not mr.get("actualizado"):
            # No permitir registrar más horas hasta que complete la evaluación
            messagebox.showwarning("Atención", "La evaluación no fue completada o no se guardó correctamente. No se puede registrar más horas hasta completar la evaluación y no se enviará correo de alerta.")
            return

        # Si llegamos aquí: el modal devolvió archivo y la orden fue marcada como completada.
        archivo_eval = mr.get("archivo")

        # # Antes de enviar: comprobar si ya se envió correo (evita duplicados)
        # try:
        #     ya_enviado = correo_enviado(self.id_sector, orden_solo, equipo)
        # except Exception as e_ce:
        #     print(f"[guardar_registro] Error verificando correo_enviado: {e_ce}")
        #     ya_enviado = False

        # if ya_enviado:
        #     messagebox.showinfo("Información", "La evaluación fue completada y el correo ya se había enviado anteriormente.")
        #     # No reenvíes; si quieres forzar reenvío, ajusta aquí.
        # else:
            # Enviar correo adjuntando el docx generado por el modal
        try:
            enviado_ok = envia_correo(sector=self.id_sector, orden_compra=orden_solo, attachment_path=archivo_eval)
            if enviado_ok:
                insertar_correo(self.id_sector, orden_solo,equipo)
                messagebox.showinfo("Éxito", "Correo con evaluación enviado correctamente.")
            else:
                messagebox.showwarning("Aviso", "No se pudo enviar el correo con evaluación. Favor verificar configuración.")
        except Exception as e_send:
            messagebox.showerror("Error", f"No se pudo enviar el correo: {e_send}")

        # Finalmente, si deseas que tras completar y enviar se inserte la hora automáticamente,
        # puedes re-invocar el proceso de inserción aquí. En tu lógica previa, cuando la validación fue 'completar'
        # no insertabas automáticamente; si quieres insertar la hora ya (porque ya completó evaluación), haz:
        if bandera == 'insertar_datos':
            insertar_hora_grua(datos)
        # if insertar:
        #     print("Registro guardado correctamente después de completar evaluación.")
        
        #if insertar: messagebox.showinfo("Éxito", "Registro guardado correctamente después de completar evaluación.")
        # En mi propuesta dejo esa decisión explícita: no inserto automáticamente para respetar tu lógica original.
        # Si quieres que inserte, descomenta las 2 líneas previas.



    def borrar_todo(self):
        self.fecha_entry.delete(0,"end")
        self.hora_inicio.delete(0,"end")
        self.hora_final.delete(0,"end")
        self.cantidad_entry.configure(state="normal")
        self.cantidad_entry.delete(0,"end")
        self.cantidad_entry.configure(state="disabled")
        self.just_entry.delete("1.0","end")
        self.resp_entry.set("")
        self.orden_entry.set("")
        self.ordenes_compras_()
        


