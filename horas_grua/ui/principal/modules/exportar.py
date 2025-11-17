import pandas as pd
from tkinter import messagebox, filedialog

def export_to_excel(data, columns=None):
    try:
        if not data or len(data) == 0:
            messagebox.showerror("Error", "No se encontraron datos para exportar.")
            return

        if isinstance(data, pd.DataFrame):
            df = data.copy()
        else:
            if columns is None:
                n_cols = len(data[0]) if len(data) > 0 else 0
                columns = [f"Columna_{i+1}" for i in range(n_cols)]
            elif len(columns) != len(data[0]):  # Previene errores de longitud
                columns = columns[:len(data[0])]
            df = pd.DataFrame(data, columns=columns)

        # 🔸 Verificar si ya existe la columna ID antes de reemplazarla
        if 'ID' in df.columns:
            df['ID'] = range(1, len(df) + 1)
        else:
            df.insert(0, 'ID', range(1, len(df) + 1))

        # Guardar archivo
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Archivos Excel", "*.xlsx"), ("Todos los archivos", "*.*")]
        )
        if not file_path:
            messagebox.showwarning("Cancelado", "La exportación ha sido cancelada.")
            return

        df.to_excel(file_path, index=False)
        messagebox.showinfo("Éxito", f"Los datos se exportaron correctamente en:\n{file_path}")

    except Exception as e:
        messagebox.showerror("Error inesperado", f"Ocurrió un error al exportar:\n{e}")
