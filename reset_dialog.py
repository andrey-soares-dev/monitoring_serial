import tkinter as tk
from tkinter import ttk, messagebox

class SaveWindow():

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Salvar Dados")
        self.window.geometry("320x150")
        self.window.configure(bg="#f0f0f0")

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background="#f0f0f0", font=('Segoe UI', 10))
        style.configure('TButton', font=('Segoe UI', 10))
        style.configure('TEntry', font=('Segoe UI', 10))
        
        width = 300
        height = 150
        
        width_screen = self.window.winfo_screenwidth()
        height_screen = self.window.winfo_screenheight()

        pos_x = (width_screen // 2) - (width // 2)
        pos_y = (height_screen // 2) - (height // 2)
        
        self.window.geometry(f"{width}x{height}+{pos_x}+{pos_y}")

        self.window.attributes('-topmost', True)
        self.window.config(padx=20, pady=20)

        label_nome = ttk.Label(self.window, text="Insira o nome do arquivo:")
        label_nome.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))

        self.file_name = ttk.Entry(self.window, width=35)
        self.file_name.grid(row=1, column=0, columnspan=2, pady=(0, 15), ipady=3)
        self.file_name.focus()

        btn_ok = ttk.Button(self.window, text="OK", width=12, command=self.save)
        btn_ok.grid(row=2, column=0, padx=(0, 5), sticky="e")

        btn_cancelar = ttk.Button(self.window, text="Cancelar", width=12, command=self.cancel)
        btn_cancelar.grid(row=2, column=1, padx=(5, 0), sticky="w")

        self.name = None

        self.window.mainloop()

    def save(self):
        name = self.file_name.get()
        if name.strip():
            self.name = name
            messagebox.showinfo("Sucesso", f"Arquivo Salvo: {name}",parent=self.window)
            self.window.quit()
            self.window.destroy()
        else:
            messagebox.showwarning("Aviso", "Por favor, insira um nome!",parent=self.window)

    def cancel(self):
        if messagebox.askyesno("Confirmar", "Deseja confirmar o não salvamento do arquivo?",parent=self.window):
            self.window.quit()
            self.window.destroy()