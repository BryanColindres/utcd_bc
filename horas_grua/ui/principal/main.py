import customtkinter as ctk
from .modules.registrar_horas import RegistrarHoras
from .modules.ver_reportes import VerReportes
from .modules.estadisticas import Estadisticas
from .modules.configuracion import AcercaDe
from .modules.orden_compra import ordencompra
from .modules.ver_oden import Verorden
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))




# ---------------- Dashboard principal ----------------
class Dashboard(ctk.CTkToplevel):  # CTkFrame, no CTk
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.state('zoomed')  # Abrir maximizado
        # Configuración general de apariencia
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
#        super().__init__()
        
        # Manejar cierre de ventana
        self.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)
        # ---- Estilo global de Treeview ----
        import tkinter.ttk as ttk

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Custom.Treeview",
            background="#FFFFFF",
            foreground="#2C3E50",
            fieldbackground="#FFFFFF",
            rowheight=30,
            font=("Poppins", 11)
        )
        style.configure(
            "Custom.Treeview.Heading",
            background="#E74C3C",
            foreground="white",
            font=("Poppins", 12, "bold")
        )
        style.map("Custom.Treeview.Heading", background=[('active', '#C0392B')])

        self.title("UTCD - Control de Horas Grúa")
        self.geometry("1000x600")

        # Estado del sidebar (expandido/contraído)
        self.sidebar_expanded = True
        self.sidebar_width = 220

        # Configuración de la cuadrícula principal
        self.grid_columnconfigure(0, weight=0)  # sidebar
        self.grid_columnconfigure(1, weight=1)  # contenido
        self.grid_rowconfigure(0, weight=1)

        # ---------------- Panel izquierdo ----------------
        self.panel_izq = ctk.CTkFrame(self, fg_color="#5FD0DF", width=self.sidebar_width)
        self.panel_izq.grid(row=0, column=0, sticky="ns")

        # Panel derecho donde se mostrarán los módulos
        self.panel_der = ctk.CTkFrame(self, fg_color="white")
        self.panel_der.grid(row=0, column=1, sticky="nsew")

        # Ventana actual
        self.current_window = None

        from db_controller import obtener_rol
        self.rol = obtener_rol()
        
        # Botones del menú lateral
        # Botones del menú lateral
        # Frame para botones principales
        frame_botones = ctk.CTkFrame(self.panel_izq, fg_color="#5FD0DF", border_width=0)
        frame_botones.pack(fill="both", expand=True, anchor="n")

        # Frame para el botón "Acerca de" abajo
        frame_bottom = ctk.CTkFrame(self.panel_izq, fg_color="#5FD0DF", border_width=0)
        frame_bottom.pack(fill="x", side="bottom", pady=20)

        # Botones principales
        botones = [
            "🏗️ Registrar Horas",
            "📊 Ver Reportes",
            "📈 Estadísticas"
        ]
        if self.rol == 'admin':
            botones.extend(["📝 Registrar orden compra", "📋 Ver orden compra"])

        for nombre in botones:
            btn = ctk.CTkButton(
                frame_botones,
                text=nombre,
                font=("TT NORMS PRO", 18),
                fg_color="#5FD0DF",
                hover_color="#56C0CE",
                text_color="white",
                corner_radius=12,
                command=lambda n=nombre: self.mostrar_modulo(n)
            )
            btn.pack(fill="x", padx=80, pady=15, anchor="center")

        # Botón "Acerca de" siempre abajo
        btn_acerca = ctk.CTkButton(
            frame_bottom,
            text="⚙️ Acerca de",
            font=("TT NORMS PRO", 18),
            fg_color="#5FD0DF",
            hover_color="#56C0CE",
            text_color="white",
            corner_radius=12,
            command=lambda: self.mostrar_modulo("⚙️ Acerca de")
        )
        btn_acerca.pack(fill="x", padx=80, pady=0)

        # Mostrar el primer módulo al iniciar
        self.mostrar_modulo("🏗️ Registrar Horas")
        # En su lugar, mostrar una pantalla de bienvenida simple
        # welcome = ctk.CTkLabel(self.panel_der, text="j", font=("TT NORMS PRO", 1, "bold"))
        # welcome.pack(expand=True)
        # self.current_window = None

    # ---------------- Función para cambiar de módulo ----------------
    def mostrar_modulo(self, nombre):
        # Ocultar y destruir el módulo actual si existe
        if self.current_window:
            self.current_window.pack_forget()
            #self.current_window.destroy()

        # Crear una nueva instancia del módulo seleccionado
        if nombre == "🏗️ Registrar Horas":
            self.current_window = RegistrarHoras(self.panel_der)
        elif nombre == "📊 Ver Reportes":
            self.current_window = VerReportes(self.panel_der)
        elif nombre == "📈 Estadísticas":
            self.current_window = Estadisticas(self.panel_der)
        elif nombre == "⚙️ Acerca de":
            self.current_window = AcercaDe(self.panel_der)
        elif nombre == "📝 Registrar orden compra" and self.rol == 'admin':
            self.current_window = ordencompra(self.panel_der)
        elif nombre == "📋 Ver orden compra" and self.rol == 'admin':
            self.current_window = Verorden(self.panel_der)
        else:
            return  # seguridad por si se pasa un nombre no existente

        # Mostrar el módulo
        self.current_window.pack(fill="both", expand=True)

    def cerrar_aplicacion(self):
        # Aquí podés destruir todos los frames que tengas
        self.quit()
        self.destroy()  # Cierra la ventana principal

# ---------------- Ejecución principal ----------------
# if __name__ == "__main__":
#     app = Dashboard()
#     app.mainloop()
