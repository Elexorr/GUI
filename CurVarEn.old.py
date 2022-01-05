import sys
import tkinter as tk
from astropy.modeling import models, fitting
from astropy.time import Time

print("CurVarEn ver. 0.03\nDrawing and reviewing variable stars observations")
if len(sys.argv) == 1:  # checking argument presence
    name = input("Enter file name:\n>> ")               # asking for file name to open
else:
    name = sys.argv[1]                                  # reading file name to open

f = open(name)                                          # opening chosen file and reading...
lines = f.readlines()                                   # ...its content line by line
print("Read succesfull. Lightcurve depicted.")

root = tk.Tk()  # creating tkinter environment
root.title("CurVarEn")  #

window = tk.Canvas(width=1280, height=720)  # creating tkinter window
window.pack()

window.create_rectangle(80, 0, 1300, 640)           #            |^^^^^^^^^^^^^^^1200
window.create_text(20, 5, text='mag')               # drawing    |
window.create_text(15, 655, text='JD')              # axes    640|

JDstr = []      # julian date list / strings
magstr = []     # mag list / strings
errstr = []     # error list / strings
JD = []         # julian date list / floats
mag = []        # mag list / floats
error = []      # error list / floats
x = []
y = []

def separatestringvalues():
    global JDay
    for i in range(2, len(lines)):              # extraxting string data from source file
        if i == 2:
            JDay = str(lines[i][0:7])           # checking julian day
        if str(lines[i][16:18]) != '99':        # filtering invalid data
            JDstr.append(lines[i][0:15])        # julian dates
            magstr.append(lines[i][16:24])      # mags
            errstr.append(lines[i][25:32])      # error

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

##  print(JD[i], mag[i], error[i], "<", Minmagvalue, Maxmagvalue, ">", magscale, timescale)

def drawcurve():                # drawing axes, labels and curves
    window.create_line(75, 22 + 600 * (Minmagvalue - Minmagvalue) / magscale,
                       86, 22 + 600 * (Minmagvalue - Minmagvalue) / magscale)
    window.create_text(50, 22 + 600 * (Minmagvalue - Minmagvalue) / magscale, text=Minmagvalue)
    window.create_line(75, 22 + 600 * (Maxmagvalue - Minmagvalue) / magscale,
                       86, 22 + 600 * (Maxmagvalue - Minmagvalue) / magscale)
    window.create_text(50, 22 + 600 * (Maxmagvalue - Minmagvalue) / magscale, text=Maxmagvalue)
    window.create_text(50, 655, text=JDay + "+")

    Jtime = Time(JDstr[0], format='jd')
    ISOtime = Jtime.iso
    window.create_text(38, 670, text=ISOtime[0:10])
    window.create_text(102 + 1140 * (JD[0] - JD[0]) / timescale, 670, text=ISOtime[11:23])

    window.create_line(102 + 1140 * (JD[0] - JD[0]) / timescale, 635,
                       102 + 1140 * (JD[0] - JD[0]) / timescale, 646)
    window.create_text(102 + 1140 * (JD[0] - JD[0]) / timescale, 655, text=JD[0])

    window.create_line(102 + 1140 * (JD[len(JD) - 1] - JD[0]) / timescale, 635,
                       102 + 1140 * (JD[len(JD) - 1] - JD[0]) / timescale, 646)
    window.create_text(102 + 1140 * (JD[len(JD) - 1] - JD[0]) / timescale, 655,
                       text=JD[len(JD) - 1])

    Jtime = Time(JDstr[len(JDstr) - 1], format='jd')
    ISOtime = Jtime.iso
    window.create_text(102 + 1140 * (JD[len(JD) - 1] - JD[0]) / timescale, 670, text=ISOtime[11:23])

    for i in range(0, len(JD)):
        window.create_line(102 + 1140 * (JD[i] - JD[0]) / timescale,        # drawing error bar
                           20 - error[i] * 1000 + 600 * (mag[i] - Minmagvalue) / magscale,
                           102 + 1140 * (JD[i] - JD[0]) / timescale,
                           25 + error[i] * 1000 + 600 * (mag[i] - Minmagvalue) / magscale,
                           fill='red')
        window.create_rectangle(100 + 1140 * (JD[i] - JD[0]) / timescale,   # drawing lightucrve
                                20 + 600 * (mag[i] - Minmagvalue) / magscale,
                                104 + 1140 * (JD[i] - JD[0]) / timescale,
                                24 + 600 * (mag[i] - Minmagvalue) / magscale,
                                fill='red', outline='red')
        if i % 10 == 0:                                                     # drawing point numbers
            window.create_line(102 + 1140 * (JD[i] - JD[0]) / timescale,
                               5 + 25 + error[i] * 1000 + 600 * (mag[i] - Minmagvalue) / magscale,
                               102 + 1140 * (JD[i] - JD[0]) / timescale,
                               40 + 25 + error[i] * 1000 + 600 * (mag[i] - Minmagvalue) / magscale,
                               fill='pink')
            window.create_text(102 + 1140 * (JD[i] - JD[0]) / timescale,
                               50 + 25 + error[i] * 1000 + 600 * (mag[i] - Minmagvalue) / magscale,
                               text=i + 1)
    window.update()

def fitprocessing():
    fstart = int(input("Enter starting point\n>> "))    # getting user starting and ending point
    fend = int(input("Enter ending point\n>> "))        # of fitting
    for i in range(fstart - 1, fend):                   # creating lists of chosen data
        x.append(JD[i])
        y.append(mag[i])

    modelchoice = input("Enter fitting model:\ng) Gaussian\nl) Lorentzian\nb) both\n>> ")

    if modelchoice == 'g' or modelchoice == 'b':    # fitting and drawing Gaussian model
        SD = (JD[fend] - JD[fstart]) / 4
        g_init = models.Gaussian1D(amplitude=magscale, mean=x[len(x) // 2], stddev=SD)
        fit_g = fitting.LevMarLSQFitter()
        fitted_g = fit_g(g_init, x, y)
        for i in range(0, len(x)):
            window.create_rectangle(100 + 1140 * (x[i] - JD[0]) / timescale,
                                    20 + 600 * (fitted_g(x[i]) - Minmagvalue) / magscale,  # drawing
                                    104 + 1140 * (x[i] - JD[0]) / timescale,
                                    24 + 600 * (fitted_g(x[i]) - Minmagvalue) / magscale,  # graph
                                    fill='blue', outline='blue')

    if modelchoice == 'l' or modelchoice == 'b':    # fitting and drawing Lorentzian model
        locmin = Maxmagvalue
        for i in range(0, len(y)):
            if y[i] < locmin:
                locmin = y[i]
                index = i
        l_init = models.Lorentz1D(amplitude=magscale, x_0=x[index], fwhm=(JD[fend - 1] - JD[fstart - 1]) / 2)
        fit_l = fitting.LevMarLSQFitter()
        fitted_l = fit_l(l_init, x, y)
        for i in range(0, len(x)):
            window.create_rectangle(100 + 1140 * (x[i] - JD[0]) / timescale,
                                    20 + 600 * (fitted_l(x[i]) - Minmagvalue) / magscale,  # drawing
                                    104 + 1140 * (x[i] - JD[0]) / timescale,
                                    24 + 600 * (fitted_l(x[i]) - Minmagvalue) / magscale,  # graph
                                    fill='brown', outline='brown')

separatestringvalues()
separatenumericalvalues()
xyscale()
drawcurve()
fitprocessing()
window.mainloop()
f.close()
print("Close window to exit")