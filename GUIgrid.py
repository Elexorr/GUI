import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
from astropy.modeling import models, fitting
from astropy.time import Time

root = tk.Tk()
root.title("GUI grid")
root.resizable(True, False)

xx = root.winfo_screenwidth()
yy = root.winfo_screenheight()

JDstr = []      # julian date list / strings
magstr = []     # mag list / strings
errstr = []     # error list / strings
JD = []         # julian date list / floats
mag = []        # mag list / floats
error = []      # error list / floats
x = []
y = []


def select_file():
    global lines
    filetypes = (('text files', '*.txt'), ('All files', '*.*'))
    filename = fd.askopenfilename(title='Open a file',
                                  initialdir='/', filetypes=filetypes)
    f = open(filename)
    lines = f.readlines()
    global JDay
    for i in range(2, len(lines)):              # extracting string data from source file
        if i == 2:
            JDay = str(lines[i][0:7])           # checking julian day
        if str(lines[i][16:18]) != '99':        # filtering invalid data
            JDstr.append(lines[i][0:15])        # julian dates
            magstr.append(lines[i][16:24])      # mags
            errstr.append(lines[i][25:32])      # error
    separatenumericalvalues()
    xyscale()
    drawcurve()
    # showinfo(title='Selected File', message=filename)


def separatenumericalvalues():
    for i in range(0, len(JDstr)):                          # creating numerical data
        JD.append(round(float(JDstr[i][0:15]) % 1, 7))      # julian dates
        mag.append(round(float(magstr[i][0:8]), 5))         # mags
        error.append(round(float(errstr[i][0:8]), 5))       # error


def xyscale():              # creating variables for scaling purposes
    global Maxmagvalue
    global Minmagvalue
    global magscale
    global timescale
    Maxmagvalue = 0
    Minmagvalue = 100
    magscale = 0
    for i in range(0, len(mag)):
        if mag[i] > Maxmagvalue:
            Maxmagvalue = mag[i]
        if mag[i] < Minmagvalue:
            Minmagvalue = mag[i]
        magscale = round(Maxmagvalue - Minmagvalue, 5)
    timescale = round((JD[len(JD) - 1] - JD[0]), 7)


def drawcurve():                # drawing axes, labels and curves
    window.create_rectangle(80, 0, xx-150, yy-210)     # |^^^^^^^^^^^^^^^
    window.create_text(20, 5, text='mag')               # |
    window.create_text(15, yy-195, text='JD')           # |

    window.create_line(75, 22 + (yy-250) * (Minmagvalue - Minmagvalue) / magscale,
                       86, 22 + (yy-250) * (Minmagvalue - Minmagvalue) / magscale)
    window.create_text(50, 22 + (yy-250) * (Minmagvalue - Minmagvalue) / magscale, text=Minmagvalue)
    window.create_line(75, 22 + (yy-250) * (Maxmagvalue - Minmagvalue) / magscale,
                       86, 22 + (yy-250) * (Maxmagvalue - Minmagvalue) / magscale)
    window.create_text(50, 22 + (yy-250) * (Maxmagvalue - Minmagvalue) / magscale, text=Maxmagvalue)
    window.create_text(50, yy-195, text=JDay + "+")

    jtime = Time(JDstr[0], format='jd')
    isotime = jtime.iso
    window.create_text(38, yy-180, text=isotime[0:10])
    window.create_text(102 + (xx - 290) * (JD[0] - JD[0]) / timescale, yy-180, text=isotime[11:23])

    window.create_line(102 + (xx - 290) * (JD[0] - JD[0]) / timescale, yy-210-5,
                       102 + (xx - 290) * (JD[0] - JD[0]) / timescale, yy-210+6)
    window.create_text(102 + (xx - 290) * (JD[0] - JD[0]) / timescale, yy-195, text=JD[0])

    window.create_line(102 + (xx - 290) * (JD[len(JD) - 1] - JD[0]) / timescale, yy-210-5,
                       102 + (xx - 290) * (JD[len(JD) - 1] - JD[0]) / timescale, yy-210+6)
    window.create_text(102 + (xx - 290) * (JD[len(JD) - 1] - JD[0]) / timescale, yy-195,
                       text=JD[len(JD) - 1])

    jtime = Time(JDstr[len(JDstr) - 1], format='jd')
    isotime = jtime.iso
    window.create_text(102 + (xx - 290) * (JD[len(JD) - 1] - JD[0]) / timescale, yy-180, text=isotime[11:23])

    for i in range(0, len(JD)):
        window.create_line(102 + (xx - 290) * (JD[i] - JD[0]) / timescale,        # drawing error bar
                           20 - error[i] * 1000 + (yy-250) * (mag[i] - Minmagvalue) / magscale,
                           102 + (xx - 290) * (JD[i] - JD[0]) / timescale,
                           25 + error[i] * 1000 + (yy-250) * (mag[i] - Minmagvalue) / magscale,
                           fill='red')
        window.create_rectangle(100 + (xx - 290) * (JD[i] - JD[0]) / timescale,   # drawing lightucrve
                                20 + (yy-250) * (mag[i] - Minmagvalue) / magscale,
                                104 + (xx - 290) * (JD[i] - JD[0]) / timescale,
                                24 + (yy-250) * (mag[i] - Minmagvalue) / magscale,
                                fill='red', outline='red')
        if i % 10 == 0:                                                     # drawing point numbers
            window.create_line(102 + (xx - 290) * (JD[i] - JD[0]) / timescale,
                               5 + 25 + error[i] * 1000 + (yy-250) * (mag[i] - Minmagvalue) / magscale,
                               102 + (xx - 290) * (JD[i] - JD[0]) / timescale,
                               40 + 25 + error[i] * 1000 + (yy-250) * (mag[i] - Minmagvalue) / magscale,
                               fill='grey')
            window.create_text(102 + (xx - 290) * (JD[i] - JD[0]) / timescale,
                               50 + 25 + error[i] * 1000 + (yy-250) * (mag[i] - Minmagvalue) / magscale,
                               text=i + 1)


