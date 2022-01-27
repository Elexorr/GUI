import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
from astropy.modeling import models, fitting
from astropy.time import Time
import numpy as np

import os
from io import BytesIO
import rawpy
from PIL import ImageTk, Image

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
fopened = []


def select_file():
    if fopened != []:
        clearwindow()
    filetypes = (('text files', '*.txt'), ('All files', '*.*'))
    filename = fd.askopenfilename(title='Open a file',
                                  initialdir='/', filetypes=filetypes)
    global f
    global lines
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
    fopened.append(x)
    showinfo(title='Selected File', message=filename)


def select_rawfile():
    if fopened != []:
        clearwindow()
    filetypes = (('All files', '*.*'), ('RAW files', '*.CR2'))
    raw_filename = fd.askopenfilename(title='Open a file', initialdir='/', filetypes=filetypes)
    global rawselected
    rawselected = raw_filename
    print(raw_filename)
    filename, _ = os.path.splitext(raw_filename)
    with rawpy.imread(raw_filename) as raw:
        try:
            thumb = raw.extract_thumb()
        except rawpy.LibRawNoThumbnailError:
            print('no thumbnail found')
            showinfo(title='No Thumbnail Found', message=raw_filename)

        else:
            if thumb.format in [rawpy.ThumbFormat.JPEG, rawpy.ThumbFormat.BITMAP]:
                if thumb.format is rawpy.ThumbFormat.JPEG:
                    thumb_filename = filename + '_thumb.jpg'
                    with open(thumb_filename, 'wb') as f:
                        f.write(thumb.data)
                    thumb_rgb = Image.open(BytesIO(thumb.data))
                else:
                    thumb_filename = filename + '_thumb.tiff'
                    thumb_rgb = Image.fromarray(thumb.data)
                    thumb_rgb.save(filename, 'tiff')

            print(thumb_filename)
            snimok = Image.open(thumb_filename)
            global thumbnailx
            global thumbnaily
            global ratio

            # ratio = round(raw.sizes.width/raw.sizes.height, 3)
            ratio = round(raw.sizes.width/raw.sizes.height, 3)
            thumbnaily = yy - 150
            thumbnailx = int(ratio * thumbnaily)

            resized = snimok.resize((thumbnailx - 6, thumbnaily - 4))   # additional subtraction -6/-4
            # for correct display purposes
            img = ImageTk.PhotoImage(resized)
            window.create_image(xx - 151 - thumbnailx/2, thumbnaily/2 + 2, image=img)  #anchor=SW

            window.create_text(10, 20, text='RAW Type:', anchor=tk.W)
            # raw type (flat or stack, e.g., Foveon sensor)
            window.create_text(150, 20, text=str(raw.raw_type), anchor=tk.W)
            window.create_text(10, 40, text='Number of Colors:', anchor=tk.W)
            # number of different color components, e.g., 3 for common RGB Bayer sensors
            # with two green identical green sensors
            window.create_text(150, 40, text=str(raw.num_colors), anchor=tk.W)
            window.create_text(10, 60, text=f'Color Description:', anchor=tk.W)
            # describes the various color components
            window.create_text(150, 60, text=str(raw.color_desc), anchor=tk.W)
            if str(raw.color_desc)=="b'RGBG'" and str(raw.raw_pattern.tolist())=='[[0, 1], [3, 2]]':
                rgbgshift = xx - 151 - thumbnailx - 45
                window.create_rectangle(rgbgshift,10,
                                        rgbgshift+20,30, fill='red', outline='')
                window.create_text(rgbgshift + 10, 20, text='0')
                window.create_rectangle(rgbgshift+20,10,
                                        rgbgshift+40,30, fill='green', outline='')
                window.create_text(rgbgshift + 30, 20, text='1')
                window.create_rectangle(rgbgshift,30,
                                        rgbgshift+20,50, fill='green', outline='')
                window.create_text(rgbgshift + 10, 40, text='3')
                window.create_rectangle(rgbgshift+20,30,
                                        rgbgshift+40,50, fill='blue', outline='')
                window.create_text(rgbgshift + 30, 40, text='2')

            window.create_text(10, 80, text=f'RAW Pattern:', anchor=tk.W)
            # decribes the pattern of the Bayer sensor
            window.create_text(150, 80, text=str(raw.raw_pattern.tolist()), anchor=tk.W) #
            window.create_text(10, 100, text=f'Black Levels:', anchor=tk.W)
            # black level correction
            window.create_text(150, 100, text=str(raw.black_level_per_channel), anchor=tk.W)
            window.create_text(10, 120, text=f'White Level:', anchor=tk.W)
            # camera white level
            window.create_text(150, 120, text=str(raw.white_level), anchor=tk.W)
            # window.create_text(20, 140,
            # text=f'Color Matrix:                 {raw.color_matrix.tolist()}', anchor=tk.W)
            # camera specific color matrix, usually obtained from a list in rawpy (not from the raw file)
            # window.create_text(20, 160,
            # text=f'XYZ to RGB Conversion Matrix: {raw.rgb_xyz_matrix.tolist()}', anchor=tk.W)
            # camera specific XYZ to camara RGB conversion matrix
            # window.create_text(20, 180,
            # text=f'Camera White Balance:    {raw.camera_whitebalance}', anchor=tk.W)
            # the picture's white balance as determined by the camera
            # window.create_text(20, 200,
            # text=f'Daylight White Balance:  {raw.daylight_whitebalance}', anchor=tk.W)
            # the camera's daylight white balance
    window.mainloop()


