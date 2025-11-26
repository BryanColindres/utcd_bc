import customtkinter as ctk
from tkinter import ttk, messagebox, font as tkFont
import sys, os
from datetime import datetime
from datetime import timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from db_controller import obtener_horas_grua, eliminar_horas_grua, actualizar_horas_grua,obtener_orden_compra,obtener_id_sector,obtener_rol,obtener_horas_grua_completo,obtener_sectores

class VerReportes(ctk.CTkFrame):
    def __init__(self, parent):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.current_data = []  # Guarda los datos actualmente visibles (filtrados o completos)

        super().__init__(parent, fg_color="white")
        # Guardamos los anchos iniciales
        
        self.sectores = obtener_sectores()


        # 🔹 Etiqueta de conteo de filas
        self.row_count_label = ctk.CTkLabel(
            self,
            text="Filas visibles: 0",
            font=("Poppins", 12, "bold"),
            text_color="#2C3E50"
        )
        self.row_count_label.pack(pady=(0, 10))

        # crear dict inverso para obtener nombre a partir de id si es necesario
        self.sectores_id_a_nombre = {v: k for k, v in self.sectores.items()}
        self.id_sector = obtener_id_sector()  # Para filtrar órdenes de compra
        self.rol = obtener_rol()
        print(f'en ver resportes el id es {self.id_sector}')
        # Variables para filtros
        self.active_filters = {}       # Guardará los filtros activos por columna
        self.filter_windows = {}       # Para no abrir varias ventanas del mismo filtro

        # Título
        ctk.CTkLabel(self, text="Reportes de Uso de Grúa 📊", font=("Poppins", 22, "bold"), text_color="#E74C3C").pack(pady=(20,10))

        # Contenedor tabla
        table_container = ctk.CTkFrame(self, fg_color="white")
        table_container.pack(fill="both", expand=True, padx=20, pady=10)

        # Scrollbars
        self.v_scroll = ctk.CTkScrollbar(table_container, orientation="vertical")
        self.v_scroll.pack(side="right", fill="y")
        self.h_scroll = ctk.CTkScrollbar(table_container, orientation="horizontal")
        self.h_scroll.pack(side="bottom", fill="x")
        
        if self.rol == 'admin':
            # Columnas
            self.columns = [
                "ID", "FECHA_UTILIZACION", "SERVICIO_UTILIZADO", "UNIDAD_DE_MEDIDA",
                "HORA_DE_INICIO", "HORA_FINAL", "CANTIDAD_UTILIZADA", "JUSTIFICACION", "RESPONSABLE","ORDEN_COMPRA",'id_sector'
            ]
            self.column_headers = [
                "ID", "FECHA UTILIZACIÓN", "SERVICIO UTILIZADO", "UNIDAD DE MEDIDA",
                "HORA DE INICIO", "HORA FINAL", "CANTIDAD UTILIZADA",
                "JUSTIFICACIÓN", "RESPONSABLE", "ORDEN COMPRA",'SECTOR'
            ]
        else:
            # Columnas
            self.columns = [
                "ID", "FECHA_UTILIZACION", "SERVICIO_UTILIZADO", "UNIDAD_DE_MEDIDA",
                "HORA_DE_INICIO", "HORA_FINAL", "CANTIDAD_UTILIZADA", "JUSTIFICACION", "RESPONSABLE","ORDEN_COMPRA"
            ]
            self.column_headers = [
                "ID", "FECHA UTILIZACIÓN", "SERVICIO UTILIZADO", "UNIDAD DE MEDIDA",
                "HORA DE INICIO", "HORA FINAL", "CANTIDAD UTILIZADA",
                "JUSTIFICACIÓN", "RESPONSABLE", "ORDEN COMPRA"
            ]
        self.colums_editables = ["FECHA_UTILIZACION","HORA_DE_INICIO","CANTIDAD_UTILIZADA", "HORA_FINAL", "JUSTIFICACION", "RESPONSABLE","ORDEN_COMPRA"]
        self.column_widths_iniciales = {col: 130 for col in self.columns}  # ancho por defecto
        # Treeview
        self.tree = ttk.Treeview(
            table_container,
            columns=self.columns,
            show="headings",
            selectmode="extended",
            yscrollcommand=self.v_scroll.set,
            xscrollcommand=self.h_scroll.set
        )
        self.tree.pack(fill="both", expand=True)
        self.v_scroll.configure(command=self.tree.yview)
        self.h_scroll.configure(command=self.tree.xview)

        # Estilo moderno
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
        self.tree.configure(style="Custom.Treeview")

        # Configurar encabezados y clic para filtro
        for col, header in zip(self.columns, self.column_headers):
            self.tree.heading(col, text=header, command=lambda c=col: self.mostrar_columna_filtrada(c))
            self.tree.column(col, anchor="center", width=120, stretch=True)

        # Botones
        button_frame = ctk.CTkFrame(self, fg_color="white")
        button_frame.pack(pady=10)
        ctk.CTkButton(button_frame, text="🔄 Refrescar", fg_color="#3498DB", hover_color="#2980B9",
                      command=self.cargar_tabla).grid(row=0, column=0, padx=5)
        # ctk.CTkButton(button_frame, text="🗑️ Eliminar seleccionado", fg_color="#E74C3C", hover_color="#C0392B",
        #               command=self.eliminar_seleccion).grid(row=0, column=1, padx=5)
        ctk.CTkButton(button_frame, text="✏️ Editar seleccionado", fg_color="#F39C12", hover_color="#D68910",
                      command=self.editar_seleccion).grid(row=0, column=1, padx=5)
        ctk.CTkButton(button_frame, text="📤 Exportar", fg_color="#056F4E", hover_color="#026033",
                    command=self.exportar_excel).grid(row=0, column=2, padx=5)


        self.cargar_tabla()


    def get_treeview_data(self):
        """Devuelve los datos actualmente visibles en la tabla (ya filtrados)."""
        data = []
        for row in self.current_data:
            # Excluir las dos últimas columnas si existen
            data.append(row[:-2] if len(row) > 2 else row)
        return data

    def actualizar_conteo_filas(self):
        total = len(self.current_data)
        self.row_count_label.configure(text=f"Resgistros: {total}")


    def exportar_excel(self):
        """Exporta los datos visibles (filtrados o completos) a Excel."""
        try:
            data = self.get_treeview_data()
            if not data:
                messagebox.showwarning("Sin datos", "No hay datos visibles para exportar.")
                return

            from .exportar import export_to_excel
            export_to_excel(data, columns=self.column_headers)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar los datos:\n{e}")


    # ------------------- CARGAR TABLA -------------------
    def cargar_tabla_(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        data = obtener_horas_grua(self.id_sector)
        sectores = obtener_sectores()  # {nombre: id}
        sectores_id_a_nombre = {v: k for k, v in sectores.items()}  # invertimos el diccionario

        for row in data:
            row = list(row)  # convertir a lista editable
            if len(row) > 1:
                id_sector = row[1]
                # Reemplazar por el nombre si existe
                row[1] = sectores_id_a_nombre.get(id_sector, f"ID {id_sector}")
            str_row = [str(cell) if cell is not None else "" for cell in row]
            self.tree.insert("", "end", values=str_row)
        for row in data:
            str_row = [str(cell) if cell is not None else "" for cell in row]
            self.tree.insert("", "end", values=str_row)

        self.auto_ajustar_columnas()

    def cargar_tabla(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        rol = obtener_rol()
        if rol == 'admin':
            print(f'SOY ROL {rol}')
            data = obtener_horas_grua_completo()
            sectores = obtener_sectores()  # {nombre: id}
            sectores_id_a_nombre = {v: k for k, v in sectores.items()}  # invertimos el diccionario

            for row in data:
                row = list(row)  # convertir a lista editable
                if len(row) > 1:
                    id_sector = row[-1]  # 🔹 último campo es id_sector
                    # Reemplazar solo ese por el nombre
                    row[-1] = sectores_id_a_nombre.get(id_sector, f"{id_sector}")

                str_row = [str(cell) if cell is not None else "" for cell in row]
                self.tree.insert("", "end", values=str_row)
        else:
            print(f'SOY ROL {rol}')
            data = obtener_horas_grua(self.id_sector)

            str_data = [[str(cell) if cell is not None else "" for cell in row] for row in data]
            for row in str_data:
                self.tree.insert("", "end", values=row)

        # Guarda los datos cargados en memoria
        self.current_data = [[str(cell) if cell is not None else "" for cell in row] for row in data]

        # Restaurar anchos iniciales
        for col, width in self.column_widths_iniciales.items():
            self.tree.column(col, width=width)

        self.limpiar_todos_los_filtros()



    # ------------------- AJUSTE DE COLUMNAS -------------------
    def auto_ajustar_columnas_(self):
        fnt = tkFont.Font()
        for col in self.columns:
            max_width = fnt.measure(col)+25
            for item in self.tree.get_children():
                cell_text = str(self.tree.item(item)['values'][self.columns.index(col)])
                width = fnt.measure(cell_text) + 25
                if width > max_width:
                    max_width = width
            self.tree.column(col, width=max_width)

    def auto_ajustar_columnas(self):
        fnt = tkFont.Font()
        MAX_COLUMN_WIDTH = 400
        for col in self.columns:
            max_width = fnt.measure(col) + 25
            for item in self.tree.get_children():
                cell_text = str(self.tree.item(item)['values'][self.columns.index(col)])
                width = fnt.measure(cell_text) + 25
                if width > max_width:
                    max_width = width
            self.tree.column(col, width=min(max_width, MAX_COLUMN_WIDTH), stretch=False)
            self.column_widths_iniciales[col] = min(max_width, MAX_COLUMN_WIDTH)

    # ------------------- COLOR ALTERNADO -------------------
    def color_alternado(self):
        for i, item in enumerate(self.tree.get_children()):
            self.tree.item(item, tags=("even",) if i % 2 == 0 else ("odd",))
        self.tree.tag_configure("even", background="#FDEDEC")
        self.tree.tag_configure("odd", background="#FADBD8")

    # ------------------- ELIMINAR -------------------
    def eliminar_seleccion(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Atención", "Seleccione al menos una fila para eliminar.")
            return
        confirm = messagebox.askyesno("Confirmar", "¿Desea eliminar las filas seleccionadas?")
        if confirm:
            for item in selected:
                row_id = self.tree.item(item)['values'][0]
                eliminar_horas_grua(row_id)
            self.cargar_tabla()

    # ------------------- EDITAR -------------------
    def editar_seleccion(self):
        selected = self.tree.selection()
        if len(selected) != 1:
            messagebox.showwarning("Atención", "Seleccione solo una fila para editar.")
            return

        item = selected[0]
        valores = self.tree.item(item)['values']

        self.fecha_uso = valores[1]
        fecha_limite = datetime.strptime(self.fecha_uso, "%Y-%m-%d").date() 
        fecha_uso = datetime.now().date() - timedelta(days=7)
        print(f"Fecha de uso: {fecha_uso}, Fecha límite: {fecha_limite}")
        if fecha_limite < fecha_uso:
            messagebox.showerror("Error", "No se puede editar un registro con más de 7 días de antigüedad.")
            return
        
        # --- Ventana de edición ---
        edit_win = ctk.CTkToplevel(self)
        edit_win.title(f"Editar ITEM {valores[0]}")
        edit_win.grab_set()

        # Tamaño fijo y centrado
        ancho_ventana = 500
        alto_ventana = 700
        x = (self.winfo_screenwidth() // 2) - (ancho_ventana // 2)
        y = (self.winfo_screenheight() // 2) - (alto_ventana // 2)
        edit_win.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")

        # --- Frame con scroll ---
        frame_canvas = ctk.CTkFrame(edit_win, fg_color="black")
        frame_canvas.pack(fill="both", expand=True, padx=10, pady=10)

        canvas = ctk.CTkCanvas(frame_canvas, bg="black", highlightthickness=0)
        scrollbar = ctk.CTkScrollbar(frame_canvas, orientation="vertical", command=canvas.yview)
        scrollable_frame = ctk.CTkFrame(canvas, fg_color="black")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- Variables ---
        self.ed_vars = {}
        entries = {}

        # --- Campos de edición ---
        for col in self.colums_editables:
            if col == "CANTIDAD_UTILIZADA":
                continue

            try:
                if col == "ORDEN_COMPRA":
                    valor = str(valores[self.columns.index(col)]).rjust(len(str(valores[self.columns.index(col)])), "0")
                else:
                    valor = valores[self.columns.index(col)]
            except ValueError:
                print(f"⚠️ Columna '{col}' no encontrada en self.columns")
                continue

            var = ctk.StringVar(value=str(valor))
            self.ed_vars[col] = var

            ctk.CTkLabel(
                scrollable_frame,
                text=col.replace("_", " ").upper(),
                anchor="w",
                text_color="#B2BCC6",
                font=("Poppins", 12, "bold")
            ).pack(anchor="w", padx=20, pady=(5, 0))

            # Campo JUSTIFICACION -> caja grande
            if col == "JUSTIFICACION":
                text_box = ctk.CTkTextbox(
                    scrollable_frame,
                    width=400,
                    height=150,
                    fg_color="#2D0101",
                    text_color="white"
                )
                text_box.insert("1.0", str(valor))
                text_box.pack(padx=20, pady=(0, 10))
                entries[col] = text_box
                continue

            # Campo ORDEN_COMPRA -> combo
            if col == "ORDEN_COMPRA":
                opciones = obtener_orden_compra(self.id_sector)
                combo = ctk.CTkOptionMenu(
                    scrollable_frame,
                    variable=var,
                    values=opciones,
                    width=350,
                    fg_color="#151010",
                    button_color="#E74C3C",
                    button_hover_color="#C0392B",
                    text_color="#D8D8D8",
                    dropdown_fg_color="#FFFFFF",
                    dropdown_text_color="#94A2B1"
                )
                combo.pack(padx=20, pady=(0, 10))
                entries[col] = combo
                continue

            # Campos no editables (ejemplo)
            if col in ["ID", "FECHA", "CANTIDAD_CALCULADA"]:  # ajusta según tu caso
                entry = ctk.CTkEntry(scrollable_frame, textvariable=var, width=350, state="disabled",
                                    fg_color="#372C2C", text_color="white")
            else:
                entry = ctk.CTkEntry(scrollable_frame, textvariable=var, width=350,
                                    fg_color="#330404", text_color="white")

            entry.pack(padx=20, pady=(0, 10))
            entries[col] = entry

        # --- Función para calcular cantidad ---
        def calcular_cantidad():
            try:
                hi_var = self.ed_vars.get("HORA_INICIO") or self.ed_vars.get("HORA_DE_INICIO")
                hf_var = self.ed_vars.get("HORA_FINAL")
                hi, hf = hi_var.get().strip(), hf_var.get().strip()
                if not hi or not hf:
                    return False

                fmt = "%H:%M:%S" if len(hi.split(":")) == 3 else "%H:%M"
                inicio = datetime.strptime(hi, fmt)
                final = datetime.strptime(hf, fmt)

                if final <= inicio:
                    messagebox.showerror("Error", "La HORA FINAL debe ser mayor que la HORA DE INICIO.")
                    return False

                delta = final - inicio
                total_min = int(delta.total_seconds() // 60)
                horas, minutos = divmod(total_min, 60)
                return f"{horas:02d}:{minutos:02d}"

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo calcular la cantidad utilizada:\n{str(e)}")
                return False

        # --- Botón para cerrar/guardar ---
        def guardar_cambios():
            cantidad = calcular_cantidad()
            if not cantidad:
                return  # No hace nada si hay error

            actualizar_horas_grua(
                FECHA_UTILIZACION=self.ed_vars.get("FECHA_UTILIZACION", ctk.StringVar(value=valores[self.columns.index("FECHA_UTILIZACION")])).get().strip(),
                HORA_DE_INICIO=(self.ed_vars.get("HORA_INICIO") or self.ed_vars.get("HORA_DE_INICIO")).get().strip(),
                CANTIDAD_UTILIZADA=cantidad,
                HORA_FINAL=self.ed_vars.get("HORA_FINAL", ctk.StringVar(value=valores[self.columns.index("HORA_FINAL")])).get().strip(),
                JUSTIFICACION=entries["JUSTIFICACION"].get("1.0", "end").strip() if "JUSTIFICACION" in entries else "",
                RESPONSABLE=self.ed_vars.get("RESPONSABLE", ctk.StringVar(value=valores[self.columns.index("RESPONSABLE")])).get().strip(),
                ORDEN_COMPRA=self.ed_vars.get("ORDEN_COMPRA", ctk.StringVar(value=valores[self.columns.index("ORDEN_COMPRA")])).get().strip(),
                id=valores[0]
            )
            edit_win.destroy()  # Solo se cierra después de guardar
            self.cargar_tabla()

        ctk.CTkButton(
            scrollable_frame,
            text="Guardar Cambios",
            fg_color="#60DAFF",
            hover_color="#F4F4F4",
            text_color="black",
            font=("Poppins", 13, "bold"),
            command=guardar_cambios
        ).pack(pady=20)
        
        



    # ------------------- FILTROS POR COLUMNA -------------------
    def mostrar_columna_filtrada(self, column):
        # Cerrar ventana de filtro si ya está abierta
        if column in self.filter_windows:
            self.filter_windows[column].destroy()

        # Crear ventana de filtro
        filter_win = ctk.CTkToplevel(self)
        filter_win.title(f"Filtrar {column}")
        filter_win.geometry("300x400")
        filter_win.transient(self)

        # Obtener valores únicos
        unique_values = self.get_unique_values(column)
        if not unique_values:
            ctk.CTkLabel(filter_win, text="No hay valores disponibles").pack(pady=10)
            return

        # Entrada de búsqueda
        search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(filter_win, textvariable=search_var, placeholder_text="Buscar...")
        search_entry.pack(pady=5, padx=5, fill='x')

        # Frame desplazable
        scroll_frame = ctk.CTkScrollableFrame(filter_win)
        scroll_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Variables y widgets de checkboxes
        check_vars = {}
        checkboxes = {}

        def update_checkboxes():
            search_text = search_var.get().lower()
            for value, checkbox in checkboxes.items():
                if search_text in str(value).lower():
                    checkbox.pack(anchor='w', padx=5, pady=2)
                else:
                    checkbox.pack_forget()

        # Crear checkboxes
        for value in unique_values:
            var = ctk.BooleanVar(value=value in self.active_filters.get(column, []))
            chk = ctk.CTkCheckBox(scroll_frame, text=str(value), variable=var)
            chk.pack(anchor='w', padx=5, pady=2)
            check_vars[value] = var
            checkboxes[value] = chk

        # Escuchar cambios en el texto del Entry
        search_var.trace_add("write", lambda *args: update_checkboxes())

        # Botones de acción
        btn_frame = ctk.CTkFrame(filter_win)
        btn_frame.pack(pady=5, fill='x')

        ctk.CTkButton(btn_frame, text="Aplicar", command=lambda: self.aplicar_filtros_de_columna(column, check_vars, filter_win)).pack(side='left', padx=5)
        ctk.CTkButton(btn_frame, text="Limpiar", command=lambda: self.limpiar_filtros_de_columna(column, filter_win)).pack(side='left', padx=5)

        self.filter_windows[column] = filter_win

    def aplicar_filtros_de_columna(self, column, check_vars, window):
        selected = [value for value, var in check_vars.items() if var.get()]
        if selected:
            self.active_filters[column] = selected
        else:
            self.active_filters.pop(column, None)
        window.destroy()
        self.aplicar_filtro_activos()

    def limpiar_filtros_de_columna(self, column, window):
        self.active_filters.pop(column, None)
        window.destroy()
        self.aplicar_filtro_activos()

    def limpiar_todos_los_filtros(self):
        # Vaciar todos los filtros activos
        self.active_filters.clear()
        
        # Cerrar todas las ventanas de filtros abiertas
        for win in self.filter_windows.values():
            if win.winfo_exists():  # Solo si la ventana sigue abierta
                win.destroy()
        self.filter_windows.clear()
        
        # Reaplicar filtro (ahora sin ninguno)
        self.aplicar_filtro_activos()

    def get_unique_values(self, column):
        idx = self.columns.index(column)
        values = set()
        for item in self.tree.get_children():
            fila = self.tree.item(item)['values']
            if len(fila) <= idx:
                continue
            val = fila[idx]
            if val not in (None, "", " "):
                values.add(val)
        # Convertir todos los valores a string para evitar error de comparación
        values_str = [str(v) for v in values]
        return sorted(values_str)

    def aplicar_filtro_activos(self):
        # Limpiar tabla actual
        for row in self.tree.get_children():
            self.tree.delete(row)

        rol = obtener_rol()
        sectores = obtener_sectores()
        sectores_id_a_nombre = {v: k for k, v in sectores.items()}

        # Obtener datos según rol
        if rol == 'admin':
            data = obtener_horas_grua_completo()
        else:
            data = obtener_horas_grua(self.id_sector)

        # 🔹 Convertir id_sector (última columna) a nombre de sector
        data_modificada = []
        for row in data:
            row = list(row)
            if len(row) > 1 and self.rol == 'admin':  # admin tiene columna de sector
                id_sector = row[-1]  # ✅ último campo es id_sector
                row[-1] = sectores_id_a_nombre.get(id_sector, f"ID {id_sector}")
            data_modificada.append(row)

        # Convertir a string
        str_data = [[str(cell) if cell is not None else "" for cell in row] for row in data_modificada]

        # Aplicar filtros activos
        filtered = []
        for row in str_data:
            keep = True
            for col, allowed in self.active_filters.items():
                idx = self.columns.index(col)
                if row[idx] not in allowed:
                    keep = False
                    break
            if keep:
                filtered.append(row)

        # Actualizar datos visibles
        self.current_data = filtered

        for row in filtered:
            self.tree.insert("", "end", values=row)
        self.actualizar_conteo_filas()  # ✅ Actualizar conteo después de aplicar filtros
