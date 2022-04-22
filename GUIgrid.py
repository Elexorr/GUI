import tkinter as tk
from tkinter import *
from tkinter import ttk
import exifread
# import PyExifTool
import exiftool
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
from astropy.modeling import models, fitting
# from astropy.modeling.models import Sine1D
from astropy.time import Time
from datetime import date, datetime
import numpy as np
from fractions import Fraction
# from scipy.optimize import curve_fit
# from matplotlib import pyplot as plt

import os
from io import BytesIO
import rawpy
from PIL import ImageTk, Image

root = tk.Tk()
root.title("LeLi Tool")
# root.attributes('-fullscreen', True)
root.state('zoomed')
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
# harx = []
# hary = []
linearity = [[],[]]
sensortemp = [[],[],[]]
phase = [[],[],[]]
fopened = []
rawopen = []
mrawopen = []
fitcounter = []

protocol = open("protocol.txt", "a")

vcompdefault = ''
tcdefault = ''
bvcompdefault = ''
bvvardefault = ''

file_exists = os.path.exists('tcconfig.cfg')
if file_exists == True:
    tcsettings = open('tcconfig.cfg', 'r')
    tcvalues = tcsettings.readlines()
    vcompdefault = tcvalues[0][0:len(tcvalues[0])-1]
    tcdefault = tcvalues[1][0:len(tcvalues[1])-1]
    bvcompdefault = tcvalues[2][0:len(tcvalues[2])-1]
    bvvardefault = tcvalues[3][0:len(tcvalues[3])-1]
    tcsettings.close()


def select_file():
    if fopened != []:
        clearwindow()
    filetypes = (('Text Files', '*.txt'), ('All Files', '*.*'))
    global filename
    filename = fd.askopenfilename(title='Open a File',
                                  initialdir='/', filetypes=filetypes)
    if filename != '':
        global f
        global lines
        f = open(filename)
        lines = f.readlines()
        if lines[3][15] !=' ':
            showinfo(title='Open a File', message='Not a Valid Lighturve File ' + filename)
        else:
            global JDay
            for i in range(2, len(lines)):              # extracting string data from source file
                if i == 2:
                    JDay = str(lines[i][0:7])           # checking julian day
                if str(lines[i][16:18]) != '99':        # filtering invalid data
                    JDstr.append(lines[i][0:15])        # julian dates
                    if lines[i][16] == '-':
                        magstr.append(lines[i][16:24])  # mags
                        errstr.append(lines[i][25:33])  # error
                    else:
                        magstr.append(lines[i][16:23])      # mags
                        errstr.append(lines[i][24:32])      # error
            separatenumericalvalues()
            xyscale()
            drawcurve()
            fopened.append(x)
            global curvetype
            curvetype = 1
            protocol = open("protocol.txt", "a")
            protocol.write('Light curve selected: ' + filename + '\n')
            protocol.close()
            T.insert(END, '\n' + 'Light curve selected: ' + filename)
            T.see(END)
            # showinfo(title='Open a File', message= 'File Selected: ' + filename)
            # print(JDstr)
            # print(magstr)
            # print(errstr)


def select_phasefile():
    if fopened != []:
        clearwindow()
    filetypes = (('Text Files', '*.txt'), ('All Files', '*.*'))
    filename = fd.askopenfilename(title='Open Phase Curve',
                                  initialdir='/', filetypes=filetypes)
    if filename != '':
        global f
        global lines
        f = open(filename)
        lines = f.readlines()
        if lines[1][1] == '.' or lines[1][2] == '.':
            # global JDay
            for i in range(0, len(lines)):  # extracting string data from source file
                # if i == 2:
                #     JDay = str(lines[i][0:7])           # checking julian day
                # if str(lines[i][16:18]) != '99':        # filtering invalid data
                if lines[i][0] == '-':
                    JDstr.append(lines[i][0:9])  # julian dates
                    magstr.append(lines[i][10:18])  # mags
                    errstr.append(lines[i][19:27])  # error
                else:
                    JDstr.append(lines[i][0:8])  # julian dates
                    magstr.append(lines[i][9:17])  # mags
                    errstr.append(lines[i][18:26])  # error
            separatephasevalues()
            xyphasescale()
            drawphasecurve()
            # for i in range(0, len(JDstr)):
            #     print(JDstr[i], magstr[i], errstr[i])
            fopened.append(x)
            global curvetype
            curvetype = 2
            if Inverted.get() == 1:
                protocol = open("protocol.txt", "a")
                protocol.write('Inverted phase curve selected: ' + filename + '\n')
                protocol.close()
                T.insert(END, '\n' + 'Inverted phase curve selected: ' + filename)
                T.see(END)
            else:
                protocol = open("protocol.txt", "a")
                protocol.write('Phase curve selected: ' + filename + '\n')
                protocol.close()
                T.insert(END, '\n' + 'Phase curve selected: ' + filename)
                T.see(END)
            # showinfo(title='Open a File', message='File Selected: ' + filename)
        else:
            showinfo(title='Open a File', message='Not a Valid Phase Curve File ' + filename)

window = tk.Canvas(width=xx - 153, height=yy - 150, bg="light grey")  # yy*0.9-80
frame2 = tk.Frame(master=root, width=150, height=yy - 146, bg="grey")  # yy*0.9-76
frame3 = tk.Frame(master=root, width=xx - 149, height=93, bg="grey")  # yy*0.1
frame4 = tk.Frame(master=root, width=150, height=93, bg="grey")  # y*0.1

window.grid(row=0, column=0, sticky=S)
frame2.grid(row=0, column=1, sticky=S)
frame3.grid(row=1, column=0, sticky=E)
frame4.grid(row=1, column=1, sticky=W)

pixelrlabel = tk.Label(master=frame3, text='Row', bg="grey")
pixelrlabel.place(x=280, y=3)

pixelclabel = tk.Label(master=frame3, text='Col.', bg="grey")
pixelclabel.place(x=328, y=3)

# entryText1 = IntVar()
# entryText2 = IntVar()

rdefault = IntVar()
cdefault = IntVar()

#
#
pixelrentry = tk.Spinbox(master=frame3, justify=CENTER, from_=0, to=10000, textvariable=rdefault,
                         increment=1, width=5)
pixelrentry.place(x=273, y=21)
pixelcentry = tk.Spinbox(master=frame3, justify=CENTER, from_=0, to=10000, textvariable=cdefault,
                         increment=1, width=5)
pixelcentry.place(x=321, y=21)