def selectmultipleraws():
    filetypes = (('All files', '*.*'), ('RAW files', '*.CR2'))
    raw_filenames = fd.askopenfilenames(title='Open multiple files', initialdir='/', filetypes=filetypes)
    print(raw_filenames)


def adumaxmin():
    print(rawselected)
    path = rawselected
    rawfile = rawpy.imread(path)
    print(rawfile.sizes)
    maxvalue = np.amax(rawfile.raw_image_visible)
    indexmax = np.where(rawfile.raw_image_visible == maxvalue)
    minvalue = np.amin(rawfile.raw_image_visible)
    indexmin = np.where(rawfile.raw_image_visible == minvalue)

    window.create_text(10, 160, text=f'Max. Pixel Value:', anchor=tk.W)  # camera white level
    window.create_text(150, 160, text=maxvalue, anchor=tk.W)
    window.create_text(10, 180, text=f'Min. Pixel Value:', anchor=tk.W)  # camera white level
    window.create_text(150, 180, text=minvalue, anchor=tk.W)

    xshift = xx - 151 - thumbnailx + 1  # additional + 1 for correct display purposes
    xfactor = thumbnailx/rawfile.sizes.width
    yfactor = thumbnaily/rawfile.sizes.height

    for i in range (0, len(indexmax[1])):
            xxx = int(xfactor*indexmax[1][i])
            yyy = int(yfactor*indexmax[0][i])

            window.create_line(xxx - 10 + xshift, yyy - 10 + 2, xxx + 10 + xshift, yyy - 10 + 2, fill='yellow')
            window.create_line(xxx + 10 + xshift, yyy - 10 + 2, xxx + 10 + xshift, yyy + 10 + 2, fill='yellow')
            window.create_line(xxx + 10 + xshift, yyy + 10 + 2, xxx - 10 + xshift, yyy + 10 + 2, fill='yellow')
            window.create_line(xxx - 10 + xshift, yyy + 10 + 2, xxx - 10 + xshift, yyy - 10 + 2, fill='yellow')


    for i in range(0, len(indexmin[1])):
            xxx = int(xfactor * indexmin[1][i])
            yyy = int(yfactor * indexmin[0][i])

            window.create_line(xxx - 10 + xshift, yyy - 10 + 2, xxx + 10 + xshift, yyy - 10 + 2, fill='brown')
            window.create_line(xxx + 10 + xshift, yyy - 10 + 2, xxx + 10 + xshift, yyy + 10 + 2, fill='brown')
            window.create_line(xxx + 10 + xshift, yyy + 10 + 2, xxx - 10 + xshift, yyy + 10 + 2, fill='brown')
            window.create_line(xxx - 10 + xshift, yyy + 10 + 2, xxx - 10 + xshift, yyy - 10 + 2, fill='brown')
    # print(indexmax)
    # print(indexmin)


def adufromlimit():
    print(rawselected)
    path = rawselected
    rawfile = rawpy.imread(path)
    print(rawfile.sizes)
    fromlimit = int(adulimitentry1.get())    # getting user starting and ending point
    maxvalue = np.amax(rawfile.raw_image_visible)
    minvalue = np.amin(rawfile.raw_image_visible)

    indexfrom = np.where(rawfile.raw_image_visible > fromlimit)

    xshift = xx - 151 - thumbnailx + 1  # additional + 1 for correct display purposes
    xfactor = thumbnailx/rawfile.sizes.width
    yfactor = thumbnaily/rawfile.sizes.height

    if fromlimit <= maxvalue and fromlimit >= minvalue:
        for i in range (0, len(indexfrom[1])):
                xxx = int(xfactor*indexfrom[1][i])
                yyy = int(yfactor*indexfrom[0][i])

                window.create_line(xxx - 10 + xshift, yyy - 10 + 2, xxx + 10 + xshift, yyy - 10 + 2, fill='red')
                window.create_line(xxx + 10 + xshift, yyy - 10 + 2, xxx + 10 + xshift, yyy + 10 + 2, fill='red')
                window.create_line(xxx + 10 + xshift, yyy + 10 + 2, xxx - 10 + xshift, yyy + 10 + 2, fill='red')
                window.create_line(xxx - 10 + xshift, yyy + 10 + 2, xxx - 10 + xshift, yyy - 10 + 2, fill='red')
    else:
        showinfo(title='Error', message='Invalid limit set')
    # print(indexmax)
    # print(indexmin)


