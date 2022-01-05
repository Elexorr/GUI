import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo

root = tk.Tk()
root.title("GUI grid")
root.resizable(True, False)

xx = root.winfo_screenwidth()
yy = root.winfo_screenheight()


def select_file():
    filetypes = (('text files', '*.txt'), ('All files', '*.*'))
    filename = fd.askopenfilename(title='Open a file',
                                  initialdir='/', filetypes=filetypes)
    showinfo(title='Selected File', message=filename)


open_button = ttk.Button(root, text='Open a File', command=select_file)
open_button.pack(expand=True)

# frame1 = tk.Frame(master=root, width=xx/2, height=yy/2, bg="yellow")
window = tk.Canvas(width=xx - 153, height=yy - 150, bg="light grey")  # yy*0.9-80
frame2 = tk.Frame(master=root, width=150, height=yy - 146, bg="grey")  # yy*0.9-76
frame3 = tk.Frame(master=root, width=xx - 149, height=83, bg="grey")  # yy*0.1
frame4 = tk.Frame(master=root, width=150, height=83, bg="grey")  # y*0.1

window.grid(row=0, column=0, sticky=S)
frame2.grid(row=0, column=1, sticky=S)
frame3.grid(row=1, column=0, sticky=E)
frame4.grid(row=1, column=1, sticky=W)

root.mainloop()
