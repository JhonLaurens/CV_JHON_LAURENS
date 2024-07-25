import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import ttkbootstrap as ttkb
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sqlite3
from mpl_toolkits.mplot3d import Axes3D

class CalculadoraPrestamo:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de Interés de Préstamo Avanzada")
        self.root.geometry("1400x800")
        self.root.resizable(True, True)

        self.style = ttkb.Style(theme="superhero")
        
        self.create_widgets()
        self.create_db()
        self.load_history()

    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame izquierdo para entrada de datos y resultados
        left_frame = ttk.Frame(main_frame, width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

        # Frame central para gráficos
        center_frame = ttk.Frame(main_frame)
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Frame derecho para historial contraíble
        self.right_frame = ttk.Frame(main_frame, width=300)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y, expand=False)

        # Widgets de entrada
        input_frame = ttk.Frame(left_frame)
        input_frame.pack(fill=tk.X, pady=10)

        ttk.Label(input_frame, text="Monto prestado:").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_monto = ttk.Entry(input_frame, width=20)
        self.entry_monto.grid(row=0, column=1, pady=5)

        ttk.Label(input_frame, text="Días del préstamo:").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_dias = ttk.Entry(input_frame, width=20)
        self.entry_dias.grid(row=1, column=1, pady=5)

        ttk.Label(input_frame, text="Valor a pagar:").grid(row=2, column=0, sticky="w", pady=5)
        self.entry_valor_pagar = ttk.Entry(input_frame, width=20)
        self.entry_valor_pagar.grid(row=2, column=1, pady=5)

        self.button_calcular = ttk.Button(left_frame, text="Calcular Interés", command=self.calcular_interes, style="Accent.TButton")
        self.button_calcular.pack(pady=20)

        self.resultado = tk.StringVar()
        self.label_resultado = ttk.Label(left_frame, textvariable=self.resultado, font=("Roboto", 12), wraplength=250, justify="center")
        self.label_resultado.pack(pady=10)

        # Frame para gráfica 3D
        self.graph_frame_3d = ttk.Frame(center_frame)
        self.graph_frame_3d.pack(fill=tk.BOTH, expand=True, pady=10)

        # Frame para gráfica de dispersión
        self.graph_frame_scatter = ttk.Frame(center_frame)
        self.graph_frame_scatter.pack(fill=tk.BOTH, expand=True, pady=10)

        # Historial contraíble
        self.history_visible = True
        self.toggle_button = ttk.Button(self.right_frame, text="Ocultar Historial", command=self.toggle_history)
        self.toggle_button.pack(pady=10)

        self.history_frame = ttk.Frame(self.right_frame)
        self.history_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(self.history_frame, text="Historial de Consultas", font=("Roboto", 14, "bold")).pack(pady=10)
        self.tree = ttk.Treeview(self.history_frame, columns=("Monto", "Días", "A Pagar", "Interés", "Porcentaje"), show="headings", height=15)
        self.tree.heading("Monto", text="Monto")
        self.tree.heading("Días", text="Días")
        self.tree.heading("A Pagar", text="A Pagar")
        self.tree.heading("Interés", text="Interés")
        self.tree.heading("Porcentaje", text="Porcentaje")
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)

    def toggle_history(self):
        if self.history_visible:
            self.history_frame.pack_forget()
            self.toggle_button.config(text="Mostrar Historial")
            self.right_frame.config(width=50)
        else:
            self.history_frame.pack(fill=tk.BOTH, expand=True)
            self.toggle_button.config(text="Ocultar Historial")
            self.right_frame.config(width=300)
        self.history_visible = not self.history_visible

    def create_db(self):
        self.conn = sqlite3.connect('prestamos.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS historial
                              (id INTEGER PRIMARY KEY,
                               monto REAL,
                               dias INTEGER,
                               valor_pagar REAL,
                               interes REAL,
                               porcentaje_interes REAL)''')
        self.conn.commit()

    def load_history(self):
        self.cursor.execute("SELECT * FROM historial")
        for row in self.cursor.fetchall():
            self.tree.insert("", "end", values=row[1:])
        self.actualizar_grafica_dispersion()

    def calcular_interes(self):
        try:
            monto = float(self.entry_monto.get())
            dias = int(self.entry_dias.get())
            valor_pagar = float(self.entry_valor_pagar.get())
            
            interes = valor_pagar - monto
            porcentaje_interes = (interes / monto) * 100
            interes_diario = porcentaje_interes / dias
            
            resultado = f"Interés: ${interes:.2f}\n" \
                        f"Porcentaje de interés total: {porcentaje_interes:.2f}%\n" \
                        f"Porcentaje de interés diario: {interes_diario:.4f}%"
            
            self.resultado.set(resultado)
            self.agregar_historial(monto, dias, valor_pagar, interes, porcentaje_interes)
            self.actualizar_grafica_3d(monto, interes, dias)
            self.actualizar_grafica_dispersion()

        except ValueError:
            messagebox.showerror("Error", "Por favor, ingrese valores numéricos válidos.")
        except ZeroDivisionError:
            messagebox.showerror("Error", "El número de días no puede ser cero.")

    def agregar_historial(self, monto, dias, valor_pagar, interes, porcentaje_interes):
        self.cursor.execute("INSERT INTO historial (monto, dias, valor_pagar, interes, porcentaje_interes) VALUES (?, ?, ?, ?, ?)",
                            (monto, dias, valor_pagar, interes, porcentaje_interes))
        self.conn.commit()
        self.tree.insert("", "end", values=(f"${monto:.2f}", dias, f"${valor_pagar:.2f}", f"${interes:.2f}", f"{porcentaje_interes:.2f}%"))

    def actualizar_grafica_3d(self, monto, interes, dias):
        for widget in self.graph_frame_3d.winfo_children():
            widget.destroy()

        fig = plt.figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111, projection='3d')
        
        fracs = [monto, interes]
        labels = ['Monto prestado', 'Interés']
        colors = ['#ff9999', '#66b3ff']
        
        def func(pct, allvals):
            absolute = int(round(pct/100.*sum(allvals)))
            return f"{pct:.1f}%\n(${absolute:d})"
        
        wedges, texts, autotexts = ax.pie(fracs, labels=labels, colors=colors, autopct=lambda pct: func(pct, fracs),
                                          shadow=True, startangle=90, radius=1)
        
        ax.bar(0, dias, zs=1, zdir='y', color='#99ff99', alpha=0.8, width=0.5)
        ax.text(0, 1, dias+5, f'{dias} días', ha='center', va='bottom')
        
        ax.set_title("Préstamo Actual")
        
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame_3d)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def actualizar_grafica_dispersion(self):
        for widget in self.graph_frame_scatter.winfo_children():
            widget.destroy()

        self.cursor.execute("SELECT monto, dias, porcentaje_interes FROM historial")
        datos = self.cursor.fetchall()

        if not datos:
            return

        montos, dias, porcentajes = zip(*datos)

        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
        scatter = ax.scatter(montos, dias, c=porcentajes, cmap='viridis', s=50)
        
        ax.set_xlabel('Monto prestado')
        ax.set_ylabel('Días del préstamo')
        ax.set_title('Historial de Préstamos')
        
        cbar = plt.colorbar(scatter)
        cbar.set_label('Porcentaje de interés')

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame_scatter)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def __del__(self):
        self.conn.close()

if __name__ == "__main__":
    root = ttkb.Window(themename="superhero")
    app = CalculadoraPrestamo(root)
    root.mainloop()