def aduuptolimit():
    print(rawselected)
    path = rawselected
    rawfile = rawpy.imread(path)
    print(rawfile.sizes)
    uptolimit = int(adulimitentry2.get())        # of fitting
    maxvalue = np.amax(rawfile.raw_image_visible)
    minvalue = np.amin(rawfile.raw_image_visible)

    indexupto = np.where(rawfile.raw_image_visible < uptolimit)

    xshift = xx - 151 - thumbnailx + 1  # additional + 1 for correct display purposes
    xfactor = thumbnailx/rawfile.sizes.width
    yfactor = thumbnaily/rawfile.sizes.height

    if uptolimit >= minvalue and uptolimit <= maxvalue:
        for i in range(0, len(indexupto[1])):
                xxx = int(xfactor * indexupto[1][i])
                yyy = int(yfactor * indexupto[0][i])

                window.create_line(xxx - 10 + xshift, yyy - 10 + 2, xxx + 10 + xshift, yyy - 10 + 2, fill='grey')
                window.create_line(xxx + 10 + xshift, yyy - 10 + 2, xxx + 10 + xshift, yyy + 10 + 2, fill='grey')
                window.create_line(xxx + 10 + xshift, yyy + 10 + 2, xxx - 10 + xshift, yyy + 10 + 2, fill='grey')
                window.create_line(xxx - 10 + xshift, yyy + 10 + 2, xxx - 10 + xshift, yyy - 10 + 2, fill='grey')
    else:
        showinfo(title='Error', message='Invalid limit set')
        # print(indexmax)
        # print(indexmin)


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

openraw_button = ttk.Button(master=frame3, text='Open RAW File', command=select_rawfile, width=15)
openraw_button.place(x=24, y=10)

openmultiraw_button = ttk.Button(master=frame3, text='Open Multiple RAW', command=selectmultipleraws, width=18)
openmultiraw_button.place(x=390, y=10)

rawmaxmin_button = ttk.Button(master=frame3, text='Max./Min. ADU', command=adumaxmin, width=15)
rawmaxmin_button.place(x=146, y=10)

fitentry1 = tk.Entry(master=frame2, justify=CENTER, width=5)
fitentry1.place(x=26, y=300)

fitentry2 = tk.Entry(master=frame2, justify=CENTER, width=5)
fitentry2.place(x=86, y=300)

adulimitlabel = tk.Label(master=frame3, text='Show pixels', bg="grey")
adulimitlabel.place(x=285, y=0)

aduminbutton = ttk.Button(master=frame3, text='From:', command=adufromlimit, width=8)
aduminbutton.place(x=260, y=20)

adumaxbutton = ttk.Button(master=frame3, text='Up to:', command=aduuptolimit, width=8)
adumaxbutton.place(x=260, y=50)

adulimitentry1 = tk.Entry(master=frame3, justify=CENTER, width=8)
adulimitentry1.place(x=325, y=23)

adulimitentry2 = tk.Entry(master=frame3, justify=CENTER, width=8)
adulimitentry2.place(x=325, y=53)

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

        window.create_line(102 + (xx - 290) * (fitted_g.mean - JD[0]) / timescale, yy-210-200,
                           102 + (xx - 290) * (fitted_g.mean - JD[0]) / timescale, yy-210+201)

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
    x.clear()
    y.clear()


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
    global tintoutput
    tintoutput = tk.Label(master=frame2, text=str(tint) + " d", font="Times 10 bold",
                          bg="light grey", justify=CENTER, width=14)
    tintoutput.place(x=22, y=511)


tint_button = ttk.Button(master=frame2, text='Compute', command=timeinterval, width=15)
tint_button.place(x=24, y=480)

tintblacklabel = tk.Label(master=frame2, text=str(tint), bg="black", bd=3, width=14)
tintblacklabel.place(x=21, y=510)

tintoutput = tk.Label(master=frame2, text=str(tint), bg="light grey", width=14)
tintoutput.place(x=22, y=511)


def clearwindow():
    fitentry1.delete(0, 'end')
    fitentry2.delete(0, 'end')
    tintentry1.delete(0, 'end')
    tintentry2.delete(0, 'end')
    checkboxGauss.deselect()
    checkboxLorentz.deselect()
    window.delete("all")
    tintoutput.destroy()
    lines.clear()
    JDstr.clear()
    magstr.clear()
    errstr.clear()
    JD.clear()
    mag.clear()
    error.clear()
    Maxmagvalue = 0
    Minmagvalue = 0
    magscale = 0
    timescale = 0
    fopened.clear()
    f.close()


clear_button = ttk.Button(master=frame2, text='Clear All', command=clearwindow, width=15)
clear_button.place(x=24, y=50)

root.mainloop()
