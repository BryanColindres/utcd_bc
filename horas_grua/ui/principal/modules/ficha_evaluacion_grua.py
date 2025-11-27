import customtkinter as ctk
from tkinter import Toplevel, messagebox
from docx import Document
from docx.shared import Pt
from docx import Document
from docx.shared import  RGBColor
from docx.oxml.ns import qn
from datetime import datetime
class EvaluacionProveedorModal(Toplevel):
    def __init__(self, parent, callback=None):
        super().__init__(parent)
        self.title("Evaluación del Proveedor de Grúa")
        self.geometry("750x650")
        self.configure(bg="#FFFFFF")
        self.grab_set()  # Bloquea la ventana principal

        self.callback = callback  # Función para devolver datos

        # ====== TÍTULO ======
        ctk.CTkLabel(
            self, text="FICHA DE EVALUACIÓN DE SERVICIO DE GRÚA",
            font=("TT NORMS PRO", 22, "bold"), text_color="#0B7890"
        ).pack(pady=20)

        form = ctk.CTkFrame(self, fg_color="white")
        form.pack(fill="both", expand=True, padx=20, pady=10)

        # ===========================================================
        # 1. Servicio tercerizado (SI / NO)
        # ===========================================================
        ctk.CTkLabel(form, text="1. ¿Cuenta su sector con servicio de grúa tercerizado?",
                     font=("TT NORMS PRO", 16)).grid(row=0, column=0, sticky="w", pady=10)

        self.servicio_tercerizado = ctk.StringVar(value="NO")
        ctk.CTkRadioButton(form, text="SI", variable=self.servicio_tercerizado, value="SI").grid(row=0, column=1)
        ctk.CTkRadioButton(form, text="NO", variable=self.servicio_tercerizado, value="NO").grid(row=0, column=2)

        # ===========================================================
        # 2. Nombre del proveedor
        # ===========================================================
        ctk.CTkLabel(form, text="2.De ser afirmativo detallar el nombre del proveedor:",
                     font=("TT NORMS PRO", 16)).grid(row=1, column=0, sticky="w", pady=10)
        self.nombre_proveedor = ctk.CTkEntry(form, width=300)
        self.nombre_proveedor.grid(row=1, column=1, columnspan=2, pady=10)

        # ===========================================================
        # 3. Orden de compra y horas aprobadas
        # ===========================================================
        ctk.CTkLabel(form, text="3. Orden de compra actual y horas aprobadas:",
                     font=("TT NORMS PRO", 16)).grid(row=2, column=0, sticky="w", pady=10)
        self.orden_info = ctk.CTkEntry(form, width=300)
        self.orden_info.grid(row=2, column=1, columnspan=2, pady=10)

        # ===========================================================
        # 4. Disponibilidad inmediata SI/NO
        # ===========================================================
        ctk.CTkLabel(form, text="4. ¿El proveedor Brinda disponibilidad inmediata?",
                     font=("TT NORMS PRO", 16)).grid(row=3, column=0, sticky="w", pady=10)
        self.disponible = ctk.StringVar(value="NO")
        ctk.CTkRadioButton(form, text="SI", variable=self.disponible, value="SI").grid(row=3, column=1)
        ctk.CTkRadioButton(form, text="NO", variable=self.disponible, value="NO").grid(row=3, column=2)

        # ===========================================================
        # 5. Grúa sin fallas SI/NO
        # ===========================================================
        ctk.CTkLabel(form, text="5. ¿Proveedor no ha prestado el servicio por grúa en mal estado ?",
                     font=("TT NORMS PRO", 16)).grid(row=4, column=0, sticky="w", pady=10)
        self.sin_fallas = ctk.StringVar(value="NO")
        ctk.CTkRadioButton(form, text="SI", variable=self.sin_fallas, value="SI").grid(row=4, column=1)
        ctk.CTkRadioButton(form, text="NO", variable=self.sin_fallas, value="NO").grid(row=4, column=2)

        # ===========================================================
        # 6. Veces que NO brindó el servicio
        # ===========================================================
        ctk.CTkLabel(form, text="6. Desde la aprobación de las horas de servicio ¿Cuántas veces NO brindó el servicio?",
                     font=("TT NORMS PRO", 16)).grid(row=5, column=0, sticky="w", pady=10)
        self.veces_no = ctk.CTkEntry(form, width=120)
        self.veces_no.grid(row=5, column=1, pady=10)

        # ===========================================================
        # 7. Cumple especificaciones técnicas
        # ===========================================================
        ctk.CTkLabel(form, text="7. ¿El equipo prestado por el proveedor Cumple especificaciones técnicas para sus labores?",
                     font=("TT NORMS PRO", 16)).grid(row=6, column=0, sticky="w", pady=10)
        self.especificaciones = ctk.StringVar(value="NO")
        ctk.CTkRadioButton(form, text="SI", variable=self.especificaciones, value="SI").grid(row=6, column=1)
        ctk.CTkRadioButton(form, text="NO", variable=self.especificaciones, value="NO").grid(row=6, column=2)

        # ===========================================================
        # 8. Calificación Muy Bueno / Regular / Mal Servicio
        # ===========================================================
        ctk.CTkLabel(form, text="8. Califique el servicio:",
                     font=("TT NORMS PRO", 16)).grid(row=7, column=0, sticky="w", pady=10)

        self.calificacion = ctk.StringVar(value="Regular")
        ctk.CTkRadioButton(form, text="Muy Bueno", variable=self.calificacion, value="Muy Bueno").grid(row=7, column=1)
        ctk.CTkRadioButton(form, text="Regular", variable=self.calificacion, value="Regular").grid(row=7, column=2)
        ctk.CTkRadioButton(form, text="Mal Servicio", variable=self.calificacion, value="Mal Servicio").grid(row=7, column=3)

        # ===========================================================
        # 9. Observaciones
        # ===========================================================
        ctk.CTkLabel(form, text="9. Observaciones:",
                     font=("TT NORMS PRO", 16)).grid(row=8, column=0, sticky="nw", pady=10)
        self.observaciones = ctk.CTkTextbox(form, width=400, height=120)
        self.observaciones.grid(row=8, column=1, columnspan=3, pady=10)

        # ===========================================================
        # BOTÓN GUARDAR
        # ===========================================================
        ctk.CTkButton(
            self, text="Guardar Evaluación", fg_color="#0C92A9", hover_color="#0B7890",
            command=self.guardar
        ).pack(pady=20)




    def generar_word(self, datos):
        doc = Document()

        # Cambiar estilo predeterminado
        style = doc.styles['Normal']
        style.font.name = 'Calibri'        # Aptos no está en python-docx, Calibri es equivalente corporativo
        style._element.rPr.rFonts.set(qn('w:eastAsia'), 'Calibri')
        style.font.size = Pt(11)

        # ==== TÍTULO ====
        titulo = doc.add_heading("FICHA DE EVALUACIÓN DE PROVEEDOR DE SERVICIO DE GRÚA", level=1)
        titulo.alignment = 1

        doc.add_paragraph("\nSe requiere marcar con un '☑' la opción a escoger\n")

        # Utilidad para crear opciones SI/NO con cuadro
        def opcion(valor, esperado):
            return "☑" if valor == esperado else "☐"

        # Utilidad para texto subrayado y azul
        def texto_subrayado(parrafo, texto):
            run = parrafo.add_run(texto)
            run.font.underline = True
            run.font.color.rgb = RGBColor(0, 0, 180)
            run.font.size = Pt(11)

        # ================= PREGUNTA 1 =================
        p = doc.add_paragraph()
        p.add_run("1. ¿Cuenta su sector con servicio de grúa tercerizado?   ")
        p.add_run(f"SI {opcion(datos['servicio_tercerizado'], 'SI')}   NO {opcion(datos['servicio_tercerizado'], 'NO')}")

        # ================= PREGUNTA 2 =================
        p = doc.add_paragraph("2. Nombre del proveedor:  ")
        texto_subrayado(p, datos['nombre_proveedor'] or " ")

        # ================= PREGUNTA 3 =================
        p = doc.add_paragraph("3. Orden de compra actual y horas aprobadas:  ")
        texto_subrayado(p, datos['orden_info'] or " ")

        # ================= PREGUNTA 4 =================
        p = doc.add_paragraph()
        p.add_run("4. ¿El proveedor brinda disponibilidad inmediata?   ")
        p.add_run(f"SI {opcion(datos['disponible'], 'SI')}   NO {opcion(datos['disponible'], 'NO')}")

        # ================= PREGUNTA 5 =================
        p = doc.add_paragraph()
        p.add_run("5. ¿Proveedor no ha prestado el servicio por grúa en mal estado?   ")
        p.add_run(f"SI {opcion(datos['sin_fallas'], 'SI')}   NO {opcion(datos['sin_fallas'], 'NO')}")

        # ================= PREGUNTA 6 =================
        p = doc.add_paragraph("6. Veces que NO brindó el servicio:  ")
        texto_subrayado(p, datos['veces_no'] or " ")

        # ================= PREGUNTA 7 =================
        p = doc.add_paragraph()
        p.add_run("7. ¿El equipo cumple especificaciones técnicas?   ")
        p.add_run(f"SI {opcion(datos['especificaciones'], 'SI')}   NO {opcion(datos['especificaciones'], 'NO')}")

        # ================= PREGUNTA 8 =================
        p = doc.add_paragraph()
        p.add_run("8. Calificación del servicio:   ")
        p.add_run(f"MUY BUENO {opcion(datos['calificacion'], 'Muy Bueno')}   ")
        p.add_run(f"REGULAR {opcion(datos['calificacion'], 'Regular')}   ")
        p.add_run(f"MAL SERVICIO {opcion(datos['calificacion'], 'Mal Servicio')}")

        # ================= OBSERVACIONES =================
        doc.add_paragraph("\n9. Observaciones:")
        p = doc.add_paragraph()
        texto_subrayado(p, datos["observaciones"] or " ")

        # ================= FIRMAS =================
        doc.add_paragraph("\n\nNombre: ________________________________")
        doc.add_paragraph("Firma: _________________________________")
        p = doc.add_paragraph("Fecha:  ")
        texto_subrayado(p, datetime.now().strftime("%d/%m/%Y"))

        nombre_archivo = "Evaluación_Proveedor_Grúa_Formato_Elegante.docx"
        doc.save(nombre_archivo)
        return nombre_archivo



    def guardar(self):
        datos = {
            "servicio_tercerizado": self.servicio_tercerizado.get(),
            "nombre_proveedor": self.nombre_proveedor.get(),
            "orden_info": self.orden_info.get(),
            "disponible": self.disponible.get(),
            "sin_fallas": self.sin_fallas.get(),
            "veces_no": self.veces_no.get(),
            "especificaciones": self.especificaciones.get(),
            "calificacion": self.calificacion.get(),
            "observaciones": self.observaciones.get("0.0", "end").strip()
        }

        archivo = self.generar_word(datos)

        messagebox.showinfo("Documento creado", f"El archivo '{archivo}' ha sido generado correctamente.")

        if self.callback:
            self.callback(datos)

        self.destroy()

if __name__ == "__main__":
    import customtkinter as ctk

    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.geometry("400x200")

    def recibir_datos(data):
        print("Datos recibidos:", data)

    def abrir_modal():
        EvaluacionProveedorModal(app, callback=recibir_datos)

    btn = ctk.CTkButton(app, text="Abrir Evaluación de Proveedor", command=abrir_modal)
    btn.pack(pady=50)
    #abrir_modal()
    app.mainloop()