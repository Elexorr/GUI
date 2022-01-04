import tkinter as tk
from tkinter import LEFT

root = tk.Tk()
root.title("CurVarEn")

x = root.winfo_screenwidth()
y = root.winfo_screenheight()

frame2 = tk.Frame(master = root, width = x/10, height = y * 0.9 - 80, bg="grey")
# frame2.place(x = 0, y = 200)
frame2.pack(side = LEFT, fill = tk.BOTH, expand=True)

plocha = tk.Canvas(width = x * 0.9, height = y * 0.9 - 80, bg ="red")
plocha.pack(fill = tk.BOTH, expand=True)

frame1 = tk.Frame(master = root, width = x, height = y * 0.1, bg="grey")
# frame1.place(x = 0, y = 0)
frame1.pack(fill = tk.BOTH, expand=True)

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
