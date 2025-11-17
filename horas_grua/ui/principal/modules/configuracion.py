import customtkinter as ctk

class AcercaDe(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="white")

        # Título principal
        ctk.CTkLabel(
            self,
            text="Acerca de la aplicación ℹ️",
            font=("Poppins", 22, "bold"),
            text_color="#1a1a1a"
        ).pack(pady=(40, 10))

        # Descripción general
        ctk.CTkLabel(
            self,
            text=(
                "Esta aplicación fue desarrollada para optimizar la gestión y control de las horas de grúa, "
                "facilitando el registro, edición y exportación de la información.\n\n"
                "Incorpora un bot de alerta que notifica automáticamente cuando se sobrepasa el 70% "
                "del total de horas disponibles.\n\n"
                "Además, el sistema permite agregar nuevas órdenes de compra junto con su soporte correspondiente, "
                "así como desactivar aquellas que ya no se utilizan. También ofrece un monitoreo continuo del uso "
                "y disponibilidad de las horas grua."
            ),
            font=("Poppins", 14),
            text_color="#333333",
            wraplength=600,
            justify="center"
        ).pack(pady=10)

        # Información del desarrollador
        info_frame = ctk.CTkFrame(self, fg_color="#f4f4f4", corner_radius=10)
        info_frame.pack(pady=30, padx=20, fill="x")

        ctk.CTkLabel(
            info_frame,
            text="Desarrollado por:",
            font=("Poppins", 16, "bold"),
            text_color="#1a1a1a"
        ).pack(pady=(10, 0))

        ctk.CTkLabel(
            info_frame,
            text="CG - Gestión de la Información ",
            font=("Poppins", 14),
            text_color="#333333"
        ).pack(pady=5)

        ctk.CTkLabel(
            info_frame,
            text="Versión: 1.0.0\n© 2025",
            font=("Poppins", 13),
            text_color="#555555"
        ).pack(pady=(10, 15))
        
        ctk.CTkLabel(
            info_frame,
            text="Para soporte contactar a: bryan.colindres@eneeutcd.hn, cristian.umanzor@eneeutcd.hn, ruben.ayestas@eneeutcd.hn ",
            font=("Poppins", 12),
            text_color="#555555"
        ).pack(pady=5)
