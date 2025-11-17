import customtkinter as ctk
from tkinter import ttk, messagebox, font as tkFont
import sys, os
from datetime import datetime
from datetime import timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from db_controller import obtener_orden_compra_activos, eliminar_orden_compra,obtener_orden_compra_activos_todas_ordenes,actualizar_orden_compra,obtener_sectores

class Verorden(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="white")
        self.sectores = obtener_sectores()
        
        # crear dict inverso para obtener nombre a partir de id si es necesario
        self.sectores_id_a_nombre = {v: k for k, v in self.sectores.items()}
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

        # Columnas
        self.columns = [
            "FECHA","ID_SECTOR","ORDEN_COMPRA","CANTIDAD_HORAS","TIPO_EQUIPO","activo"
        ]
        self.column_headers = ["FECHA","ID_SECTOR","ORDEN_COMPRA","CANTIDAD_HORAS","TIPO_EQUIPO","activo"]
        self.columns_editables = ["FECHA","ID_SECTOR","ORDEN_COMPRA","CANTIDAD_HORAS","TIPO_EQUIPO","activo"]

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
        # Estilo moderno
        style = ttk.Style()
        style.theme_use("clam")

        # --- Filas ---
        style.configure(
            "Custom.Treeview",
            background="#FFFFFF",
            foreground="#2C3E50",
            fieldbackground="#FFFFFF",
            rowheight=30,
            font=("Poppins", 11)
        )

        # --- Encabezados ---
        style.configure(
            "Treeview.Heading",  # 👈 usar el nombre estándar
            background="#E74C3C",
            foreground="white",
            font=("Poppins", 12, "bold"),
            relief="flat"
        )
        style.map("Treeview.Heading",
                background=[('active', '#C0392B')],
                relief=[('pressed', 'flat'), ('!pressed', 'flat')])

        self.tree.configure(style="Custom.Treeview")


        # Configurar encabezados y clic para filtro
        for col, header in zip(self.columns, self.column_headers):
            self.tree.heading(col, text=header, command=lambda c=col: self.mostrar_columna_filtrada(c))
            self.tree.column(col, anchor="center", width=120, stretch=True)

        # Botones
        button_frame = ctk.CTkFrame(self, fg_color="white")
        button_frame.pack(pady=10)
        ctk.CTkButton(button_frame, text="🔄 Refrescar", fg_color="#3498DB", hover_color="#2980B9",
                      command=self.cargar_tabla_).grid(row=0, column=0, padx=5)
        ctk.CTkButton(button_frame, text="🗑️ Eliminar seleccionado", fg_color="#E74C3C", hover_color="#C0392B",
                      command=self.eliminar_seleccion).grid(row=0, column=1, padx=5)
        ctk.CTkButton(button_frame, text="✏️ Editar seleccionado", fg_color="#F39C12", hover_color="#D68910",
                      command=self.editar_seleccion).grid(row=0, column=2, padx=5)

        self.cargar_tabla()

    # ------------------- CARGAR TABLA -------------------
    def cargar_tabla_(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Obtener datos y sectores
        data = obtener_orden_compra_activos()
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

        self.auto_ajustar_columnas_()

    def cargar_tabla(self):
        # Limpiar tabla
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Obtener datos y sectores
        data = obtener_orden_compra_activos()
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
        self.color_alternado
        self.auto_ajustar_columnas()

    # ------------------- AJUSTE DE COLUMNAS -------------------
    def auto_ajustar_columnas_(self):
        fnt = tkFont.Font()
        for col in self.columns:
            max_width = fnt.measure(col)
            for item in self.tree.get_children():
                cell_text = str(self.tree.item(item)['values'][self.columns.index(col)])
                width = fnt.measure(cell_text) + 20
                if width > max_width:
                    max_width = width
            self.tree.column(col, width=max_width)

    def auto_ajustar_columnas(self):
        fnt = tkFont.Font()
        for col in self.columns:
            max_width = fnt.measure(col) + 25
            for item in self.tree.get_children():
                cell_text = str(self.tree.item(item)['values'][self.columns.index(col)])
                width = fnt.measure(cell_text) + 25
                if width > max_width:
                    max_width = width
            current_width = self.tree.column(col, option="width")
            if current_width < max_width:
                self.tree.column(col, width=max_width)

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
                eliminar_orden_compra(row_id)
            self.cargar_tabla()

    # ------------------- EDITAR -------------------
    def editar_seleccion(self):
        # Verificar si hay un registro seleccionado
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Atención", "Selecciona un registro primero.")
            return

        # Obtener los valores de la fila seleccionada
        valores = self.tree.item(item)["values"]
        print("📋 Valores seleccionados:", valores)

        self.orden_inicial = valores[2]  # Guardar orden original

        # Columnas esperadas (en el mismo orden que los valores)
        columnas = ["FECHA", "ID_SECTOR", "ORDEN_COMPRA", "CANTIDAD_HORAS", "TIPO_EQUIPO", "ACTIVO"]

        # Crear ventana
        edit_win = ctk.CTkToplevel(self)
        edit_win.title(f"Editar orden {valores[2]}")
        #edit_win.geometry("1200x1300")
        edit_win.grab_set()

        # --- Definir tamaño fijo y centrar ventana ---
        ancho, alto = 600, 450  # ajusta a gusto
        edit_win.geometry(f"{ancho}x{alto}")

        edit_win.update_idletasks()
        x = (edit_win.winfo_screenwidth() // 2) - (ancho // 2)
        y = (edit_win.winfo_screenheight() // 2) - (alto // 2)
        edit_win.geometry(f"{ancho}x{alto}+{x}+{y}")
        entries = {}

        for i, col in enumerate(columnas):
            ctk.CTkLabel(edit_win, text=col, width=140, anchor="e").grid(row=i, column=0, padx=10, pady=8, sticky="e")

            valor = valores[i]

            # --- Campo especial: ID_SECTOR ---
            if col.upper() == "ID_SECTOR":
                nombres_sectores = list(self.sectores.keys())
                entry = ctk.CTkComboBox(
                    edit_win,
                    values=nombres_sectores,
                    width=250,
                    state="readonly"
                )

                try:
                    valor_actual_id = valor
                    print(f'valor actual{valor_actual_id}')
                    nombre_sector = valor_actual_id
                    #self.sectores_id_a_nombre.get(valor_actual_id)
                    print(nombre_sector)
                    if nombre_sector:
                        entry.set(nombre_sector)
                    else:
                        entry.set(nombres_sectores[0])
                except Exception as e:
                    print(f"⚠️ Error asignando ID_SECTOR: {e}")
                    entry.set(nombres_sectores[0])

            # --- Campo especial: TIPO_EQUIPO ---
            elif col.upper() == "TIPO_EQUIPO":
                entry = ctk.CTkComboBox(
                    edit_win,
                    values=["GRUA", "CANASTA"],
                    width=250,
                    state="readonly"
                )
                entry.set(str(valor))

            # --- Campo especial: ACTIVO ---
            elif col.upper() == "ACTIVO":
                entry = ctk.CTkComboBox(
                    edit_win,
                    values=["0", "1"],
                    width=250,
                    state="readonly"
                )
                entry.set(str(valor))

            # --- Campos normales ---
            else:
                entry = ctk.CTkEntry(edit_win, width=250, fg_color="#FFFFFF", text_color="black")
                entry.insert(0, str(valor) if valor is not None else "")

            entry.grid(row=i, column=1, padx=10, pady=8, sticky="w")
            entries[col] = entry

            print(f"🟦 Columna: {col} → Valor cargado: {valor}")

        # --- Guardar cambios ---
        def guardar_cambios():
            try:
                ID_SECTOR_nombre = entries["ID_SECTOR"].get()
                ID_SECTOR_id = self.sectores.get(ID_SECTOR_nombre)

                if ID_SECTOR_id is None:
                    messagebox.showerror("Error", "El sector seleccionado no es válido.")
                    return

                actualizar_orden_compra(
                    FECHA=entries["FECHA"].get().strip(),
                    ID_SECTOR=ID_SECTOR_id,
                    ORDEN_COMPRA=entries["ORDEN_COMPRA"].get().strip(),
                    CANTIDAD_HORAS=int(entries["CANTIDAD_HORAS"].get().strip()),
                    TIPO_EQUIPO=entries["TIPO_EQUIPO"].get().strip(),
                    ACTIVO=int(entries["ACTIVO"].get().strip()),
                    orden_original=self.orden_inicial
                )

               # messagebox.showinfo("Éxito", "Orden de compra actualizada correctamente.")
                edit_win.destroy()
                self.cargar_tabla()

            except Exception as e:
                print(f"❌ Error al guardar: {e}")
                messagebox.showerror("Error", f"No se pudieron guardar los cambios:\n{e}")

        ctk.CTkButton(
            edit_win,
            text="💾 Guardar cambios",
            command=guardar_cambios,
            fg_color="#2b9348",
            hover_color="#1b6530",
            width=180
        ).grid(row=len(columnas), column=0, columnspan=2, pady=20)

        # # Centrar ventana
        # edit_win.update_idletasks()
        # w = edit_win.winfo_width()
        # h = edit_win.winfo_height()
        # x = (edit_win.winfo_screenwidth() // 2) - (w // 2)
        # y = (edit_win.winfo_screenheight() // 2) - (h // 2)
        # edit_win.geometry(f"{w}x{h}+{x}+{y}")







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
        for row in self.tree.get_children():
            self.tree.delete(row)

        data = obtener_orden_compra_activos()
        sectores = obtener_sectores()  # {nombre: id}
        sectores_id_a_nombre = {v: k for k, v in sectores.items()}  # invertimos el diccionario

        # 🔹 CORREGIDO: modificar los elementos dentro de 'data'
        data_modificada = []
        for row in data:
            row = list(row)
            if len(row) > 1:
                id_sector = row[1]
                row[1] = sectores_id_a_nombre.get(id_sector, f"ID {id_sector}")
            data_modificada.append(row)

        # convertir a texto
        str_data = [[str(cell) if cell is not None else "" for cell in row] for row in data_modificada]

        # aplicar filtros
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

        for row in filtered:
            self.tree.insert("", "end", values=row)