window = tk.Canvas(width=xx - 153, height=yy - 150, bg="light grey")  # yy*0.9-80
frame2 = tk.Frame(master=root, width=150, height=yy - 146, bg="grey")  # yy*0.9-76
frame3 = tk.Frame(master=root, width=xx - 149, height=83, bg="grey")  # yy*0.1
frame4 = tk.Frame(master=root, width=150, height=83, bg="grey")  # y*0.1

window.grid(row=0, column=0, sticky=S)
frame2.grid(row=0, column=1, sticky=S)
frame3.grid(row=1, column=0, sticky=E)
frame4.grid(row=1, column=1, sticky=W)

open_button = ttk.Button(master=frame2, text='Open a File', command=select_file, width=15)
open_button.place(x=24, y=10)


fitentry1 = tk.Entry(master=frame2, justify=CENTER, width=5)
fitentry1.place(x=26, y=300)

fitentry2 = tk.Entry(master=frame2, justify=CENTER, width=5)
fitentry2.place(x=86, y=300)

Gaussian = IntVar()
Lorentzian = IntVar()

checkboxGauss = tk.Checkbutton(master=frame2, text=' Gaussian',
                               variable=Gaussian, onvalue=1, offvalue=0, bg="grey")
checkboxGauss.place(x=27, y=330)
checkboxLorentz = tk.Checkbutton(master=frame2, text=' Lorentzian',
                                 variable=Lorentzian, onvalue=1, offvalue=0, bg="grey")
checkboxLorentz.place(x=27, y=350)


def fitprocessing():
    fstart = int(fitentry1.get())    # getting user starting and ending point
    fend = int(fitentry2.get())        # of fitting
    for i in range(fstart - 1, fend):                   # creating lists of chosen data
        x.append(JD[i])
        y.append(mag[i])

    if Gaussian.get() == 1:          # fitting and drawing Gaussian model
        sd = (JD[fend] - JD[fstart]) / 4
        g_init = models.Gaussian1D(amplitude=magscale, mean=x[len(x) // 2], stddev=sd)
        fit_g = fitting.LevMarLSQFitter()
        fitted_g = fit_g(g_init, x, y)
        for i in range(0, len(x)):
            window.create_rectangle(100 + (xx - 290) * (x[i] - JD[0]) / timescale,
                                    20 + (yy-250) * (fitted_g(x[i]) - Minmagvalue) / magscale,  # drawing
                                    104 + (xx - 290) * (x[i] - JD[0]) / timescale,
                                    24 + (yy-250) * (fitted_g(x[i]) - Minmagvalue) / magscale,  # graph
                                    fill='blue', outline='blue')

    if Lorentzian.get() == 1:        # fitting and drawing Lorentzian model
        locmin = Maxmagvalue
        index = 0
        for i in range(0, len(y)):
            if y[i] < locmin:
                locmin = y[i]
                index = i
        l_init = models.Lorentz1D(amplitude=magscale, x_0=x[index], fwhm=(JD[fend - 1] - JD[fstart - 1]) / 2)
        fit_l = fitting.LevMarLSQFitter()
        fitted_l = fit_l(l_init, x, y)
        for i in range(0, len(x)):
            window.create_rectangle(100 + (xx - 290) * (x[i] - JD[0]) / timescale,
                                    20 + (yy-250) * (fitted_l(x[i]) - Minmagvalue) / magscale,  # drawing
                                    104 + (xx - 290) * (x[i] - JD[0]) / timescale,
                                    24 + (yy-250) * (fitted_l(x[i]) - Minmagvalue) / magscale,  # graph
                                    fill='brown', outline='brown')


fit_button = ttk.Button(master=frame2, text='Fit Curve', command=fitprocessing, width=14)
fit_button.place(x=26, y=380)

tintlabel = tk.Label(master=frame2, text='Time Interval', bg="grey")
tintlabel.place(x=35, y=420)

tintentry1 = tk.Entry(master=frame2, justify=CENTER, width=5)
tintentry1.place(x=26, y=450)

tintentry2 = tk.Entry(master=frame2, justify=CENTER, width=5)
tintentry2.place(x=86, y=450)

tint = ""


def timeinterval():
    tint = round(JD[int(tintentry2.get())-1] - JD[int(tintentry1.get())-1], 7)
    tintoutput = tk.Label(master=frame2, text=str(tint)+ " d", font="Times 10 bold", bg="light grey", justify=CENTER, width=14)
    tintoutput.place(x=22, y=511)


tint_button = ttk.Button(master=frame2, text='Compute', command=timeinterval, width=15)
tint_button.place(x=24, y=480)

tintblacklabel = tk.Label(master=frame2, text=str(tint), bg="black", bd=3, width=14)
tintblacklabel.place(x=21, y=510)

tintoutput = tk.Label(master=frame2, text=str(tint), bg="light grey", width=14)
tintoutput.place(x=22, y=511)


def clearwindow():
    window.delete("all")


clear_button = ttk.Button(master=frame2, text='Clear All', command=clearwindow, width=15)
clear_button.place(x=24, y=50)

root.mainloop()
