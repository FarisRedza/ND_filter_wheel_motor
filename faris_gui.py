import tkinter as tk
from tkinter import ttk  
import faris_cli

window = tk.Tk()
window.title("Faris' Automated RotatIng Standa (FARIS) Motor")
window.minsize(400,400)
frame = tk.Frame(master=window)
frame.pack(side=tk.LEFT, padx=10,pady=10)

def handle_button_press():
    window.destroy()

label = ttk.Label(text="Select option", master=frame)
label.pack(anchor=tk.W)

def set_option(option):
    selected_option.set(option)

selected_option = tk.StringVar()

def create_menu(menu: dict):
    width = max(len(value) for value in menu.values())
    for key, value in menu.items():
        button = tk.Button(text=value, command=lambda v=value: set_option(v), width=width, anchor="w", master=frame)
        button.pack(anchor=tk.W)

create_menu(faris_cli.menu_dict)
window.mainloop()