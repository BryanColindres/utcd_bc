import customtkinter as ctk
from tkinter import messagebox, Label
from PIL import Image, ImageTk
import sys
import os

# ---------------- Rutas y imports ----------------

# Agregar la raíz del proyecto al path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Imports




# ---------------- Configuración global Login ----------------
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ---------------- Funciones ----------------

# ---------------- Clase Login ----------------
class Login(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.transient(master)            # hace que sea modal respecto al master
        self.grab_set()                   # asegurar modalidad (también lo puedes manejar afuera)
        self.exito = False  # <- indicador de login exitoso

        self.title("UTCD - Control de Horas Grúa | Inicio de Sesión")
        self.state('zoomed')  # Abrir maximizado

        # Grid principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ---------------- Panel izquierdo ----------------
        frame_izq = ctk.CTkFrame(self, fg_color="#5FD0DF")
        frame_izq.grid(row=0, column=0, sticky="nsew", padx=(40,20), pady=40)
        frame_izq.grid_rowconfigure(0, weight=1)
        frame_izq.grid_rowconfigure(1, weight=0)
        frame_izq.grid_columnconfigure(0, weight=1)

        inner_frame = ctk.CTkFrame(frame_izq, fg_color="#5FD0DF", border_width=0)
        inner_frame.grid(row=0, column=0, sticky="nsew")
        inner_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(inner_frame, text="UTCD",
                     font=("Poppins", 48, "bold"),
                     fg_color="#5FD0DF", text_color="white").pack(pady=(0,10))
        ctk.CTkLabel(inner_frame, text="Control de Horas de Grúa",
                     font=("Poppins", 22, "bold"),
                     fg_color="#5FD0DF", text_color="white").pack(pady=(50,10))
        ctk.CTkLabel(inner_frame, text="Sistema interno para el registro, control y\nseguimiento del uso de grúas UTCD.",
                     font=("Inter", 19), fg_color="#5FD0DF", text_color="white", justify="center").pack(pady=(100,0))

        ruta_imagen = os.path.join(os.path.dirname(os.path.dirname(__file__)), "imagenes", "grua.png")
        img = Image.open(ruta_imagen).resize((250,300))
        self.imagen_tk = ImageTk.PhotoImage(img)
        Label(inner_frame, image=self.imagen_tk, bg="#5FD0DF").pack(pady=(100,100))

        ctk.CTkLabel(frame_izq, text="© UTCD, 2025 - Gestión de Información",
                     font=("Inter",12), fg_color="#5FD0DF", text_color="#D6E3FF").grid(row=1, column=0, sticky="s", pady=(10,10))

        # ---------------- Panel derecho ----------------
        frame_der = ctk.CTkFrame(self, fg_color="white")
        frame_der.grid(row=0, column=1, sticky="nsew", padx=(20,40), pady=40)
        frame_der.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame_der, text="Iniciar Sesión",
                     font=("Poppins",26,"bold")).pack(anchor="w", pady=(40,10), padx=40)
        ctk.CTkLabel(frame_der, text="Ingrese las credenciales de base de datos",
                     font=("Inter",14), text_color="#777777").pack(anchor="w", padx=40, pady=(0,30))

        ctk.CTkLabel(frame_der, text="Usuario", font=("Inter",13,"bold"), text_color="#2E6CF6").pack(anchor="w", padx=40)
        self.usuario = ctk.CTkEntry(frame_der, placeholder_text="Ingrese su usuario", corner_radius=10, height=35)
        self.usuario.pack(fill="x", padx=40, pady=(5,20))

        ctk.CTkLabel(frame_der, text="Contraseña", font=("Inter",13,"bold"), text_color="#2E6CF6").pack(anchor="w", padx=40)
        frame_pass = ctk.CTkFrame(frame_der, fg_color="white", border_width=0)
        frame_pass.pack(fill="x", padx=40, pady=(5,30))
        frame_pass.grid_columnconfigure(0, weight=1)

        self.clave = ctk.CTkEntry(frame_pass, placeholder_text="Ingrese su contraseña", show="•", corner_radius=10, height=35)
        self.clave.grid(row=0, column=0, sticky="ew")
        self.btn_toggle = ctk.CTkButton(frame_pass, text="🔒", width=35, corner_radius=10,
                                        command=self.alternar_contraseña, fg_color="#E0E0E0", text_color="#555555")
        self.btn_toggle.grid(row=0, column=1, padx=(8,0))

        self.btn_login = ctk.CTkButton(frame_der, text="Entrar", corner_radius=15, height=40,
                                       fg_color="#5FD0DF", hover_color="#265BC8",
                                       font=("Poppins",14,"bold"), command=self.iniciar_sesion)
        self.btn_login.pack(fill="x", padx=40, pady=10)

        # Enter para submit
        self.usuario.bind("<Return>", lambda e: self.iniciar_sesion())
        self.clave.bind("<Return>", lambda e: self.iniciar_sesion())

    # ---------------- Funciones ----------------
    def alternar_contraseña(self):
        if self.clave.cget("show") == "•":
            self.clave.configure(show="")
            self.btn_toggle.configure(text="🔓")
        else:
            self.clave.configure(show="•")
            self.btn_toggle.configure(text="🔒")

    def iniciar_sesion(self):
        usuario = self.usuario.get().strip()
        contrasena = self.clave.get()
        if not usuario or not contrasena:
            messagebox.showerror("Error", "Ingrese usuario y contraseña.")
            return

        try:
            from ui.principal.session_manager import set_sesion
            from db_controller import connect_to_sql

            # Intentar conexión (esperamos que connect_to_sql retorne (conn, rol) o (None, None) al fallar)
            conn, rol = connect_to_sql(usuario, contrasena)

            if conn:
                # Guardar sesión *solo* cuando la conexión OK
                set_sesion(usuario, contrasena)
                # Opcional: almacenar rol en sesión si lo necesitas
                self.exito = True
                self.destroy()
            else:
                # Conexión inválida: informar y no cerrar la ventana
                messagebox.showerror("Error de autenticación", "Usuario o contraseña incorrectos.")
                return
        except Exception as e:
            # Mensaje claro + log para depuración
            print("Error en iniciar_sesion:", repr(e))
            messagebox.showerror("Error", f"No se pudo conectar: {str(e)}")
            return

# ---------------- Main ----------------
# if __name__ == "__main__":
#     root = ctk.CTk()
#     root.withdraw()  # Ocultamos la raíz inicialmente

#     # Abrimos Login como modal
#     login = Login()
#     login.grab_set()           # Bloquea la ventana principal
#     root.wait_window(login)    # Espera hasta que Login se cierre

#     # ---------------- Dashboard ----------------
#     from ui.principal.main import Dashboard
#     dashboard = Dashboard(master=root)  # Usamos la misma raíz
# #    dashboard.pack(fill="both", expand=True)
#     root.deiconify()  # Mostramos root (ahora Dashboard)
#     root.mainloop()   # Solo 1 mainloop

if __name__ == "__main__":
    root = ctk.CTk()
    root.withdraw()
    login = Login(master=root)   # <-- pasar root como master
    # No es necesario llamar login.grab_set() aquí porque ya lo hace en __init__
    root.wait_window(login)

    # ✅ Solo abrir Dashboard si el login fue exitoso
    if getattr(login, "exito", False):
        print('ya me loguee bien')
        from ui.principal.main import Dashboard
        dashboard = Dashboard(master=root)
        root.deiconify()
        root.mainloop()
    else:
        root.destroy()  # <- Cierra todo si el login falló o se canceló
