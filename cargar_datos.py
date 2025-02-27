import pandas as pd
import mysql.connector
import threading
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import filedialog, messagebox
from sqlalchemy import create_engine
from ttkbootstrap import Style
from ttkbootstrap.widgets import Progressbar

# Configuración de Base de datos
USER = "admin"
PASSWORD = "manager"
HOST = "localhost"
DATABASE = "ventas_videojuegos"

# Conexión MySQL
engine = create_engine(f"mysql+mysqlconnector://{USER}:{PASSWORD}@{HOST}/{DATABASE}")

# Función para seleccionar archivo
def seleccionar_archivo():
    archivo = filedialog.askopenfilename(filetypes=[("Archivos Excel", "*.xlsx")])
    if archivo:
        entry_archivo.delete(0, tk.END)
        entry_archivo.insert(0, archivo)

# Función para cargar datos
def cargar_datos():
    archivo = entry_archivo.get()
    if not archivo:
        messagebox.showerror("Error", "Selecciona un archivo Excel")
        return

    btn_cargar.config(state=tk.DISABLED)
    progress["value"] = 0
    lbl_progreso.config(text="Cargando datos...")

    def proceso_carga():
        try:
            df = pd.read_excel(archivo, engine="openpyxl")
            df.columns = ["nombre", "plataforma", "anio", "genero", "editorial", 
                        "ventas_na", "ventas_eu", "ventas_jp", "ventas_otros", "ventas_global"]

            df["editorial"].fillna("Desconocido", inplace=True)

            total_filas = len(df)
            if total_filas == 0:
                messagebox.showwarning("Advertencia", "El archivo está vacío")
                return

            progreso_por_fila = 100 / total_filas

            with engine.begin() as conn:
                for i, row in df.iterrows():
                    row.to_frame().T.to_sql(name="datos_videojuegos", con=conn, if_exists="append", index=False)
                    progress["value"] += progreso_por_fila
                    ventana.update_idletasks()

            messagebox.showinfo("Éxito", "Datos cargados correctamente")
            lbl_progreso.config(text="Carga completada")
        except Exception as e:
            messagebox.showerror("Error", f"Error en la carga: {e}")
        finally:
            btn_cargar.config(state=tk.NORMAL)

    threading.Thread(target=proceso_carga).start()

# Interfaz gráfica
ventana = tk.Tk()
ventana.title("Cargar datos a Base de datos")
ventana.geometry("500x250")

style = Style(theme="flatly")

# Ruta Imagen
imagen = Image.open("logoUMG.png")
imagen = imagen.resize((40, 40))
imagen_tk = ImageTk.PhotoImage(imagen)

label_imagen = tk.Label(ventana, image=imagen_tk)
label_imagen.pack(pady=10)

# Etiqueta y entrada para seleccionar archivo
tk.Label(ventana, text="Nombre del archivo: ").pack(pady=5)
entry_archivo = tk.Entry(ventana, width=50)
entry_archivo.pack(pady=5)
tk.Button(ventana, text="Seleccionar el archivo (Excel.xlsx): ", command=seleccionar_archivo).pack(pady=5)

btn_cargar = tk.Button(ventana, text="Cargar Datos", command=cargar_datos)
btn_cargar.pack(pady=10)

# Barra de progreso
progress = Progressbar(ventana, length=400, mode="determinate")
progress.pack(pady=5)

# Etiqueta de estado
lbl_progreso = tk.Label(ventana, text="")
lbl_progreso.pack(pady=5)

ventana.mainloop()
