import tkinter as tk
from tkinter import TOP
from tkinter import BOTTOM

root = tk.Tk()
root.title("CurVarEn")

xx = root.winfo_screenwidth()
yy = root.winfo_screenheight()

geo = (str(xx) + "x" + str(yy))

root.geometry(geo)

for i in range(j):
    for j in range(2):
        frame = tk.Frame(master=window, relief=tk.RAISED, borderwidth=1)
        frame.grid(row=i, column=j)

plocha = tk.Canvas(master = root, width = xx - 200, height = yy - 200, bg ="red")
plocha.pack(side = tk.LEFT, expand=True)

frame1 = tk.Frame(master = root, width = 200, height = yy - 200, bg="grey")
# frame2.place(x = 0, y = 200)
frame1.pack(side = tk.RIGHT)

frame2 = tk.Frame(master = root, width = xx, height = 200, bg="grey")
frame2.pack(side = tk.BOTTOM)

# frame3 = tk.Frame(master=window, width=50, bg="blue")
# frame3.pack(fill=tk.Y, side=tk.LEFT)

# pozdrav = tk.Label(text = "Nazdar" + str(x)+ str(y), foreground = 'white', background = 'blue', width = 300, height = 10)
# pozdrav.pack()

# vstup = tk.Entry(fg="green", bg="light grey", width=50)
# vstup.pack()
#
# tlacidlo = tk.Button(text="Click me!", width=20, height=1, bg="grey", fg="yellow")
# tlacidlo.pack()

# menolabel = tk.Label(text = "Meno", width = 20)
# menoentry = tk.Entry(fg = "yellow", bg = "grey")
# menolabel.pack()
# menoentry.pack()

# vysledoklabel = tk.Label(text = meno, width = 20)
# vysledoklabel.pack()

# text_box = tk.Text()
# text_box.pack()

root.mainloop()
