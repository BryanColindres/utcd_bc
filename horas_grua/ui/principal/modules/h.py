import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
import pyodbc

# ============================================================
# CONFIGURACIÓN SQL
# ============================================================
SERVER = "192.168.100.7"
DATABASE = "GestionControl"
USER = "bdc01755"
PASSWORD = "Honduras2026"

CONN_STR = (
    "DRIVER={SQL Server};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"UID={USER};"
    f"PWD={PASSWORD};"
   #" "Encrypt=yes;"
   # "TrustServerCertificate=yes;"
)

def get_connection():
    return pyodbc.connect(CONN_STR)

# ============================================================
# METADATOS DINÁMICOS
# ============================================================
def get_columns():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'BOT_CORREOS'
        ORDER BY ORDINAL_POSITION
    """)

    cols = [r[0] for r in cur.fetchall()]
    conn.close()

    base = ["NOMBRE", "CORREO"]
    flags = [c for c in cols if c not in base]

    return base, flags

# ============================================================
# APP PRINCIPAL
# ============================================================
class BotCorreosApp(tb.Window):

    def __init__(self):
        super().__init__(themename="flatly")
        self.title("Administrador BOT_CORREOS")
        self.geometry("1000x600")

        self.base_cols, self.flag_cols = get_columns()
        self.create_widgets()
        self.load_data()

    # --------------------------------------------------------
    def create_widgets(self):

        frame = tb.Frame(self, padding=10)
        frame.pack(fill=BOTH, expand=True)

        # ===== BUSCADOR =====
        search_frame = tb.Labelframe(frame, text="Buscar", padding=10)
        search_frame.pack(fill=X)

        self.search_entry = tb.Entry(search_frame, width=50)
        self.search_entry.pack(side=LEFT, padx=5)
        tb.Button(search_frame, text="Buscar", command=self.search).pack(side=LEFT)
        tb.Button(search_frame, text="Refrescar", command=self.load_data).pack(side=LEFT, padx=5)

        # ===== TABLA =====
        cols = self.base_cols + self.flag_cols
        self.tree = tb.Treeview(frame, columns=cols, show="headings", height=18)
        self.tree.pack(fill=BOTH, expand=True, pady=10)

        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=CENTER)

        self.tree.bind("<Double-1>", self.edit_selected)

        # ===== BOTONES =====
        btn_frame = tb.Frame(frame)
        btn_frame.pack(fill=X)

        tb.Button(btn_frame, text="➕ Agregar", bootstyle=SUCCESS, command=self.add).pack(side=LEFT)
        tb.Button(btn_frame, text="✏️ Editar", bootstyle=WARNING, command=self.edit_selected).pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="🗑 Eliminar", bootstyle=DANGER, command=self.delete).pack(side=LEFT)

    # --------------------------------------------------------
    def load_data(self, filtro=None):
        self.tree.delete(*self.tree.get_children())

        conn = get_connection()
        cur = conn.cursor()

        sql = f"SELECT {','.join(self.base_cols + self.flag_cols)} FROM BOT_CORREOS"
        params = []

        if filtro:
            sql += " WHERE NOMBRE LIKE ? OR CORREO LIKE ?"
            params = [f"%{filtro}%", f"%{filtro}%"]

        cur.execute(sql, params)

        for row in cur.fetchall():
            self.tree.insert("", END, values=row)

        conn.close()

    def search(self):
        self.load_data(self.search_entry.get())

    # --------------------------------------------------------
    def add(self):
        PersonForm(self)

    def edit_selected(self, event=None):
        item = self.tree.focus()
        if not item:
            messagebox.showwarning("Atención", "Seleccione un registro")
            return

        values = self.tree.item(item)["values"]
        data = dict(zip(self.base_cols + self.flag_cols, values))
        PersonForm(self, data)

    def delete(self):
        item = self.tree.focus()
        if not item:
            return

        correo = self.tree.item(item)["values"][1]

        if not messagebox.askyesno("Confirmar", f"Eliminar {correo}?"):
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM BOT_CORREOS WHERE CORREO = ?", correo)
        conn.commit()
        conn.close()
        self.load_data()

# ============================================================
# FORMULARIO DINÁMICO
# ============================================================
class PersonForm(tb.Toplevel):

    def __init__(self, parent, data=None):
        super().__init__(parent)
        self.parent = parent
        self.data = data or {}

        self.base_cols, self.flag_cols = get_columns()
        self.vars = {}

        self.title("Editar Persona" if data else "Agregar Persona")
        self.geometry("450x600")

        self.create_form()

    # --------------------------------------------------------
    def create_form(self):
        frame = tb.Frame(self, padding=15)
        frame.pack(fill=BOTH, expand=True)

        # ===== BASE =====
        for col in self.base_cols:
            tb.Label(frame, text=col).pack(anchor=W)
            var = tb.StringVar(value=self.data.get(col, ""))
            self.vars[col] = var
            entry = tb.Entry(frame, textvariable=var)
            entry.pack(fill=X, pady=2)
            if col == "CORREO" and self.data:
                entry.config(state=DISABLED)

        tb.Separator(frame).pack(fill=X, pady=10)

        # ===== FLAGS =====
        for col in self.flag_cols:
            var = tb.BooleanVar(value=(self.data.get(col) == "SI"))
            self.vars[col] = var
            tb.Checkbutton(
                frame,
                text=col.replace("_", " "),
                variable=var
            ).pack(anchor=W)

        tb.Button(frame, text="Guardar", bootstyle=SUCCESS, command=self.save).pack(pady=15)

    # --------------------------------------------------------
    def save(self):
        conn = get_connection()
        cur = conn.cursor()

        correo = self.vars["CORREO"].get()

        cur.execute("SELECT COUNT(*) FROM BOT_CORREOS WHERE CORREO = ?", correo)
        exists = cur.fetchone()[0] > 0

        columnas = self.base_cols + self.flag_cols
        valores = []

        for c in columnas:
            v = self.vars[c]
            if isinstance(v, tb.BooleanVar):
                valores.append("SI" if v.get() else "NO")
            else:
                valores.append(v.get())

        if exists:
            sets = ",".join([f"{c}=?" for c in columnas if c != "CORREO"])
            sql = f"UPDATE BOT_CORREOS SET {sets} WHERE CORREO=?"
            cur.execute(sql, valores[0:1] + valores[2:] + [correo])
        else:
            placeholders = ",".join(["?"] * len(columnas))
            sql = f"INSERT INTO BOT_CORREOS ({','.join(columnas)}) VALUES ({placeholders})"
            cur.execute(sql, valores)

        conn.commit()
        conn.close()
        self.parent.load_data()
        self.destroy()

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    app = BotCorreosApp()
    app.mainloop()