def select_rawfile():
    if fopened != []:
        clearwindow()
    # filetypes = (('All files', '*.*'), ('RAW files', '*.CR2'))
    raw_filename = fd.askopenfilename(title='Open a file', initialdir='/', filetypes=[('RAW files', '*.CRW *.CR2 *CR3 *.NEF *.ARW')])
    window.delete("all")
    global rawselected
    rawselected = raw_filename
    print(raw_filename)
    rawopen.append('1')
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
            print(raw.sizes)
            snimok = Image.open(thumb_filename)
            global thumbnailx
            global thumbnaily
            global ratio

            # ratio = round(raw.sizes.width/raw.sizes.height, 3)
            ratio = round(raw.sizes.width/raw.sizes.height, 3)
            thumbnaily = yy - 150
            thumbnailx = int(ratio * thumbnaily)

            resized = snimok.resize((thumbnailx - 2, thumbnaily - 1))   # additional subtraction -6/-4
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
            if str(raw.color_desc)=="b'RGBG'":
                if str(raw.raw_pattern.tolist())=='[[0, 1], [3, 2]]':
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
                if str(raw.raw_pattern.tolist()) == '[[3, 2], [0, 1]]':
                    rgbgshift = xx - 151 - thumbnailx - 45
                    window.create_rectangle(rgbgshift,10,
                                            rgbgshift+20,30, fill='green', outline='')
                    window.create_text(rgbgshift + 10, 20, text='3')
                    window.create_rectangle(rgbgshift+20,10,
                                            rgbgshift+40,30, fill='blue', outline='')
                    window.create_text(rgbgshift + 30, 20, text='2')
                    window.create_rectangle(rgbgshift,30,
                                            rgbgshift+20,50, fill='red', outline='')
                    window.create_text(rgbgshift + 10, 40, text='0')
                    window.create_rectangle(rgbgshift+20,30,
                                            rgbgshift+40,50, fill='green', outline='')
                    window.create_text(rgbgshift + 30, 40, text='1')

            window.create_text(10, 80, text=f'RAW Pattern:', anchor=tk.W)
            # describes the pattern of the Bayer sensor
            window.create_text(150, 80, text=str(raw.raw_pattern.tolist()), anchor=tk.W) #
            window.create_text(10, 100, text=f'Black Levels:', anchor=tk.W)
            # black level correction
            window.create_text(150, 100, text=str(raw.black_level_per_channel), anchor=tk.W)
            window.create_text(10, 120, text=f'White Level:', anchor=tk.W)
            # camera white level
            window.create_text(150, 120, text=str(raw.white_level), anchor=tk.W)
            # window.create_text(20, 140, text=f'Color Matrix:                 {raw.color_matrix.tolist()}', anchor=tk.W)
            # camera specific color matrix, usually obtained from a list in rawpy (not from the raw file)
            window.create_text(10,140, text='Visible area (in pixels):', anchor=tk.W)
            window.create_text(150,140, text= str(raw.sizes.height)+' x ' + str(raw.sizes.width), anchor=tk.W)
            window.create_text(10, 160, text='Coordinates Range:', anchor=tk.W)
            window.create_text(150, 160, text='0-' + str(raw.sizes.height-1) + ', ' + '0-' + str(raw.sizes.width-1), anchor=tk.W)
            window.create_text(10,180, text='Center Coordinates:', anchor=tk.W)
            window.create_text(150,180, text= str(raw.sizes.height//2-1)+' x '+str(raw.sizes.width//2-1), anchor=tk.W)

            # window.create_text(20, 160,
            # text=f'XYZ to RGB Conversion Matrix: {raw.rgb_xyz_matrix.tolist()}', anchor=tk.W)
            # camera specific XYZ to camera RGB conversion matrix
            # window.create_text(20, 180,
            # text=f'Camera White Balance:    {raw.camera_whitebalance}', anchor=tk.W)
            # the picture's white balance as determined by the camera
            # window.create_text(20, 200,
            # text=f'Daylight White Balance:  {raw.daylight_whitebalance}', anchor=tk.W)
            # the camera's daylight white balance=
            # rdef=raw.sizes.height//2-1
            # cdef=raw.sizes.width//2-1
            rdefault.set(raw.sizes.height//2-1)
            cdefault.set(raw.sizes.width//2-1)
            # pixelrentry = tk.Spinbox(master=frame3, justify=CENTER, from_= 0, to=raw.sizes.height, textvariable=str(rdef), increment=1, width=5)
            # pixelrentry.place(x=273, y=21)
            #
            # pixelcentry = tk.Spinbox(master=frame3, justify=CENTER, from_= 0, to=raw.sizes.width, textvariable=str(cdef), increment=1, width=5)
            # pixelcentry.place(x=321, y=21)

            # pixelrentry.insert(0, raw.sizes.height//2-1)
            # pixelcentry.insert(0, raw.sizes.width//2-1)
            # entryText1.set(raw.sizes.height//2-1)
            # entryText2.set(raw.sizes.width//2-1)

            protocol = open("protocol.txt", "a")
            protocol.write('RAW file selected: ' + raw_filename + '\n')
            protocol.close()
            T.insert(END, '\n' + 'RAW file selected: ' + raw_filename)
            T.see(END)
    window.mainloop()


def selectmultipleraws():
    filetypes = ('RAW files', '*.CRW *.CR2 *CR3 *.NEF *.ARW')
    global raw_filenames
    # raw_filenames = fd.askopenfilenames(title='Open multiple files', initialdir='/', filetypes=filetypes)
    raw_filenames = fd.askopenfilenames(title='Open Multiple RAW', initialdir='/', filetypes=[('RAW files', '*.CRW *.CR2 *CR3 *.NEF *.ARW')])
    print(raw_filenames)
    if len(raw_filenames) > 1:
        mrawopen.append('1')
        # showinfo(title='Open Multiple RAW', message= str(len(raw_filenames)) + ' RAW Files Opened')
        protocol = open("protocol.txt", "a")
        protocol.write('Multiple RAW: ' + str(len(raw_filenames)) + ' RAW Files Opened' + '\n')
        protocol.close()
        T.insert(END, '\n' + 'Multiple RAW: ' + str(len(raw_filenames)) + ' RAW Files Opened')
        T.see(END)


RBsample = IntVar()
checkboxRBsample = tk.Checkbutton(master=frame3, text=' R/B sample',
                               variable=RBsample, onvalue=1, offvalue=0, bg="grey")
checkboxRBsample.place(x=405, y=45)


def checklinearity():
    print(mrawopen)
    if mrawopen == []:
        showinfo(title='Error', message='No Multiple RAW to Check')
    elif pixelrentry.get() == '' or pixelcentry.get() == '':
        showinfo(title='Error', message='No Pixel Coordinates to Check')
    else:
        window.delete("all")
        for j in range (0,len(raw_filenames)):
            f = open(raw_filenames[j], 'rb')
            tags = exifread.process_file(f)
            f.close()
            data = list(tags.items())
            an_array = np.array(data)
            pixr = int(pixelrentry.get())
            pixc = int(pixelcentry.get())

            samplefield = []

            with rawpy.imread(raw_filenames[j]) as raw:
                if RBsample.get() == 1:
                    samplefield.append(raw.raw_image_visible[pixr - 4][pixc - 4])
                    samplefield.append(raw.raw_image_visible[pixr - 4][pixc - 2])
                    samplefield.append(raw.raw_image_visible[pixr - 4][pixc])
                    samplefield.append(raw.raw_image_visible[pixr - 4][pixc + 2])
                    samplefield.append(raw.raw_image_visible[pixr - 4][pixc + 4])
                    samplefield.append(raw.raw_image_visible[pixr - 2][pixc - 4])
                    samplefield.append(raw.raw_image_visible[pixr - 2][pixc - 2])
                    samplefield.append(raw.raw_image_visible[pixr - 2][pixc])
                    samplefield.append(raw.raw_image_visible[pixr - 2][pixc + 2])
                    samplefield.append(raw.raw_image_visible[pixr][pixc - 4])
                    samplefield.append(raw.raw_image_visible[pixr][pixc - 2])
                    samplefield.append(raw.raw_image_visible[pixr][pixc])
                    samplefield.append(raw.raw_image_visible[pixr][pixc + 2])
                    samplefield.append(raw.raw_image_visible[pixr][pixc + 4])
                    samplefield.append(raw.raw_image_visible[pixr + 2][pixc - 4])
                    samplefield.append(raw.raw_image_visible[pixr + 2][pixc - 2])
                    samplefield.append(raw.raw_image_visible[pixr + 2][pixc])
                    samplefield.append(raw.raw_image_visible[pixr + 2][pixc + 2])
                    samplefield.append(raw.raw_image_visible[pixr + 4][pixc + 4])
                    samplefield.append(raw.raw_image_visible[pixr + 4][pixc - 4])
                    samplefield.append(raw.raw_image_visible[pixr + 4][pixc - 2])
                    samplefield.append(raw.raw_image_visible[pixr + 4][pixc])
                    samplefield.append(raw.raw_image_visible[pixr + 4][pixc + 2])
                    samplefield.append(raw.raw_image_visible[pixr + 4][pixc + 4])
                else:
                    samplefield.append(raw.raw_image_visible[pixr - 3][pixc - 3])
                    samplefield.append(raw.raw_image_visible[pixr - 3][pixc - 1])
                    samplefield.append(raw.raw_image_visible[pixr - 3][pixc + 1])
                    samplefield.append(raw.raw_image_visible[pixr - 3][pixc + 3])
                    samplefield.append(raw.raw_image_visible[pixr - 2][pixc - 2])
                    samplefield.append(raw.raw_image_visible[pixr - 2][pixc])
                    samplefield.append(raw.raw_image_visible[pixr - 2][pixc + 2])
                    samplefield.append(raw.raw_image_visible[pixr - 1][pixc - 3])
                    samplefield.append(raw.raw_image_visible[pixr - 1][pixc - 1])
                    samplefield.append(raw.raw_image_visible[pixr - 1][pixc + 1])
                    samplefield.append(raw.raw_image_visible[pixr - 1][pixc + 3])
                    samplefield.append(raw.raw_image_visible[pixr][pixc - 2])
                    samplefield.append(raw.raw_image_visible[pixr][pixc])
                    samplefield.append(raw.raw_image_visible[pixr][pixc + 2])
                    samplefield.append(raw.raw_image_visible[pixr + 1][pixc - 3])
                    samplefield.append(raw.raw_image_visible[pixr + 1][pixc - 1])
                    samplefield.append(raw.raw_image_visible[pixr + 1][pixc + 1])
                    samplefield.append(raw.raw_image_visible[pixr + 1][pixc + 3])
                    samplefield.append(raw.raw_image_visible[pixr + 2][pixc - 2])
                    samplefield.append(raw.raw_image_visible[pixr + 2][pixc])
                    samplefield.append(raw.raw_image_visible[pixr + 2][pixc + 2])
                    samplefield.append(raw.raw_image_visible[pixr + 3][pixc - 3])
                    samplefield.append(raw.raw_image_visible[pixr + 3][pixc - 1])
                    samplefield.append(raw.raw_image_visible[pixr + 3][pixc + 1])
                    samplefield.append(raw.raw_image_visible[pixr + 3][pixc + 3])
            for i in range(0, len(an_array) - 1):
                if an_array[i][0] == 'EXIF ExposureTime':
                    # print(an_array[i][1])
                    time = str(an_array[i][1])
                    # print(float(sum(Fraction(time) for time in time.split())))
                    timetime = float(sum(Fraction(time) for time in time.split()))
                    timetime = round(timetime, 4)

            # print(timetime, np.mean(samplefield))
            # linearity.append[timetime][np.mean(samplefield)]
            linearity[0].append(timetime)
            linearity[1].append(np.mean(samplefield))
            samplefield.clear()
            # raw.close
        # print(linearity)
        filelinearity = open("linearity.txt", "w")
        for l in range (0, len(linearity[0])):
            filelinearity.write(str(linearity[0][l])+' '+str(linearity[1][l])+'\n')
        filelinearity.close()
        maxtime = np.amax(linearity[0])
        maxadu = np.amax(linearity[1])
        minadu = np.amin(linearity[1])
        aduscale = (yy-210)/(minadu+maxadu)
        timescale = (xx-150)/(maxtime*1.05)
        # print(maxtime, maxadu, minadu)
        window.create_rectangle(80, 0, xx - 150, yy - 210)
        for i in range (0,len(linearity[0])-1):
            timeshift=int(float(linearity[0][i])*timescale)
            adushift=int(float(linearity[1][i])*aduscale)
            # print(timeshift,adushift)
            window.create_rectangle(80+timeshift-2, yy-210-adushift-2,
                                    80+timeshift+2, yy-210-adushift+2, fill='blue')


def checktemperature():
    if mrawopen == []:
        showinfo(title='Error', message='No Multiple RAW to Check')
    else:
        files = [raw_filenames]
        with exiftool.ExifToolHelper() as et:
            for j in range (0,len(raw_filenames)):
                metadata = et.get_metadata(raw_filenames[j])
                metastring = str(metadata)
                tempposition = metastring.index("CameraTemperature")
                timeposition = metastring.index("DateTimeOriginal")
                exptime = str(metastring[timeposition + 20:timeposition + 39])
                # exphh = int(metastring[timeposition + 31:timeposition + 33])
                # expmm = int(metastring[timeposition + 34:timeposition + 36])
                # expss = int(metastring[timeposition + 37:timeposition + 39])
                isotime = Time(str(metastring[timeposition+20:timeposition+24])+'-'
                            +str(metastring[timeposition+25:timeposition+27])+'-'
                            +str(metastring[timeposition+28:timeposition+30])+' '
                            +str(metastring[timeposition+31:timeposition+33])+':'
                            +str(metastring[timeposition+34:timeposition+36])+':'
                            +str(metastring[timeposition+37:timeposition+39])+'.000', format='iso')
                # jtime = Time(JDstr[0], format='jd')
                jdtime = round(isotime.jd,6)
                # print(jdtime)
                if metastring[tempposition + 21] == ',':
                    temperature = metastring[tempposition + 19:tempposition + 21]
                else:
                    temperature = metastring[tempposition + 19:tempposition + 22]
                # temperature = int(metastring[tempposition + 19:tempposition + 22])
                sensortemp[0].append(jdtime)
                sensortemp[1].append(exptime)
                sensortemp[2].append(int(temperature))
        filesensortemp = open("sensortemp.txt", "w")
        for l in range (0, len(sensortemp[0])):
            filesensortemp.write(str(sensortemp[0][l])+' '
                                 +str(sensortemp[1][l])+' '
                                 +str(sensortemp[2][l])+'\n')

        Maxtempvalue = np.amax(sensortemp[2])
        Mintempvalue = np.amin(sensortemp[2])
        temperaturescale = Maxtempvalue - Mintempvalue

        tscale = round(sensortemp[0][len(sensortemp[0]) - 1] - sensortemp[0][0], 5)
        print(temperaturescale,tscale)

        window.create_rectangle(80, 0, xx - 150, yy - 210)  # |^^^^^^^^^^^^^^^
        window.create_text(20, 10, text='Temp')  # |
        window.create_text(20, yy - 195, text='Time')  # |

        window.create_line(75, 22 + (yy - 250) * (Mintempvalue - Mintempvalue) / temperaturescale,
                           86, 22 + (yy - 250) * (Mintempvalue - Mintempvalue) / temperaturescale)
        window.create_text(50, 22 + (yy - 250) * (Mintempvalue - Mintempvalue) / temperaturescale, text=Maxtempvalue)
        window.create_line(75, 22 + (yy - 250) * (Maxtempvalue - Mintempvalue) / temperaturescale,
                           86, 22 + (yy - 250) * (Maxtempvalue - Mintempvalue) / temperaturescale)
        window.create_text(50, 22 + (yy - 250) * (Maxtempvalue - Mintempvalue) / temperaturescale, text=Mintempvalue)
        # window.create_text(50, yy - 195, text=JDay + "+")
        # jtime = Time(JDstr[0], format='jd')
        # isotime = jtime.iso
        # window.create_text(38, yy - 180, text=isotime[0:10])
        # window.create_text(102 + (xx - 290) * (JD[0] - JD[0]) / timescale, yy - 180, text=isotime[11:23])

        window.create_line(102 + (xx - 290) * (sensortemp[0][0] - sensortemp[0][0]) / tscale, yy - 210 - 5,
                           102 + (xx - 290) * (sensortemp[0][0] - sensortemp[0][0]) / tscale, yy - 210 + 6)
        window.create_text(102 + (xx - 290) * (sensortemp[0][0] - sensortemp[0][0]) / tscale, yy - 195, text=str(sensortemp[1][0]))

        window.create_line(102 + (xx - 290) * (sensortemp[0][len(sensortemp[0])-1] - sensortemp[0][0]) / tscale, yy - 210 - 5,
                           102 + (xx - 290) * (sensortemp[0][len(sensortemp[0])-1] - sensortemp[0][0]) / tscale, yy - 210 + 6)
        window.create_text(102 + (xx - 290) * (sensortemp[0][len(sensortemp[0])-1] - sensortemp[0][0]) / tscale, yy - 195,
                           text=str(sensortemp[1][len(sensortemp[0])-1]))

        # jtime = Time(JDstr[len(JDstr) - 1], format='jd')
        # isotime = jtime.iso
        # window.create_text(102 + (xx - 290) * (JD[len(JD) - 1] - JD[0]) / timescale, yy - 180, text=isotime[11:23])

        for i in range(0, len(sensortemp[0])):
            # window.create_rectangle(100 + (xx - 290) * (sensortemp[0][i] - sensortemp[0][0]) / tscale,  # drawing lightucrve
            #                         20 + (yy - 250) * (sensortemp[2][i] - Mintempvalue) / temperaturescale,
            #                         104 + (xx - 290) * (sensortemp[0][i] - sensortemp[0][0]) / tscale,
            #                         24 + (yy - 250) * (sensortemp[2][i] - Mintempvalue) / temperaturescale,
            #                         fill='red', outline='red')
            window.create_rectangle(100 + (xx - 290) * (sensortemp[0][i] - sensortemp[0][0]) / tscale,  # drawing lightucrve
                                    yy - 230 - (yy - 250) * (sensortemp[2][i] - Mintempvalue) / temperaturescale,
                                    104 + (xx - 290) * (sensortemp[0][i] - sensortemp[0][0]) / tscale,
                                    yy - 226 - (yy - 250) * (sensortemp[2][i] - Mintempvalue) / temperaturescale,
                                    fill='red', outline='red')

            # if i % 10 == 0:  # drawing point numbers
            #     window.create_line(102 + (xx - 290) * (JD[i] - JD[0]) / timescale,
            #                        5 + 25 + error[i] * 1000 + (yy - 250) * (mag[i] - Minmagvalue) / magscale,
            #                        102 + (xx - 290) * (JD[i] - JD[0]) / timescale,
            #                        40 + 25 + error[i] * 1000 + (yy - 250) * (mag[i] - Minmagvalue) / magscale,
            #                        fill='grey')
            #     window.create_text(102 + (xx - 290) * (JD[i] - JD[0]) / timescale,
            #                        50 + 25 + error[i] * 1000 + (yy - 250) * (mag[i] - Minmagvalue) / magscale,
            #                        text=i + 1)


def adumaxmin():
    if rawopen == []:
        showinfo(title='Error', message='No RAW File to Check')
    else:
        print(rawselected)
        path = rawselected
        rawfile = rawpy.imread(path)
        print(rawfile.sizes)
        maxvalue = np.amax(rawfile.raw_image_visible)
        indexmax = np.where(rawfile.raw_image_visible == maxvalue)
        minvalue = np.amin(rawfile.raw_image_visible)
        indexmin = np.where(rawfile.raw_image_visible == minvalue)

        window.create_text(10, 200, text=f'Max. Pixel Value:', anchor=tk.W)  # camera white level
        window.create_text(150, 200, text=maxvalue, anchor=tk.W)
        window.create_text(10, 220, text=f'Min. Pixel Value:', anchor=tk.W)  # camera white level
        window.create_text(150, 220, text=minvalue, anchor=tk.W)

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
                window.create_text(xxx + xshift, yyy - 20 + 2,
                                   text = str(rawfile.raw_image_visible[indexmax[0][i]][indexmax[1][i]]), fill='white' )
                window.create_text(xxx + xshift - 25, yyy + 2,
                                   text=str(indexmax[0][i]), fill='yellow')
                window.create_text(xxx + xshift, yyy + 20 + 2,
                                   text=str(indexmax[1][i]), fill='yellow')

        for i in range(0, len(indexmin[1])):
                xxx = int(xfactor * indexmin[1][i])
                yyy = int(yfactor * indexmin[0][i])

                window.create_line(xxx - 10 + xshift, yyy - 10 + 2, xxx + 10 + xshift, yyy - 10 + 2, fill='brown')
                window.create_line(xxx + 10 + xshift, yyy - 10 + 2, xxx + 10 + xshift, yyy + 10 + 2, fill='brown')
                window.create_line(xxx + 10 + xshift, yyy + 10 + 2, xxx - 10 + xshift, yyy + 10 + 2, fill='brown')
                window.create_line(xxx - 10 + xshift, yyy + 10 + 2, xxx - 10 + xshift, yyy - 10 + 2, fill='brown')
                window.create_text(xxx + xshift, yyy - 20 + 2,
                                   text=str(rawfile.raw_image_visible[indexmin[0][i]][indexmin[1][i]]), fill='white')
                window.create_text(xxx + xshift - 25, yyy + 2,
                                   text=str(indexmin[0][i]), fill='brown')
                window.create_text(xxx + xshift, yyy + 20 + 2,
                                   text=str(indexmin[1][i]), fill='brown')
        protocol = open("protocol.txt", "a")
        protocol.write('Max. ADU: ' + str(maxvalue) + ' / Min. ADU: ' + str(minvalue) + '\n')
        protocol.close()
        T.insert(END, '\n' + 'Max. ADU: ' + str(maxvalue) + ' / Min. ADU: ' + str(minvalue))
        T.see(END)
        # print(indexmax)
        # print(indexmin)


def adufromlimit():
    if rawopen == []:
        showinfo(title='Error', message='No RAW File to Check')
    elif adulimitentry1.get() == '':
        showinfo(title='Error', message='No Limit Set')
    else:
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

                    window.create_line(xxx - 10 + xshift, yyy - 10 + 2, xxx + 10 + xshift, yyy - 10 + 2, fill='red', tags = "square2")
                    window.create_line(xxx + 10 + xshift, yyy - 10 + 2, xxx + 10 + xshift, yyy + 10 + 2, fill='red', tags = "square2")
                    window.create_line(xxx + 10 + xshift, yyy + 10 + 2, xxx - 10 + xshift, yyy + 10 + 2, fill='red', tags = "square2")
                    window.create_line(xxx - 10 + xshift, yyy + 10 + 2, xxx - 10 + xshift, yyy - 10 + 2, fill='red', tags = "square2")

                    window.create_text(xxx + xshift, yyy - 20 + 2,
                                       text=str(rawfile.raw_image_visible[indexfrom[0][i]][indexfrom[1][i]]),
                                       fill='red', tags = "square2")
                    window.create_text(xxx + xshift - 25, yyy + 2,
                                       text=str(indexfrom[0][i]), fill='red', tags = "square2")
                    window.create_text(xxx + xshift, yyy + 20 + 2,
                                       text=str(indexfrom[1][i]), fill='red', tags = "square2")
        else:
            showinfo(title='Error', message='Invalid limit set')
        # print(indexmax)
        # print(indexmin)


def aduuptolimit():
    if rawopen == []:
        showinfo(title='Error', message='No RAW File to Check')
    elif adulimitentry2.get() == '':
        showinfo(title='Error', message='No Limit Set')
    else:
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

                    window.create_line(xxx - 10 + xshift, yyy - 10 + 2, xxx + 10 + xshift, yyy - 10 + 2, fill='grey', tags = "square2")
                    window.create_line(xxx + 10 + xshift, yyy - 10 + 2, xxx + 10 + xshift, yyy + 10 + 2, fill='grey', tags = "square2")
                    window.create_line(xxx + 10 + xshift, yyy + 10 + 2, xxx - 10 + xshift, yyy + 10 + 2, fill='grey', tags = "square2")
                    window.create_line(xxx - 10 + xshift, yyy + 10 + 2, xxx - 10 + xshift, yyy - 10 + 2, fill='grey', tags = "square2")

                    window.create_text(xxx + xshift, yyy - 20 + 2,
                                       text=str(rawfile.raw_image_visible[indexupto[0][i]][indexupto[1][i]]),
                                       fill='grey', tags = "square2")
                    window.create_text(xxx + xshift - 25, yyy + 2,
                                       text=str(indexupto[0][i]), fill='grey', tags = "square2")
                    window.create_text(xxx + xshift, yyy + 20 + 2,
                                       text=str(indexupto[1][i]), fill='grey', tags = "square2")
        else:
            showinfo(title='Error', message='Invalid Limit Set')
            # print(indexmax)
            # print(indexmin)


def clearsquares():
    window.delete("square2")


def pixelprop():
    global pixcolor
    window.delete("square")
    if pixelrentry.get() == '' or pixelcentry.get() == '':
        showinfo(title='Error', message='No Pixel Coordinates to Check')
    if rawopen == []:
        showinfo(title='Error', message='No RAW File to Check')
    else:
        path = rawselected
        rawfile = rawpy.imread(path)
        pixr=int(pixelrentry.get())
        pixc=int(pixelcentry.get())
        value=rawfile.raw_value_visible(pixr,pixc)
        pixcolorindex=rawfile.raw_colors_visible[pixr][pixc]
        if str(rawfile.color_desc) == "b'RGBG'":
            if str(rawfile.raw_pattern.tolist()) == '[[0, 1], [3, 2]]':
                if pixcolorindex == 0:
                    pixcolor = 'red'
                    pixproplabel = tk.Label(master=frame3, text=str(pixcolorindex)+' / '+str(value),
                                            fg='yellow', bg="red", width=11)
                    pixproplabel.place(x=411, y=20)
                if pixcolorindex == 1:
                    pixcolor = 'green'
                    pixproplabel = tk.Label(master=frame3, text=str(pixcolorindex)+' / '+str(value),
                                            fg='yellow', bg="green", width=11)
                    pixproplabel.place(x=411, y=20)
                if pixcolorindex == 2:
                    pixcolor = 'blue'
                    pixproplabel = tk.Label(master=frame3, text=str(pixcolorindex)+' / '+str(value),
                                            fg='yellow', bg="blue", width=11)
                    pixproplabel.place(x=411, y=20)
                if pixcolorindex == 3:
                    pixcolor = 'green'
                    pixproplabel = tk.Label(master=frame3, text=str(pixcolorindex)+' / '+str(value),
                                            fg='yellow', bg="green", width=11)
                    pixproplabel.place(x=411, y=20)
            if str(rawfile.raw_pattern.tolist()) == '[[3, 2], [0, 1]]':
                if pixcolorindex == 0:
                    pixcolor = 'blue'
                    pixproplabel = tk.Label(master=frame3, text=str(pixcolorindex)+' / '+str(value),
                                            fg='yellow', bg="blue", width=11)
                    pixproplabel.place(x=411, y=20)
                if pixcolorindex == 1:
                    pixcolor = 'green'
                    pixproplabel = tk.Label(master=frame3, text=str(pixcolorindex)+' / '+str(value),
                                            fg='yellow', bg="green", width=11)
                    pixproplabel.place(x=411, y=20)
                if pixcolorindex == 2:
                    pixcolor = 'blue'
                    pixproplabel = tk.Label(master=frame3, text=str(pixcolorindex)+' / '+str(value),
                                            fg='yellow', bg="blue",  width=11)
                    pixproplabel.place(x=411, y=20)
                if pixcolorindex == 3:
                    pixcolor = 'red'
                    pixproplabel = tk.Label(master=frame3, text=str(pixcolorindex)+' / '+str(value),
                                            fg='yellow', bg="red",  width=11)
                    pixproplabel.place(x=411, y=20)
        xshift = xx - 151 - thumbnailx + 1  # additional + 1 for correct display purposes
        xfactor = thumbnailx / rawfile.sizes.width
        yfactor = thumbnaily / rawfile.sizes.height
        xxx = int(xfactor * pixc)
        yyy = int(yfactor * pixr)
        window.create_line(xxx - 10 + xshift, yyy - 10 + 2, xxx + 10 + xshift, yyy - 10 + 2, fill='white', tags = 'square')
        window.create_line(xxx + 10 + xshift, yyy - 10 + 2, xxx + 10 + xshift, yyy + 10 + 2, fill='white', tags = 'square')
        window.create_line(xxx + 10 + xshift, yyy + 10 + 2, xxx - 10 + xshift, yyy + 10 + 2, fill='white', tags = 'square')
        window.create_line(xxx - 10 + xshift, yyy + 10 + 2, xxx - 10 + xshift, yyy - 10 + 2, fill='white', tags = 'square')
        window.create_line(xxx - 7 + xshift, yyy - 7 + 2, xxx + 7 + xshift, yyy - 7 + 2, fill='white', tags = 'square')
        window.create_line(xxx + 7 + xshift, yyy - 7 + 2, xxx + 7 + xshift, yyy + 7 + 2, fill='white', tags = 'square')
        window.create_line(xxx + 7 + xshift, yyy + 7 + 2, xxx - 7 + xshift, yyy + 7 + 2, fill='white', tags = 'square')
        window.create_line(xxx - 7 + xshift, yyy + 7 + 2, xxx - 7 + xshift, yyy - 7 + 2, fill='white', tags = 'square')
        selectsample()


def separatenumericalvalues():
    for i in range(0, len(JDstr)):                          # creating numerical data
        JD.append(round(float(JDstr[i][0:15]) % 1, 7))      # julian dates
        mag.append(round(float(magstr[i][0:8]), 5))         # mags
        error.append(round(float(errstr[i][0:8]), 5))       # error


def separatephasevalues():
    global npphase
    for i in range(0, len(JDstr)):                          # creating numerical data
        if JDstr[i][0] == '-':
            JD.append(0.5+(-1)*round(float(JDstr[i][1:9]) % 1, 7))    #phase
            phase[0].append(0.5+(-1)*round(float(JDstr[i][1:9]) % 1, 7))
        else:
            JD.append(0.5+round(float(JDstr[i][0:8]) % 1, 7))      #phase
            phase[0].append(0.5+round(float(JDstr[i][1:9]) % 1, 7))
        if Inverted.get() == 1:
            mag.append(5-round(2 + (float(magstr[i][0:8])), 5))  # adds factor 5 to make all values positive
            phase[1].append(5-round(2 + (float(magstr[i][0:8])), 5))  # adds factor 5 to make all values positive
        else:
            # mag.append(round(2+(float(magstr[i][0:8])), 5))           # adds factor 5 to make all values positive
            # phase[1].append(round(2+(float(magstr[i][0:8])), 5))      # adds factor 5 to make all values positive
            mag.append(round(float(magstr[i][0:8]), 5))         # mags
            phase[1].append(round(float(magstr[i][0:8]), 5))
        error.append(round(float(errstr[i][0:8]), 5))       # error
        phase[2].append(round(float(errstr[i][0:8]), 5))
    npphase = np.array(phase)   #creating np.array from standard array for fitting and drawing purposes
    npphase = npphase[:, npphase[0, :].argsort()]  #sorting np.array by phase


def xyscale():              # creating variables for scaling purposes
    global Maxmagvalue
    global Minmagvalue
    global magscale
    global timescale
    Maxmagvalue = np.max(mag, axis = 0)
    Minmagvalue = np.min(mag, axis = 0)
    # print(Maxmagvalue, Minmagvalue)
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


def xyphasescale():              # creating variables for scaling purposes
    global Maxmagvalue
    global Minmagvalue
    global magscale
    global timescale
    Maxmagvalue = round(np.max(npphase[1], axis = 0), 5)
    Minmagvalue = round(np.min(npphase[1], axis = 0), 5)
    magscale = round(Maxmagvalue - Minmagvalue, 5)
    timescale = 1


def drawphasecurve():                # drawing axes, labels and curves
    window.create_rectangle(80, 0, xx-150, yy-210)     # |^^^^^^^^^^^^^^^
    window.create_text(60, 6, text='mag')               # |
    window.create_text(60, yy-196, text='Phase:')           # |

    window.create_line(75, 22 + (yy-250) * (Minmagvalue - Minmagvalue) / magscale,
                       86, 22 + (yy-250) * (Minmagvalue - Minmagvalue) / magscale)
    if Inverted.get() == 1:
        window.create_text(50, 22 + (yy-250) * (Minmagvalue - Minmagvalue) / magscale, text=round(5-Minmagvalue-2, 5))
    else:
        window.create_text(50, 22 + (yy - 250) * (Minmagvalue - Minmagvalue) / magscale, text=round(Minmagvalue, 5))
    window.create_line(75, 22 + (yy-250) * (Maxmagvalue - Minmagvalue) / magscale,
                       86, 22 + (yy-250) * (Maxmagvalue - Minmagvalue) / magscale)
    if Inverted.get() == 1:
        window.create_text(50, 22 + (yy-250) * (Maxmagvalue - Minmagvalue) / magscale, text=round(5-Maxmagvalue-2, 5))

    else:
        window.create_text(50, 22 + (yy - 250) * (Maxmagvalue - Minmagvalue) / magscale, text=round(Maxmagvalue, 5))

    window.create_line(102 + (xx - 290) * (npphase[0][0] - npphase[0][0]) / timescale, yy-210-5,
                       102 + (xx - 290) * (npphase[0][0] - npphase[0][0]) / timescale, yy-210+6)
    window.create_text(102 + (xx - 290) * (npphase[0][0] - npphase[0][0]) / timescale, yy-195,
                       text=-0.5)  # text=round(npphase[0][0]-1000000.5, 1))

    window.create_line(102 + (xx - 290) * 1 / timescale, yy-210-5,
                       102 + (xx - 290) * 1 / timescale, yy-210+6)
    window.create_text(102 + (xx - 290) * 1 / timescale, yy-195,
                       text=0.5)

    for i in range(0, len(npphase[0])):
        window.create_line(102 + (xx - 290) * (npphase[0][i] - npphase[0][0]) / timescale,        # drawing error bar
                           20 - npphase[2][i] * 1000 + (yy-250) * (npphase[1][i] - Minmagvalue) / magscale,
                           102 + (xx - 290) * (npphase[0][i] - npphase[0][0]) / timescale,
                           25 + npphase[2][i] * 1000 + (yy-250) * (npphase[1][i] - Minmagvalue) / magscale,
                           fill='red')
        window.create_rectangle(100 + (xx - 290) * (npphase[0][i] - npphase[0][0]) / timescale,   # drawing lightucrve
                                20 + (yy-250) * (npphase[1][i] - Minmagvalue) / magscale,
                                104 + (xx - 290) * (npphase[0][i] - npphase[0][0]) / timescale,
                                24 + (yy-250) * (npphase[1][i] - Minmagvalue) / magscale,
                                fill='red', outline='red')

        if i % 10 == 0:                                                     # drawing point numbers
            window.create_line(102 + (xx - 290) * (npphase[0][i] - npphase[0][0]) / timescale,
                               5 + 25 + npphase[2][i] * 1000 + (yy-250) * (npphase[1][i] - Minmagvalue) / magscale,
                               102 + (xx - 290) * (npphase[0][i] - npphase[0][0]) / timescale,
                               40 + 25 + npphase[2][i] * 1000 + (yy-250) * (npphase[1][i] - Minmagvalue) / magscale,
                               fill='grey')
            window.create_text(102 + (xx - 290) * (npphase[0][i] - npphase[0][0]) / timescale,
                               50 + 25 + npphase[2][i] * 1000 + (yy-250) * (npphase[1][i] - Minmagvalue) / magscale,
                               text=i + 1)


# window = tk.Canvas(width=xx - 153, height=yy - 150, bg="light grey")  # yy*0.9-80


today = date.today()
d1 = today.strftime("%d/%m/%Y")
now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print("Current Time =", current_time)
T = Text(master=frame3, height = 4, width = 74, bg = 'Light grey', bd = 3, padx=10)
T.place(x=xx - 153 - 594, y=0)
T.insert(END, d1 + ' ' + current_time + ' / LeLi Tool / Open a file to continue...')
protocol = open("protocol.txt", "a")
protocol.write(d1 + ' ' + current_time + '\n')
protocol.close()


open_button = ttk.Button(master=frame2, text='Open Light Curve', command=select_file, width=17)
open_button.place(x=18, y=10)

openphase_button = ttk.Button(master=frame2, text='Open Phase Curve', command=select_phasefile, width=17)
openphase_button.place(x=18, y=50)

openraw_button = ttk.Button(master=frame3, text='Open RAW File', command=select_rawfile, width=15)
openraw_button.place(x=24, y=10)

openmultiraw_button = ttk.Button(master=frame3, text='Open Multiple RAW', command=selectmultipleraws, width=18)
openmultiraw_button.place(x=510, y=10)

checklinearity_button = ttk.Button(master=frame3, text='Check Linearity', command=checklinearity, width=18)
checklinearity_button.place(x=510, y=40)

checktemperature_button = ttk.Button(master=frame3, text='Sensor Temp. (°C)', command=checktemperature, width=18)
checktemperature_button.place(x=648, y=40)

rawmaxmin_button = ttk.Button(master=frame3, text='Max./Min. ADU', command=adumaxmin, width=15)
rawmaxmin_button.place(x=24, y=40)

tintlabel = tk.Label(master=frame2, text='Fit Start        Fit End', bg="grey")
tintlabel.place(x=19, y=99)

fitentry1 = tk.Entry(master=frame2, justify=CENTER, width=5)
fitentry1.place(x=26, y=119)

fitentry2 = tk.Entry(master=frame2, justify=CENTER, width=5)
fitentry2.place(x=87, y=119)

def recommendline():
    hi = int(fitentry1.get()) - 1
    if curvetype == 1:
        window.create_line(60, 22 + (yy - 250) * (mag[hi] - Minmagvalue) / magscale,
                           xx-90, 22 + (yy - 250) * (mag[hi] - Minmagvalue) / magscale, dash=(3,2), fill='black')
    if curvetype == 2:
        window.create_line(60, 22 + (yy - 250) * (npphase[1][hi] - Minmagvalue) / magscale,
                           xx-90, 22 + (yy - 250) * (npphase[1][hi] - Minmagvalue) / magscale, dash=(3,2), fill='black')


recommend_button = ttk.Button(master=frame2, text='-', command=recommendline, width=1)
recommend_button.place(x=66, y=117)

adulimitlabel = tk.Label(master=frame3, text='Show Pixels', bg="grey")
adulimitlabel.place(x=165, y=-1)

aduminbutton = ttk.Button(master=frame3, text='From:', command=adufromlimit, width=8)
aduminbutton.place(x=140, y=18)

adumaxbutton = ttk.Button(master=frame3, text='Up to:', command=aduuptolimit, width=8)
adumaxbutton.place(x=140, y=47)

clearsquaresbutton = ttk.Button(master=frame3, text='Clear', command=clearsquares, width=8)
clearsquaresbutton.place(x=274, y=47)

adulimitentry1 = tk.Spinbox(master=frame3, justify=CENTER, width=7)
adulimitentry1.place(x=205, y=21)

adulimitentry2 = tk.Spinbox(master=frame3, justify=CENTER, width=7)
adulimitentry2.place(x=205, y=50)

adulimitlabel = tk.Label(master=frame3, text='Col. Index/ADU', bg="grey")
adulimitlabel.place(x=409, y=-1)

pixelpropbutton = ttk.Button(master=frame3, text='>>', command=pixelprop, width=3)
pixelpropbutton.place(x=375, y=18)

pixpropblacklabel = tk.Label(master=frame3, text='', bg="black", bd=3, width=11)
pixpropblacklabel.place(x=410, y=19)

pixproplabel = tk.Label(master=frame3, text='', bg="light grey", width=11)
pixproplabel.place(x=411, y=20)

Inverted = IntVar()
Gaussian = IntVar()
Lorentzian = IntVar()
Harmonic = IntVar()

checkboxInverted = tk.Checkbutton(master=frame2, text=' Inverted',
                               variable=Inverted, onvalue=1, offvalue=0, bg="grey")
checkboxInverted.place(x=34, y=75)

checkboxGauss = tk.Checkbutton(master=frame2, text=' Gaussian',
                               variable=Gaussian, onvalue=1, offvalue=0, bg="grey")
checkboxGauss.place(x=27, y=142)

checkboxLorentz = tk.Checkbutton(master=frame2, text=' Lorentzian',
                                 variable=Lorentzian, onvalue=1, offvalue=0, bg="grey")
checkboxLorentz.place(x=27, y=162)

# checkboxHarmonic = tk.Checkbutton(master=frame2, text=' Harmonic',
#                                   variable=Harmonic, onvalue=1, offvalue=0, bg="grey")
# checkboxHarmonic.place(x=27, y=180)

min1label = tk.Label(master=frame2, text='T1', bg="grey")
min1label.place(x=5, y=225)

min1tblacklabel = tk.Label(master=frame2, bg="black", bd=3, width=15)
min1tblacklabel.place(x=26, y=224)

min1toutput = tk.Label(master=frame2, text='', bg="light grey", width=15)
min1toutput.place(x=27, y=225)

magmin1label = tk.Label(master=frame2, text='M1', bg="grey")
magmin1label.place(x=3, y=251)

magmin1tblacklabel = tk.Label(master=frame2, bg="black", bd=3, width=15)
magmin1tblacklabel.place(x=26, y=250)

magmin1toutput = tk.Label(master=frame2, text='', bg="light grey", width=15)
magmin1toutput.place(x=27, y=251)

min2label = tk.Label(master=frame2, text='T2', bg="grey")
min2label.place(x=5, y=277)

min2tblacklabel = tk.Label(master=frame2, bg="black", bd=3, width=15)
min2tblacklabel.place(x=26, y=276)

min2toutput = tk.Label(master=frame2, text='', bg="light grey", width=15)
min2toutput.place(x=27, y=277)

magmin2label = tk.Label(master=frame2, text='M2', bg="grey")
magmin2label.place(x=3, y=303)

magmin2tblacklabel = tk.Label(master=frame2, bg="black", bd=3, width=15)
magmin2tblacklabel.place(x=26, y=302)

magmin2toutput = tk.Label(master=frame2, text='', bg="light grey", width=15)
magmin2toutput.place(x=27, y=303)

timediflabel = tk.Label(master=frame2, text='T2-T1', bg="grey")
timediflabel.place(x=7, y=330)

timediftblacklabel = tk.Label(master=frame2, bg="black", bd=3, width=12)
timediftblacklabel.place(x=47, y=328)

timedifoutput = tk.Label(master=frame2, text='', bg="light grey", width=12)
timedifoutput.place(x=48, y=329)

mindiflabel = tk.Label(master=frame2, text='M2-M1', bg="grey")
mindiflabel.place(x=3, y=356)

mindiftblacklabel = tk.Label(master=frame2, bg="black", bd=3, width=12)
mindiftblacklabel.place(x=47, y=354)

mindifoutput = tk.Label(master=frame2, text='', bg="light grey", width=12)
mindifoutput.place(x=48, y=355)

tclabel = tk.Label(master=frame2, text='V-band Transformation', bg="grey")
tclabel.place(x=10, y=495)

VTClabel = tk.Label(master=frame2, text='V(comp)         TC', bg="grey")
VTClabel.place(x=19, y=515)


vcompentry = tk.Entry(master=frame2, justify=CENTER, width=7)
vcompentry.insert(0, vcompdefault)
vcompentry.place(x=21, y=535)

tcentry = tk.Entry(master=frame2, justify=CENTER, width=7)
tcentry.insert(0, tcdefault)
tcentry.place(x=82, y=535)

bvlabel = tk.Label(master=frame2, text='B-V(comp)    B-V(tgt)', bg="grey")
bvlabel.place(x=12, y=555)

bvcompentry = tk.Entry(master=frame2, justify=CENTER, width=7)
bvcompentry.insert(0, bvcompdefault)
bvcompentry.place(x=21, y=575)

bvvarentry = tk.Entry(master=frame2, justify=CENTER, width=7)
bvvarentry.insert(0, bvvardefault)
bvvarentry.place(x=82, y=575)


def transformation():
    if 'curvetype' in globals():
       if curvetype == 1:
            # print('transformation')
            Vcomp = round(float(vcompentry.get()), 3)
            TC = round(float(tcentry.get()), 3)
            BVcomp = round(float(bvcompentry.get()), 3)
            BVvar = round(float(bvvarentry.get()), 3)
            # print(Vcomp,TC, BVcomp, BVvar)
            transformed = open(filename + "-V.txt", "w")
            transformed.write('JD V s1\n')
            transformed.write(lines[1])
            for i in range (0, len(JD)):
                magtransformed = str(round((Vcomp+mag[i]+TC*(BVvar-BVcomp)), 5))
                magtransformed = round((Vcomp+mag[i]+TC*(BVvar-BVcomp)), 5)
                transformed.write(JDstr[i] + ' ' + str(f'{magtransformed:.5f}') + ' ' + errstr[i] + '\n')
                # transformed.write(JDstr[i] + ' ' + str(f'{mag[i]:.5f}') + ' ' + str(f'{magtransformed:.5f}') + ' ' + errstr[i] + '\n')
            transformed.close()
            open('tcconfig.cfg', 'w').close()
            tcsettings = open('tcconfig.cfg', 'w')
            tcsettings.write(str(Vcomp)+'\n')
            tcsettings.write(str(TC)+'\n')
            tcsettings.write(str(BVcomp)+'\n')
            tcsettings.write(str(BVvar)+'\n')
            tcsettings.close()
            protocol = open("protocol.txt", "a")
            protocol.write('Data transformed to V-band with: ' + '\n')
            protocol.write('V(comp) = ' + str(Vcomp) + ' / TC = ' + str(TC) + ' / B-V(comp) = ' + str(BVcomp) + ' / B-V(tgt) =' + str(BVvar) + '\n')
            protocol.write('File saved: ' + filename + "-V.txt" + '\n')
            protocol.close()
            T.insert(END, '\n' + 'Data transformed to V-band with: ')
            T.insert(END, '\n' + 'V(comp) = ' + str(Vcomp) + ' / TC = ' + str(TC) + ' / B-V(comp) = ' + str(BVcomp) + ' / B-V(tgt) = ' + str(BVvar))
            T.insert(END, '\n' + 'File saved: ' + filename + "-V.txt")
            T.see(END)
            showinfo(title='V-band Transformation', message='File Transformed and Saved to: ' + filename + "-V.txt")
       else:
           showinfo(title='V-band Transformation', message='No Valid Curve File Selected')
    else:
        showinfo(title='V-band Transformation', message='No File Selected')


tcbutton = ttk.Button(master=frame2, text='Transform', command=transformation, width=15)
tcbutton.place(x=24, y=600)


def fitprocessing():
    if fopened != []:
        global Tmin1
        global magmin1
        if curvetype == 1:
            fstart = int(fitentry1.get())    # getting user starting and ending point
            fend = int(fitentry2.get())        # of fitting
            protocol = open("protocol.txt", "a")
            if Inverted.get() == 1:
                protocol.write('Curve inverted: Yes \n' + 'Fit start: ' + str(fstart) + ' Fit end: ' + str(fend) + '\n')
                T.insert(END, '\n' + 'Curve inverted: Yes \n' + 'Fit start: ' + str(fstart) + ' / Fit end: ' + str(fend))
                T.see(END)
            else:
                protocol.write('Curve inverted: No \n' + 'Fit start: ' + str(fstart) + ' Fit end: ' + str(fend) + '\n')
                T.insert(END, '\n' + 'Curve inverted: No \n' + 'Fit start: ' + str(fstart) + ' / Fit end: ' + str(fend))
                T.see(END)
            protocol.close()
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

                if fitcounter == []:
                    Tmin1 = round(float(JDay)+fitted_g.mean, 7)
                    magmin1 = round(fitted_g(fitted_g.mean), 5)
                    mintoutput = tk.Label(master=frame2, text=str(Tmin1), bg="light grey", width=15, font="Times 10 bold")
                    mintoutput.place(x=27, y=225)
                    magmin1toutput = tk.Label(master=frame2, text=str(magmin1), bg="light grey", width=15, font="Times 10 bold")
                    magmin1toutput.place(x=27, y=251)
                    protocol = open("protocol.txt", "a")
                    if Inverted.get() == 1:
                        protocol.write('Time Of Maximum 1 (Gaussian):   T(M1) = ' + str(Tmin1) + '\n')
                        protocol.write('Magnitude:                         M1 = ' + str(magmin1) + '\n')
                        T.insert(END, '\n' + 'Time Of Maximum 1 (Gaussian): T(M1) = ' + str(Tmin1) + ' / M1 = ' + str(magmin1))
                        T.see(END)
                    else:
                        protocol.write('Time Of Minimum 1 (Gaussian):   T(M1) = ' + str(Tmin1) + '\n')
                        protocol.write('Magnitude:                         M1 = ' + str(magmin1) + '\n')
                        T.insert(END, '\n' + 'Time Of Minimum 1 (Gaussian): T(M1) = ' + str(Tmin1) + ' / M1 = ' + str(magmin1))
                        T.see(END)
                    protocol.close()
                    fitcounter.append('1')

                else:
                    Tmin2 = round(float(JDay)+fitted_g.mean, 7)
                    magmin2 = round(fitted_g(fitted_g.mean), 5)
                    min2toutput = tk.Label(master=frame2, text=str(Tmin2), bg="light grey", width=15, font="Times 10 bold")
                    min2toutput.place(x=27, y=277)
                    magmin2toutput = tk.Label(master=frame2, text=str(magmin2), bg="light grey", width=15, font="Times 10 bold")
                    magmin2toutput.place(x=27, y=303)
                    timedifoutput = tk.Label(master=frame2, text=str(round((Tmin2-Tmin1), 7)), bg="light grey", width=12, font="Times 10 bold")
                    timedifoutput.place(x=48, y=329)
                    mindifoutput = tk.Label(master=frame2, text=str(round((magmin2-magmin1), 5)), bg="light grey", width=12, font="Times 10 bold")
                    mindifoutput.place(x=48, y=355)
                    protocol = open("protocol.txt", "a")
                    if Inverted.get() == 1:
                        protocol.write('Time Of Maximum 2 (Gaussian):   T(M2) = ' + str(Tmin2) + '\n')
                        protocol.write('Magnitude:                         M2 = ' + str(magmin2) + '\n')
                        protocol.write('Maxima Dev.:            T(M2) - T(M1) = ' + str(round((Tmin2 - Tmin1), 7)) + '\n')
                        protocol.write('Magnitude Dev.:               M2 - M1 = ' + str(round((magmin2-magmin1), 5)) + '\n')
                        T.insert(END, '\n' + 'Time Of Maximum 2 (Gaussian): T(M2) = ' + str(Tmin2) + ' / M2 = ' + str(magmin2))
                        T.insert(END, '\n' + 'Magnitude Dev.: M2 - M1 = ' + str(round((magmin2-magmin1), 5)))
                        T.see(END)
                    else:
                        protocol.write('Time Of Minimum 2 (Gaussian):   T(M2) = ' + str(Tmin1) + '\n')
                        protocol.write('Magnitude:                         M2 = ' + str(magmin2) + '\n')
                        protocol.write('Minima Dev.:            T(M2) - T(M1) = ' + str(round((Tmin2 - Tmin1), 7)) + '\n')
                        protocol.write('Magnitude Dev.:               M2 - M1 = ' + str(round((magmin2 - magmin1), 5)) + '\n')
                        T.insert(END, '\n' + 'Time Of Minimum 2 (Gaussian): T(M2) = ' + str(Tmin2) + ' / M2 = ' + str(magmin2))
                        T.insert(END, '\n' + 'Magnitude Dev.: M2 - M1 = ' + str(round((magmin2-magmin1), 5)))
                        T.see(END)
                    protocol.close()
                    fitcounter.clear()
                # print(magmin1)

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

                window.create_line(102 + (xx - 290) * (fitted_l.x_0 - JD[0]) / timescale, yy-210-200,
                                   102 + (xx - 290) * (fitted_l.x_0 - JD[0]) / timescale, yy-210+201)

                if fitcounter == []:
                    Tmin1 = round(float(JDay)+fitted_l.x_0, 7)
                    magmin1 = round(fitted_l(fitted_l.x_0), 5)
                    mintoutput = tk.Label(master=frame2, text=str(Tmin1), bg="light grey", width=15, font="Times 10 bold")
                    mintoutput.place(x=27, y=225)
                    magmin1toutput = tk.Label(master=frame2, text=str(magmin1), bg="light grey", width=15, font="Times 10 bold")
                    magmin1toutput.place(x=27, y=251)
                    protocol = open("protocol.txt", "a")
                    if Inverted.get() == 1:
                        protocol.write('Time Of Maximum 1 (Lorentzian): T(M1) = ' + str(Tmin1) + '\n')
                        protocol.write('Magnitude:                         M1 = ' + str(magmin1) + '\n')
                        T.insert(END, '\n' + 'Time Of Maximum 1 (Lorentzian): T(M1) = ' + str(Tmin1) + ' / M1 = ' + str(magmin1))
                        T.see(END)
                    else:
                        protocol.write('Time Of Minimum 1 (Lorentzian): T(M1) = ' + str(Tmin1) + '\n')
                        protocol.write('Magnitude:                         M1 = ' + str(magmin1) + '\n')
                        T.insert(END, '\n' + 'Time Of Minimum 1 (Lorentzian): T(M1) = ' + str(Tmin1) + ' / M1 = ' + str(magmin1))
                        T.see(END)
                    protocol.close()
                    fitcounter.append('1')
                else:
                    Tmin2 = round(float(JDay)+fitted_l.x_0, 7)
                    magmin2 = round(fitted_l(fitted_l.x_0), 5)
                    min2toutput = tk.Label(master=frame2, text=str(Tmin2), bg="light grey", width=15, font="Times 10 bold")
                    min2toutput.place(x=27, y=277)
                    magmin2toutput = tk.Label(master=frame2, text=str(magmin2), bg="light grey", width=15, font="Times 10 bold")
                    magmin2toutput.place(x=27, y=303)
                    timedifoutput = tk.Label(master=frame2, text=str(round((Tmin2-Tmin1), 7)), bg="light grey", width=12, font="Times 10 bold")
                    timedifoutput.place(x=48, y=329)
                    mindifoutput = tk.Label(master=frame2, text=str(round((magmin2-magmin1), 5)), bg="light grey", width=12, font="Times 10 bold")
                    mindifoutput.place(x=48, y=355)
                    protocol = open("protocol.txt", "a")
                    if Inverted.get() == 1:
                        protocol.write('Time Of Maximum 2 (Lorentzian): T(M2) = ' + str(Tmin2) + '\n')
                        protocol.write('Magnitude:                         M2 = ' + str(magmin2) + '\n')
                        protocol.write('Maxima Dev.:            T(M2) - T(M1) = ' + str(round((Tmin2 - Tmin1), 7)) + '\n')
                        protocol.write('Magnitude Dev.:               M2 - M1 = ' + str(round((magmin2 - magmin1), 5)) + '\n')
                        T.insert(END, '\n' + 'Time Of Maximum 2 (Lorentzian): T(M2) = ' + str(Tmin2) + ' / M2 = ' + str(magmin2))
                        T.insert(END, '\n' + 'Magnitude Dev.: M2 - M1 = ' + str(round((magmin2-magmin1), 5)))
                        T.see(END)
                    else:
                        protocol.write('Time Of Minimum 2 (Lorentzian): T(M2) = ' + str(Tmin2) + '\n')
                        protocol.write('Magnitude:                         M2 = ' + str(magmin2) + '\n')
                        protocol.write('Minima Dev.:            T(M2) - T(M1) = ' + str(round((Tmin2 - Tmin1), 7)) + '\n')
                        protocol.write('Magnitude Dev.:               M2 - M1 = ' + str(round((magmin2 - magmin1), 5)) + '\n')
                        T.insert(END, '\n' + 'Time Of Minimum 2 (Lorentzian): T(M2) = ' + str(Tmin2) + ' / M2 = ' + str(magmin2))
                        T.insert(END, '\n' + 'Magnitude Dev.: M2 - M1 = ' + str(round((magmin2-magmin1), 5)))
                        T.see(END)
                    protocol.close()
                    fitcounter.clear()


        if curvetype == 2:
            fstart = int(fitentry1.get())    # getting user starting and ending point
            fend = int(fitentry2.get())        # of fitting
            protocol = open("protocol.txt", "a")
            if Inverted.get() == 1:
                protocol.write('Curve inverted: Yes \n' + 'Fit start: ' + str(fstart) + ' Fit end: ' + str(fend) + '\n')
                T.insert(END, '\n' + 'Curve inverted: Yes \n' + 'Fit start: ' + str(fstart) + ' / Fit end: ' + str(fend))
                T.see(END)
            else:
                protocol.write('Curve inverted: No \n' + 'Fit start: ' + str(fstart) + ' Fit end: ' + str(fend) + '\n')
                T.insert(END, '\n' + 'Curve inverted: No \n' + 'Fit start: ' + str(fstart) + ' / Fit end: ' + str(fend))
                T.see(END)
            protocol.close()
            for i in range(fstart - 1, fend-1):                   # creating lists of chosen data
                x.append(npphase[0][i])
                y.append(npphase[1][i])
            if Gaussian.get() == 1:          # fitting and drawing Gaussian model
                sd = (npphase[0][fend] - npphase[0][fstart]) / 4
                g_init = models.Gaussian1D(amplitude=magscale, mean=x[len(x) // 2], stddev=sd)
                fit_g = fitting.LevMarLSQFitter()
                fitted_g = fit_g(g_init, x, y)

                window.create_line(102 + (xx - 290) * (fitted_g.mean - npphase[0][0]) / timescale, yy-210-200,
                                    102 + (xx - 290) * (fitted_g.mean - npphase[0][0]) / timescale, yy-210+201)

                for i in range(0, len(x)):
                    window.create_rectangle(100 + (xx - 290) * (x[i] - npphase[0][0]) / timescale,
                                            20 + (yy-250) * (fitted_g(x[i]) - Minmagvalue) / magscale,  # drawing
                                            104 + (xx - 290) * (x[i] - npphase[0][0]) / timescale,
                                            24 + (yy-250) * (fitted_g(x[i]) - Minmagvalue) / magscale,  # graph
                                            fill='blue', outline='blue')
                if fitcounter == []:
                    Tmin1 = round(((3+fitted_g.mean)-3)-0.5, 7)
                    if Inverted.get() == 1:
                        magmin1 = round(5-fitted_g(fitted_g.mean)-2, 5)
                    else:
                        magmin1 = round(fitted_g(fitted_g.mean), 5)
                    mintoutput = tk.Label(master=frame2, text=str(Tmin1), bg="light grey", width=15, font="Times 10 bold")
                    mintoutput.place(x=27, y=225)
                    magmin1toutput = tk.Label(master=frame2, text=str(magmin1), bg="light grey", width=15, font="Times 10 bold")
                    magmin1toutput.place(x=27, y=251)
                    protocol = open("protocol.txt", "a")
                    if Inverted.get() == 1:
                        protocol.write('Time Of Maximum 1 (Gaussian):   T(M1) = ' + str(Tmin1) + '\n')
                        protocol.write('Magnitude:                         M1 = ' + str(magmin1) + '\n')
                        T.insert(END, '\n' + 'Time Of Maximum 1 (Gaussian): T(M1) = ' + str(Tmin1) + ' / M1 = ' + str(magmin1))
                        T.see(END)
                    else:
                        protocol.write('Time Of Minimum 1 (Gaussian):   T(M1) = ' + str(Tmin1) + '\n')
                        protocol.write('Magnitude:                         M1 = ' + str(magmin1) + '\n')
                        T.insert(END, '\n' + 'Time Of Minimum 1 (Gaussian): T(M1) = ' + str(Tmin1) + ' / M1 = ' + str(magmin1))
                        T.see(END)
                    protocol.close()
                    fitcounter.append('1')
                else:
                    Tmin2 = round(((3+fitted_g.mean)-3)-0.5, 7)
                    if Inverted.get() == 1:
                        magmin2 = round(5-fitted_g(fitted_g.mean)-2, 5)
                    else:
                        magmin2 = round(fitted_g(fitted_g.mean), 5)
                    min2toutput = tk.Label(master=frame2, text=str(Tmin2), bg="light grey", width=15, font="Times 10 bold")
                    min2toutput.place(x=27, y=277)
                    magmin2toutput = tk.Label(master=frame2, text=str(magmin2), bg="light grey", width=15, font="Times 10 bold")
                    magmin2toutput.place(x=27, y=303)
                    timedifoutput = tk.Label(master=frame2, text=str(round((Tmin2-Tmin1), 7)), bg="light grey", width=12, font="Times 10 bold")
                    timedifoutput.place(x=48, y=329)
                    mindifoutput = tk.Label(master=frame2, text=str(round((magmin2-magmin1), 5)), bg="light grey", width=12, font="Times 10 bold")
                    mindifoutput.place(x=48, y=355)
                    protocol = open("protocol.txt", "a")
                    if Inverted.get() == 1:
                        protocol.write('Time Of Maximum 2 (Gaussian):   T(M2) = ' + str(Tmin2) + '\n')
                        protocol.write('Magnitude:                         M2 = ' + str(magmin2) + '\n')
                        protocol.write('Maxima Dev.:            T(M2) - T(M1) = ' + str(round((Tmin2 - Tmin1), 7)) + '\n')
                        protocol.write('Magnitude Dev.:               M2 - M1 = ' + str(round((magmin2-magmin1), 5)) + '\n')
                        T.insert(END, '\n' + 'Time Of Maximum 2 (Gaussian): T(M2) = ' + str(Tmin2) + ' / M2 = ' + str(magmin2))
                        T.insert(END, '\n' + 'Magnitude Dev.: M2 - M1 = ' + str(round((magmin2-magmin1), 5)))
                        T.see(END)
                    else:
                        protocol.write('Time Of Minimum 2 (Gaussian):   T(M2) = ' + str(Tmin1) + '\n')
                        protocol.write('Magnitude:                         M2 = ' + str(magmin2) + '\n')
                        protocol.write('Minima Dev.:            T(M2) - T(M1) = ' + str(round((Tmin2 - Tmin1), 7)) + '\n')
                        protocol.write('Magnitude Dev.:               M2 - M1 = ' + str(round((magmin2 - magmin1), 5)) + '\n')
                        T.insert(END, '\n' + 'Time Of Minimum 2 (Gaussian): T(M2) = ' + str(Tmin2) + ' / M2 = ' + str(magmin2))
                        T.insert(END, '\n' + 'Magnitude Dev.: M2 - M1 = ' + str(round((magmin2-magmin1), 5)))
                        T.see(END)
                    protocol.close()
                    fitcounter.clear()

            if Lorentzian.get() == 1:        # fitting and drawing Lorentzian model
                locmin = Maxmagvalue
                index = 0
                for i in range(0, len(y)):
                    if y[i] < locmin:
                        locmin = y[i]
                        index = i
                l_init = models.Lorentz1D(amplitude=magscale, x_0=x[index], fwhm=(npphase[0][fend - 1] - npphase[0][fstart - 1]) / 2)
                fit_l = fitting.LevMarLSQFitter()
                fitted_l = fit_l(l_init, x, y)
                for i in range(0, len(x)):
                    window.create_rectangle(100 + (xx - 290) * (x[i] - npphase[0][0]) / timescale,
                                            20 + (yy-250) * (fitted_l(x[i]) - Minmagvalue) / magscale,  # drawing
                                            104 + (xx - 290) * (x[i] - npphase[0][0]) / timescale,
                                            24 + (yy-250) * (fitted_l(x[i]) - Minmagvalue) / magscale,  # graph
                                            fill='brown', outline='brown')

                window.create_line(102 + (xx - 290) * (fitted_l.x_0 - npphase[0][0]) / timescale, yy-210-200,
                                    102 + (xx - 290) * (fitted_l.x_0 - npphase[0][0]) / timescale, yy-210+201)

                if fitcounter == []:
                    Tmin1 = round(((3+fitted_l.x_0)-3)-0.5, 7)
                    if Inverted.get() == 1:
                        magmin1 = round(5-fitted_l(fitted_l.x_0)-2, 5)
                    else:
                        magmin1 = round(fitted_l(fitted_l.x_0), 5)
                    mintoutput = tk.Label(master=frame2, text=str(Tmin1), bg="light grey", width=15, font="Times 10 bold")
                    mintoutput.place(x=27, y=225)
                    magmin1toutput = tk.Label(master=frame2, text=str(magmin1), bg="light grey", width=15, font="Times 10 bold")
                    magmin1toutput.place(x=27, y=251)
                    protocol = open("protocol.txt", "a")
                    if Inverted.get() == 1:
                        protocol.write('Time Of Maximum 1 (Lorentzian): T(M1) = ' + str(Tmin1) + '\n')
                        protocol.write('Magnitude:                         M1 = ' + str(magmin1) + '\n')
                        T.insert(END, '\n' + 'Time Of Maximum 1 (Lorentzian): T(M1) = ' + str(Tmin1) + ' / M1 = ' + str(magmin1))
                        T.see(END)
                    else:
                        protocol.write('Time Of Minimum 1 (Lorentzian): T(M1) = ' + str(Tmin1) + '\n')
                        protocol.write('Magnitude:                         M1 = ' + str(magmin1) + '\n')
                        T.insert(END, '\n' + 'Time Of Minimum 1 (Lorentzian): T(M1) = ' + str(Tmin1) + ' / M1 = ' + str(magmin1))
                        T.see(END)
                    protocol.close()
                    fitcounter.append('1')
                else:
                    Tmin2 = round(((3+fitted_l.x_0)-3)-0.5, 7)
                    if Inverted.get() == 1:
                        magmin2 = round(5-fitted_l(fitted_l.x_0)-2, 5)
                    else:
                        magmin2 = round(fitted_l(fitted_l.x_0), 5)
                    min2toutput = tk.Label(master=frame2, text=str(Tmin2), bg="light grey", width=15, font="Times 10 bold")
                    min2toutput.place(x=27, y=277)
                    magmin2toutput = tk.Label(master=frame2, text=str(magmin2), bg="light grey", width=15, font="Times 10 bold")
                    magmin2toutput.place(x=27, y=303)
                    timedifoutput = tk.Label(master=frame2, text=str(round((Tmin2-Tmin1), 7)), bg="light grey", width=12, font="Times 10 bold")
                    timedifoutput.place(x=48, y=329)
                    mindifoutput = tk.Label(master=frame2, text=str(round((magmin2-magmin1), 5)), bg="light grey", width=12, font="Times 10 bold")
                    mindifoutput.place(x=48, y=355)
                    protocol = open("protocol.txt", "a")
                    if Inverted.get() == 1:
                        protocol.write('Time Of Maximum 2 (Lorentzian): T(M2) = ' + str(Tmin2) + '\n')
                        protocol.write('Magnitude:                         M2 = ' + str(magmin2) + '\n')
                        protocol.write('Maxima Dev.:            T(M2) - T(M1) = ' + str(round((Tmin2 - Tmin1), 7)) + '\n')
                        protocol.write('Magnitude Dev.:               M2 - M1 = ' + str(round((magmin2 - magmin1), 5)) + '\n')
                        T.insert(END, '\n' + 'Time Of Maximum 2 (Lorentzian): T(M2) = ' + str(Tmin2) + ' / M2 = ' + str(magmin2))
                        T.insert(END, '\n' + 'Magnitude Dev.: M2 - M1 = ' + str(round((magmin2-magmin1), 5)))
                        T.see(END)
                    else:
                        protocol.write('Time Of Minimum 2 (Lorentzian): T(M2) = ' + str(Tmin2) + '\n')
                        protocol.write('Magnitude:                         M2 = ' + str(magmin2) + '\n')
                        protocol.write('Minima Dev.:            T(M2) - T(M1) = ' + str(round((Tmin2 - Tmin1), 7)) + '\n')
                        protocol.write('Magnitude Dev.:               M2 - M1 = ' + str(round((magmin2 - magmin1), 5)) + '\n')
                        T.insert(END, '\n' + 'Time Of Minimum 2 (Lorentzian): T(M2) = ' + str(Tmin2) + ' / M2 = ' + str(magmin2))
                        T.insert(END, '\n' + 'Magnitude Dev.: M2 - M1 = ' + str(round((magmin2-magmin1), 5)))
                        T.see(END)
                    protocol.close()
                    fitcounter.clear()
            # if Harmonic.get() == 1:        # fitting and drawing Harmonic model
                # print('Harmonic')
                # fstart = int(fitentry1.get())  # getting user starting and ending point
                # fend = int(fitentry2.get())  # of fitting
                # for i in range(fstart - 1, fend):  # creating lists of chosen data
                #     harx.append(npphase[0][i])
                #     hary.append(npphase[1][i])
                # harx = npphase[0][fstart:fend]
                # hary = npphase[1][fstart:fend]
                # amp = (np.max(hary) - np.min(hary))
                # print(amp)
                # s_init = models.Sine1D(amplitude=amp, phase=0.5)
                # fit_s = fitting.LevMarLSQFitter()
                # fitted_s = fit_s(s_init, harx, hary)
                # for i in range(0, len(harx)):
                #     window.create_rectangle(100 + (xx - 290) * (harx[i] - harx[0]) / timescale,
                #                             20 + (yy-250) * (fitted_s(harx[i]) - Minmagvalue) / magscale,  # drawing
                #                             104 + (xx - 290) * (harx[i] - harx[0]) / timescale,
                #                             24 + (yy-250) * (fitted_s(harx[i]) - Minmagvalue) / magscale,  # graph
                #                             fill='blue', outline='blue')
                # print(harx)
        #         def test(harx, K, a1, b1, c1):
        #             return K + a1 * np.sin(b1 * harx + c1)
        #             # return a * np.sin(b * harx)
        #         param, param_cov = curve_fit(test, harx, hary)
        #
        #         print("Sine function coefficients:")
        #         print(param)
        #         print("Covariance of coefficients:")
        #         print(param_cov)
        #
        #         ans = (param[0] * (np.sin(param[1] * harx)))
        #
        #         plt.plot(harx, 1-hary, 'o', color='red', label="data")
        #         plt.plot(harx, ans, '--', color='blue', label="optimized data")
        #         plt.legend()
        #         plt.show()
        # curvetype.clear()
        x.clear()
        y.clear()
    else:
        showinfo(title='Fit Curve', message='No File Selected')


fit_button = ttk.Button(master=frame2, text='Fit Curve', command=fitprocessing, width=14)
fit_button.place(x=26, y=190)

tintlabel = tk.Label(master=frame2, text='Time Interval', bg="grey")
tintlabel.place(x=35, y=385)

tintentry1 = tk.Entry(master=frame2, justify=CENTER, width=5)
tintentry1.place(x=26, y=406)

tintentry2 = tk.Entry(master=frame2, justify=CENTER, width=5)
tintentry2.place(x=86, y=406)


def timeinterval():
    if fopened != []:
        if curvetype == 1:
            tint = round(JD[int(tintentry2.get()) - 1] - JD[int(tintentry1.get()) - 1], 7)
        if curvetype == 2:
            tint = round(npphase[0][int(tintentry2.get())-1] - npphase[0][int(tintentry1.get())-1], 7)
        global tintoutput
        protocol = open("protocol.txt", "a")
        protocol.write('Time interval start / end: ' + tintentry1.get() + " / " + tintentry2.get() + "\n")
        T.insert(END, '\n' + 'Time interval start / end: ' + tintentry1.get() + ' / ' + tintentry2.get())
        T.see(END)
        if curvetype == 1:
            tintoutput = tk.Label(master=frame2, text=str(tint) + " d", font="Times 10 bold",
                                  bg="light grey", justify=CENTER, width=14)
            protocol.write('Time interval:                      T = ' + str(tint) + " d\n")
            T.insert(END, '\n' + 'Time interval calculated: T = ' + str(tint) + ' d')
            T.see(END)
            protocol.close()
        if curvetype == 2:
            tintoutput = tk.Label(master=frame2, text=str(tint) + " p", font="Times 10 bold",
                                  bg="light grey", justify=CENTER, width=14)
            protocol.write('Time interval:                      T = ' + str(tint) + " p\n")
            T.insert(END, '\n' + 'Time interval calculated: T = ' + str(tint) + ' p')
            T.see(END)
            protocol.close()
        tintoutput.place(x=22, y=463)
    else:
        showinfo(title='Fit Curve', message='No File Selected')


tint_button = ttk.Button(master=frame2, text='Compute', command=timeinterval, width=15)
tint_button.place(x=24, y=432)

tintblacklabel = tk.Label(master=frame2, text=str(''), bg="black", bd=3, width=14)
tintblacklabel.place(x=21, y=462)

tintoutput = tk.Label(master=frame2, text=str(''), bg="light grey", width=14)
tintoutput.place(x=22, y=463)


def selectsample():
    window.delete('samprop')
    path = rawselected
    rawfile = rawpy.imread(path)
    pixr=int(pixelrentry.get())
    pixc=int(pixelcentry.get())
    samplefield = []
    if RBsample.get() == 1:
        samplefield.append(rawfile.raw_image_visible[pixr - 4][pixc - 4])
        samplefield.append(rawfile.raw_image_visible[pixr - 4][pixc - 2])
        samplefield.append(rawfile.raw_image_visible[pixr - 4][pixc])
        samplefield.append(rawfile.raw_image_visible[pixr - 4][pixc + 2])
        samplefield.append(rawfile.raw_image_visible[pixr - 4][pixc + 4])
        samplefield.append(rawfile.raw_image_visible[pixr - 2][pixc - 4])
        samplefield.append(rawfile.raw_image_visible[pixr - 2][pixc - 2])
        samplefield.append(rawfile.raw_image_visible[pixr - 2][pixc])
        samplefield.append(rawfile.raw_image_visible[pixr - 2][pixc + 2])
        samplefield.append(rawfile.raw_image_visible[pixr - 2][pixc + 4])
        samplefield.append(rawfile.raw_image_visible[pixr][pixc - 4])
        samplefield.append(rawfile.raw_image_visible[pixr][pixc - 2])
        samplefield.append(rawfile.raw_image_visible[pixr][pixc])
        samplefield.append(rawfile.raw_image_visible[pixr][pixc + 2])
        samplefield.append(rawfile.raw_image_visible[pixr][pixc + 4])
        samplefield.append(rawfile.raw_image_visible[pixr + 2][pixc - 4])
        samplefield.append(rawfile.raw_image_visible[pixr + 2][pixc - 2])
        samplefield.append(rawfile.raw_image_visible[pixr + 2][pixc])
        samplefield.append(rawfile.raw_image_visible[pixr + 2][pixc + 2])
        samplefield.append(rawfile.raw_image_visible[pixr + 4][pixc + 4])
        samplefield.append(rawfile.raw_image_visible[pixr + 4][pixc - 4])
        samplefield.append(rawfile.raw_image_visible[pixr + 4][pixc - 2])
        samplefield.append(rawfile.raw_image_visible[pixr + 4][pixc])
        samplefield.append(rawfile.raw_image_visible[pixr + 4][pixc + 2])
        samplefield.append(rawfile.raw_image_visible[pixr + 4][pixc + 4])
    else:
        samplefield.append(rawfile.raw_image_visible[pixr-3][pixc-3])
        samplefield.append(rawfile.raw_image_visible[pixr-3][pixc-1])
        samplefield.append(rawfile.raw_image_visible[pixr-3][pixc+1])
        samplefield.append(rawfile.raw_image_visible[pixr-3][pixc+3])
        samplefield.append(rawfile.raw_image_visible[pixr-2][pixc-2])
        samplefield.append(rawfile.raw_image_visible[pixr-2][pixc])
        samplefield.append(rawfile.raw_image_visible[pixr-2][pixc+2])
        samplefield.append(rawfile.raw_image_visible[pixr-1][pixc-3])
        samplefield.append(rawfile.raw_image_visible[pixr-1][pixc-1])
        samplefield.append(rawfile.raw_image_visible[pixr-1][pixc+1])
        samplefield.append(rawfile.raw_image_visible[pixr-1][pixc+3])
        samplefield.append(rawfile.raw_image_visible[pixr][pixc-2])
        samplefield.append(rawfile.raw_image_visible[pixr][pixc])
        samplefield.append(rawfile.raw_image_visible[pixr][pixc+2])
        samplefield.append(rawfile.raw_image_visible[pixr+1][pixc-3])
        samplefield.append(rawfile.raw_image_visible[pixr+1][pixc-1])
        samplefield.append(rawfile.raw_image_visible[pixr+1][pixc+1])
        samplefield.append(rawfile.raw_image_visible[pixr+1][pixc+3])
        samplefield.append(rawfile.raw_image_visible[pixr+2][pixc-2])
        samplefield.append(rawfile.raw_image_visible[pixr+2][pixc])
        samplefield.append(rawfile.raw_image_visible[pixr+2][pixc+2])
        samplefield.append(rawfile.raw_image_visible[pixr+3][pixc-3])
        samplefield.append(rawfile.raw_image_visible[pixr+3][pixc-1])
        samplefield.append(rawfile.raw_image_visible[pixr+3][pixc+1])
        samplefield.append(rawfile.raw_image_visible[pixr+3][pixc+3])
    samplemaxvalue = np.amax(samplefield)
    sampleminvalue = np.amin(samplefield)
    samplemean=np.mean(samplefield)

    samplerange = samplemaxvalue+sampleminvalue
    shiftx = xx - 403 - thumbnailx
    shifty = yy - 151
    window.create_rectangle(shiftx,shifty,shiftx+250,shifty-200, fill='white', outline='black', tags="samprop")
    for i in range(0, len(samplefield)):
        columnscale = samplefield[i]/samplerange
        window.create_rectangle(shiftx+10*i, shifty, shiftx+10+10*i, shifty-int(columnscale*200),
                                fill = "orange", tags="samprop")
    window.create_line(shiftx-3,shifty-int(rawfile.raw_image_visible[pixr][pixc]*200/samplerange),
                       shiftx+250, shifty-int(rawfile.raw_image_visible[pixr][pixc]*200/samplerange),
                       width = 2, stipple='gray25', tags="samprop")
    if rawfile.raw_image_visible[pixr][pixc]/samplemean > 1.1 or rawfile.raw_image_visible[pixr][pixc]/samplemean < 0.9:
        window.create_text(shiftx-30, shifty-int(rawfile.raw_image_visible[pixr][pixc]*200/samplerange),
                           text = str(rawfile.raw_image_visible[pixr][pixc]), tags="samprop")
    window.create_line(shiftx-3,shifty-int(samplemean*200/samplerange),
                       shiftx+250, shifty-int(samplemean*200/samplerange), width = 2, stipple='gray25', tags="samprop")
    window.create_text(shiftx-30, shifty-int(samplemean*200/samplerange), text = str(samplemean), tags="samprop")

    if RBsample.get() == 1:
        window.create_rectangle(shiftx-115,shifty,shiftx-110,shifty-5, fill = pixcolor, tags="samprop")
        window.create_rectangle(shiftx-105,shifty,shiftx-100,shifty-5, fill = pixcolor, tags="samprop")
        window.create_rectangle(shiftx-95,shifty,shiftx-90,shifty-5, fill = pixcolor, tags="samprop")
        window.create_rectangle(shiftx-85,shifty,shiftx-80,shifty-5, fill = pixcolor, tags="samprop")
        window.create_rectangle(shiftx-75,shifty,shiftx-70,shifty-5, fill = pixcolor, tags="samprop")
        window.create_rectangle(shiftx-115,shifty-10,shiftx-110,shifty-15, fill = pixcolor, tags="samprop")
        window.create_rectangle(shiftx-105,shifty-10,shiftx-100,shifty-15, fill = pixcolor, tags="samprop")
        window.create_rectangle(shiftx-95,shifty-10,shiftx-90,shifty-15, fill = pixcolor, tags="samprop")
        window.create_rectangle(shiftx-85,shifty-10,shiftx-80,shifty-15, fill = pixcolor, tags="samprop")
        window.create_rectangle(shiftx-75,shifty-10,shiftx-70,shifty-15, fill = pixcolor, tags="samprop")
        window.create_rectangle(shiftx-115,shifty-20,shiftx-110,shifty-25, fill = pixcolor, tags="samprop")
        window.create_rectangle(shiftx-105,shifty-20,shiftx-100,shifty-25, fill = pixcolor, tags="samprop")
        window.create_rectangle(shiftx-95,shifty-20,shiftx-90,shifty-25, fill = "orange", tags="samprop")
        window.create_rectangle(shiftx-85,shifty-20,shiftx-80,shifty-25, fill = pixcolor, tags="samprop")
        window.create_rectangle(shiftx-75,shifty-20,shiftx-70,shifty-25, fill = pixcolor, tags="samprop")
        window.create_rectangle(shiftx-115,shifty-30,shiftx-110,shifty-35, fill = pixcolor, tags="samprop")
        window.create_rectangle(shiftx-105,shifty-30,shiftx-100,shifty-35, fill = pixcolor, tags="samprop")
        window.create_rectangle(shiftx-95,shifty-30,shiftx-90,shifty-35, fill = pixcolor, tags="samprop")
        window.create_rectangle(shiftx-85,shifty-30,shiftx-80,shifty-35, fill = pixcolor, tags="samprop")
        window.create_rectangle(shiftx-75,shifty-30,shiftx-70,shifty-35, fill = pixcolor, tags="samprop")
        window.create_rectangle(shiftx-115,shifty-40,shiftx-110,shifty-45, fill = pixcolor, tags="samprop")
        window.create_rectangle(shiftx-105,shifty-40,shiftx-100,shifty-45, fill = pixcolor, tags="samprop")
        window.create_rectangle(shiftx-95,shifty-40,shiftx-90,shifty-45, fill = pixcolor, tags="samprop")
        window.create_rectangle(shiftx-85,shifty-40,shiftx-80,shifty-45, fill = pixcolor, tags="samprop")
        window.create_rectangle(shiftx-75,shifty-40,shiftx-70,shifty-45, fill = pixcolor, tags="samprop")
    else:
        if pixcolor == 'green':
            color1 = 'green'
            color2 = 'green'
        if pixcolor == 'blue':
            color1 = 'blue'
            color2 = 'red'
        if pixcolor == 'red':
            color1 = 'red'
            color2 = 'blue'
        window.create_rectangle(shiftx-110,shifty-35,shiftx-105,shifty-40, fill = color2, tags="samprop")
        window.create_rectangle(shiftx-100,shifty-35,shiftx-95,shifty-40, fill = color2, tags="samprop")
        window.create_rectangle(shiftx-90,shifty-35,shiftx-85,shifty-40, fill = color2, tags="samprop")
        window.create_rectangle(shiftx-80,shifty-35,shiftx-75,shifty-40, fill = color2, tags="samprop")
        window.create_rectangle(shiftx-105,shifty-30,shiftx-100,shifty-35, fill = color1, tags="samprop")
        window.create_rectangle(shiftx-95,shifty-30,shiftx-90,shifty-35, fill = color1, tags="samprop")
        window.create_rectangle(shiftx-85,shifty-30,shiftx-80,shifty-35, fill = color1, tags="samprop")
        window.create_rectangle(shiftx-110,shifty-25,shiftx-105,shifty-30, fill = color2, tags="samprop")
        window.create_rectangle(shiftx-100,shifty-25,shiftx-95,shifty-30, fill = color2, tags="samprop")
        window.create_rectangle(shiftx-90,shifty-25,shiftx-85,shifty-30, fill = color2, tags="samprop")
        window.create_rectangle(shiftx-80,shifty-25,shiftx-75,shifty-30, fill = color2, tags="samprop")
        window.create_rectangle(shiftx-105,shifty-20,shiftx-100,shifty-25, fill = color1, tags="samprop")
        window.create_rectangle(shiftx-95,shifty-20,shiftx-90,shifty-25, fill = "orange", tags="samprop")
        window.create_rectangle(shiftx-85,shifty-20,shiftx-80,shifty-25, fill = color1, tags="samprop")
        window.create_rectangle(shiftx-110,shifty-15,shiftx-105,shifty-20, fill = color2, tags="samprop")
        window.create_rectangle(shiftx-100,shifty-15,shiftx-95,shifty-20, fill = color2, tags="samprop")
        window.create_rectangle(shiftx-90,shifty-15,shiftx-85,shifty-20, fill = color2, tags="samprop")
        window.create_rectangle(shiftx-80,shifty-15,shiftx-75,shifty-20, fill = color2, tags="samprop")
        window.create_rectangle(shiftx-105,shifty-10,shiftx-100,shifty-15, fill = color1, tags="samprop")
        window.create_rectangle(shiftx-95,shifty-10,shiftx-90,shifty-15, fill = color1, tags="samprop")
        window.create_rectangle(shiftx-85,shifty-10,shiftx-80,shifty-15, fill = color1, tags="samprop")
        window.create_rectangle(shiftx-110,shifty-5,shiftx-105,shifty-10, fill = color2, tags="samprop")
        window.create_rectangle(shiftx-100,shifty-5,shiftx-95,shifty-10, fill = color2, tags="samprop")
        window.create_rectangle(shiftx-90,shifty-5,shiftx-85,shifty-10, fill = color2, tags="samprop")
        window.create_rectangle(shiftx-80,shifty-5,shiftx-75,shifty-10, fill = color2, tags="samprop")


def wav2RGB(wavelength):
    w = int(wavelength)

    # colour
    if w >= 380 and w < 440:
        R = -(w - 440.) / (440. - 350.)
        G = 0.0
        B = 1.0
    elif w >= 440 and w < 490:
        R = 0.0
        G = (w - 440.) / (490. - 440.)
        B = 1.0
    elif w >= 490 and w < 510:
        R = 0.0
        G = 1.0
        B = -(w - 510.) / (510. - 490.)
    elif w >= 510 and w < 580:
        R = (w - 510.) / (580. - 510.)
        G = 1.0
        B = 0.0
    elif w >= 580 and w < 645:
        R = 1.0
        G = -(w - 645.) / (645. - 580.)
        B = 0.0
    elif w >= 645 and w <= 780:
        R = 1.0
        G = 0.0
        B = 0.0
    else:
        R = 0.0
        G = 0.0
        B = 0.0

    # intensity correction
    if w >= 380 and w < 420:
        SSS = 0.3 + 0.7*(w - 350) / (420 - 350)
    elif w >= 420 and w <= 700:
        SSS = 1.0
    elif w > 700 and w <= 780:
        SSS = 0.3 + 0.7*(780 - w) / (780 - 700)
    else:
        SSS = 0.0
    SSS *= 255

    return [int(SSS*R), int(SSS*G), int(SSS*B)]


pixelrlabel = tk.Label(master=frame3, text='Wavelength\nto RGB', bg="grey")
pixelrlabel.place(x=635, y=3)


def rgbtohex(r,g,b):
    return f'#{r:02x}{g:02x}{b:02x}'


def wlengcolor():
    wleng = int(wlengthentry.get())
    rgb = wav2RGB(wleng)
    print(rgb[0], rgb[1], rgb[2])
    print(rgbtohex(r = rgb[0], g = rgb[1], b = rgb[2]))
    hexcolor = rgbtohex(r = rgb[0], g = rgb[1], b = rgb[2])
    window.create_rectangle(0,0,xx - 150, yy - 147, fill = hexcolor, tags="samprop")

wlengthentry = tk.Spinbox(master=frame3, from_=380, to=780, increment=1,
                          command=wlengcolor, justify=CENTER, width=5)
wlengthentry.place(x=708, y=13)

wlength_button = ttk.Button(master=frame3, text='>', command=wlengcolor, width=1)
wlength_button.place(x=760, y=10)

def clearwindow():
    fitentry1.delete(0, 'end')
    fitentry2.delete(0, 'end')
    tintentry1.delete(0, 'end')
    tintentry2.delete(0, 'end')
    checkboxGauss.deselect()
    checkboxLorentz.deselect()
    window.delete("all")
    # tintoutput.destroy()
    fitcounter.clear()
    tintoutput = tk.Label(master=frame2, text='', bg="light grey", width=14)
    tintoutput.place(x=22, y=463)
    min1toutput = tk.Label(master=frame2, text='', bg="light grey", width=15)
    min1toutput.place(x=27, y=225)
    magmin1toutput = tk.Label(master=frame2, text='', bg="light grey", width=15)
    magmin1toutput.place(x=27, y=251)
    min2toutput = tk.Label(master=frame2, text='', bg="light grey", width=15)
    min2toutput.place(x=27, y=277)
    magmin2toutput = tk.Label(master=frame2, text='', bg="light grey", width=15)
    magmin2toutput.place(x=27, y=303)
    timedifoutput = tk.Label(master=frame2, text='', bg="light grey", width=12)
    timedifoutput.place(x=48, y=329)
    mindifoutput = tk.Label(master=frame2, text='', bg="light grey", width=12)
    mindifoutput.place(x=48, y=355)
    if 'lines' in globals():
        lines.clear()
    phase[0].clear()
    phase[1].clear()
    phase[2].clear()
    if 'npphase' in globals():
        np.delete(npphase, 0)
        np.delete(npphase, 1)
        np.delete(npphase, 2)
    # Tmin1.clear()
    # magmin1.clear()
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
    if 'f' in locals():
        f.close()


clear_button = ttk.Button(master=frame4, text='Clear All', command=clearwindow, width=15)
clear_button.place(x=22, y=10)

protocol.close()
root.mainloop()
