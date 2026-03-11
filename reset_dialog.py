import tkinter as tk
from tkinter import messagebox

class SaveWindow():

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Salvar")
        self.window.geometry("300x120")
        
        width = 300
        height = 150
        
        width_screen = self.window.winfo_screenwidth()
        height_screen = self.window.winfo_screenheight()

        pos_x = (width_screen // 2) - (width // 2)
        pos_y = (height_screen // 2) - (height // 2)
        
        self.window.geometry(f"{width}x{height}+{pos_x}+{pos_y}")

        self.window.attributes('-topmost', True)
        self.window.config(padx=20, pady=20)

        label_nome = tk.Label(self.window, text="Insira o nome do arquivo:")
        label_nome.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))

        self.file_name = tk.Entry(self.window, width=30)
        self.file_name.grid(row=1, column=0, columnspan=2, pady=(0, 15))
        self.file_name.focus()

        btn_ok = tk.Button(self.window, text="OK", width=10, command=self.save, bg="#e1e1e1")
        btn_ok.grid(row=2, column=0, padx=5)

        btn_cancelar = tk.Button(self.window, text="Cancelar", width=10, command=self.cancel)
        btn_cancelar.grid(row=2, column=1, padx=5)

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