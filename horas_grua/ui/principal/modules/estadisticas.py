import customtkinter as ctk
import matplotlib.pyplot as plt
import mplcursors  # para interactividad
import sys
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from db_controller import obtener_orden_compra, obtener_sectores, horas_para_grafico,obtener_rol,obtener_id_sector,obtener_proveedor_por_orden

def decimal_a_hhmm(horas_decimal):
    """Convierte horas decimales a HH:MM"""
    horas = int(horas_decimal)
    minutos = int(round((horas_decimal - horas) * 60))
    return f"{horas}:{minutos:02d}"

class Estadisticas(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="white")

        ctk.CTkLabel(self, text="Estadísticas 📈", font=("Poppins", 22, "bold")).pack(pady=(20, 10))
        ctk.CTkLabel(self, text="Gráficos de uso de órdenes de compra", font=("Poppins", 16)).pack(pady=(0, 20))

        # --- Filtro por sector ---
        filter_frame = ctk.CTkFrame(self, fg_color="white")
        filter_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(filter_frame, text="Filtrar por sector:", font=("Poppins", 14)).pack(side="left", padx=(0,10))
        rol = obtener_rol()

        if rol == 'admin':
            sectores_dict = obtener_sectores()  # Devuelve dict {nombre: id}
            self.sectores_nombres = list(sectores_dict.keys())
            self.sectores_dict = sectores_dict
            print('holis, soy admin', self.sectores_dict)
        else:
            sector_id = obtener_id_sector()  # Asegurate que sea una función que devuelve solo el id
            self.sectores_dict = {str(sector_id): sector_id}  # Lo envolvemos en dict
            self.sectores_nombres = [str(sector_id)]          # Lista con un solo nombre
            print('holis, no soy admin', self.sectores_dict)

        self.sector_var = ctk.StringVar()
        self.sector_var.set(self.sectores_nombres[0] if self.sectores_nombres else "")

        if rol == 'admin':
            self.sector_combo = ctk.CTkOptionMenu(
                filter_frame,
                variable=self.sector_var,
                values=self.sectores_nombres,
                width=200,
                fg_color="#E0E0E0",
                button_color="#3498DB",
                button_hover_color="#2980B9",
                text_color="#2C3E50",
                command=self.actualizar_graficos
            )
            self.sector_combo.pack(side="left", padx=10)

        # --- Contenedor de cuadros ---
        self.canvas_frame = ctk.CTkScrollableFrame(self, fg_color="white")
        self.canvas_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Inicializar gráficos
        self.actualizar_graficos()

    def actualizar_graficos(self, *args):
        # Crear ventana de cargando centrada
        cargando = ctk.CTkToplevel(self)
        cargando.title("Cargando...")
        cargando.geometry("350x100")
        cargando.grab_set()
        cargando.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() // 2) - 175
        y = self.winfo_rooty() + (self.winfo_height() // 2) - 50
        cargando.geometry(f"+{x}+{y}")
        ctk.CTkLabel(cargando, text="Generando gráficos, por favor espere...", font=("Poppins", 14)).pack(expand=True, pady=20)
        cargando.update()

        # Limpiar el frame
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        nombre_sector = self.sector_var.get()
        id_sector = self.sectores_dict.get(nombre_sector)
        if id_sector is None:
            cargando.destroy()
            return
        
        print('el id del sector es ',id_sector)
        data = obtener_orden_compra(id_sector)
        print('data de ordenes es ',data)
        try:
            ordenes = data["orden_compra"].tolist()
            equipos = data['tipo_equipo'].tolist()
            col = 0
            row = 0
            for i in range(len(data)):
                orden = ordenes[i]
                equipo = equipos[i]
                resultado = horas_para_grafico(id_sector, orden, {"CANTIDAD_UTILIZADA": "0"}, equipo)
                if resultado:
                    cuadro = self.crear_cuadro_orden(orden, resultado,equipo)
                    cuadro.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
                    col += 1
                    if col > 1:
                        col = 0
                        row += 1
            for i in range(2):
                self.canvas_frame.grid_columnconfigure(i, weight=1)
            cargando.destroy()
        except Exception as e:
            cargando.destroy()

    def crear_cuadro_orden(self, orden, resultado,equipo):
        cuadro = ctk.CTkFrame(self.canvas_frame, fg_color="#FDEDEC", corner_radius=15, height=250, width=250)
        cuadro.pack_propagate(False)
        
        proveedor = obtener_proveedor_por_orden(orden)
        ctk.CTkLabel(
            cuadro,
            text=f"{orden} - {equipo} - {proveedor}",
            font=("Poppins", 12, "bold"),
            text_color="#C0392B"
        ).pack(pady=(10,5))

        # --- Valores principales ---
        horas_usadas = float(resultado["Total_Usado"])
        horas_disponibles_decimal = float(resultado["Disponible_Decimal"])

        # Manejar valores negativos (excedente)
        excedido = 0
        if horas_disponibles_decimal < 0:
            excedido = abs(horas_disponibles_decimal)
            horas_disponibles_decimal = 0

        # Convertir a HH:MM
        horas_usadas_hhmm = decimal_a_hhmm(horas_usadas)
        horas_disponibles_hhmm = decimal_a_hhmm(horas_disponibles_decimal)
        excedido_hhmm = decimal_a_hhmm(excedido)

        # --- Evitar gráfico si todo es cero ---
        if horas_usadas == 0 and horas_disponibles_decimal == 0 and excedido == 0:
            ctk.CTkLabel(cuadro, text="Sin datos para graficar", font=("Poppins", 12)).pack(expand=True)
            return cuadro

        # --- Preparar datos para pie chart ---
        valores = [horas_usadas, horas_disponibles_decimal]
        labels = [f"Usadas ({horas_usadas_hhmm})", f"Disponibles ({horas_disponibles_hhmm})"]
        # Calcular proporción usada
        total_horas = horas_usadas + horas_disponibles_decimal + excedido
        proporcion_usada = horas_usadas / total_horas if total_horas > 0 else 0

        # Color dinámico
        if proporcion_usada >= 0.7:
            color_usada = "#E74C3C"  # rojo
        else:
            color_usada = "#F39C12"  # anaranjado
        color_disponible = "#2ECC71"

        colors = [color_usada, color_disponible]



        if excedido > 0:
            valores.append(excedido)
            labels.append(f"Excedido ({excedido_hhmm})")
            colors.append("#C0392B")  # rojo intenso para excedente

        # --- Dibujar gráfico ---
        fig, ax = plt.subplots(figsize=(3,3), dpi=100)
        wedges, texts, autotexts = ax.pie(
            valores,
            labels=labels,
            autopct=lambda pct: "",  # solo etiquetas
            colors=colors,
            startangle=90,
            shadow=True,
            wedgeprops=dict(width=0.4, edgecolor='w')
        )
        ax.axis("equal")

        # Interactividad con tooltips
        cursor = mplcursors.cursor(wedges, hover=True)
        cursor.connect(
            "add", lambda sel: sel.annotation.set_text(
                f"{labels[sel.index]}"
            )
        )

        canvas = FigureCanvasTkAgg(fig, master=cuadro)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill="both", pady=10, padx=10)

        return cuadro
