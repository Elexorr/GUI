import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
import sys, os
import numpy as np
from astropy.io import fits
import rawpy


root = tk.Tk()
root.title("Extractor")
root.geometry('320x240')
root.resizable(False, False)

frame = tk.Frame(master=root, width=320, height=240, bg="grey")  # yy*0.9-76
frame.grid(row=0, column=0, sticky=N)

# Tu nastavujes ktore kanaly chces extrahovat
Gray = 1           # Cely snimok bez rozbitia do fit
Red = 1            # Cerveny kanal
Green1 = 0         # Zeleny kanal 1
Green2 = 0         # Zeleny kanal 2
Blue = 1           # Modry kanal
GpG = 0            # Zelene sucet
GavG = 1           # Zelene priemer


# Vyberas snimky na rozbitie
def selectmultipleraws():
    filetypes = ('RAW files', '*.CRW *.CR2 *CR3 *.NEF *.ARW')
    global raw_filenames
    raw_filenames = fd.askopenfilenames(title='Open Multiple RAW', initialdir='/', filetypes=[('RAW files', '*.CRW *.CR2 *CR3 *.NEF *.ARW')])


openmultiraw_button = ttk.Button(master=frame, text='Open Multiple RAW', command=selectmultipleraws, width=18)
openmultiraw_button.place(x=5, y=5)


def channelextract():
        # Tu dajak cesty nastavuje uz nepamatam jak
        curdir = os.path.dirname(raw_filenames[0])
        print(curdir)
        path = (curdir + '/Grayscale/')
        print(path)
        isDir = os.path.isdir(path)
        print(isDir)
        # Tu len kontroluje ci uz existuju adresare podla kanalov, ked nesu vytvori - vcelku zbytocne, len aby nehlasil chybu
        isDir = os.path.isdir(curdir + '/Grayscale/')
        if isDir == False:
            os.mkdir(curdir + '/Grayscale/')
        isDir = os.path.isdir(curdir + '/Blue/')
        if isDir == False:
            os.mkdir(curdir + '/Blue/')
        isDir = os.path.isdir(curdir + '/Red/')
        if isDir == False:
            os.mkdir(curdir + '/Red/')
        isDir = os.path.isdir(curdir + '/Green1/')
        if isDir == False:
            os.mkdir(curdir + '/Green1/')
        isDir = os.path.isdir(curdir + '/Green2/')
        if isDir == False:
            os.mkdir(curdir + '/Green2/')
        isDir = os.path.isdir(curdir + '/Gsum/')
        if isDir == False:
            os.mkdir(curdir + '/Gsum/')
        isDir = os.path.isdir(curdir + '/Gaverage/')
        if isDir == False:
             os.mkdir(curdir + '/Gaverage/')
        # Tu rozbija na kanaly mazanim parnych a neparnych stlpcov/riadkov
        for j in range(0, len(raw_filenames)):
            with rawpy.imread(raw_filenames[j]) as raw:
                oddx = []
                evenx = []
                for i in range(0, len(raw.raw_image_visible[0]) - 1, 2):
                    oddx.append(i)
                    evenx.append(i + 1)
                oddy = []
                eveny = []
                for i in range(0, len(raw.raw_image_visible) - 1, 2):
                    oddy.append(i)
                    eveny.append(i + 1)
                npraw = np.array(raw.raw_image_visible)
                # Grayscale snimok nerozbija, necha tak, ulozi ako fit
                if Gray == 1:
                    hdu = fits.PrimaryHDU(npraw)
                    Grayfile = (curdir + '/Grayscale/' + os.path.basename(raw_filenames[j]).rsplit('.', 1)[
                        0] + '-Gray' + '.fit')
                    hdu.writeto(Grayfile, overwrite=True)
                # Pri farebnych kanaloch najprv vymaze stlpce, ulozi do docasneho pola, tak vymaze aj riadky
                if Blue == 1:
                    nprawblue = np.delete(npraw, oddx, 1)  # deleting odd columns
                    nprawbluefinal = np.delete(nprawblue, oddy, 0)  # deleting odd rows
                    hdub = fits.PrimaryHDU(nprawbluefinal)
                    Bluefile = (curdir + '/Blue/' + os.path.basename(raw_filenames[j]).rsplit('.', 1)[
                        0] + '-Blue' + '.fit')
                    hdub.writeto(Bluefile, overwrite=True)

                if Red == 1:
                    nprawred = np.delete(npraw, evenx, 1)  # vdeleting even columns
                    nprawredfinal = np.delete(nprawred, eveny, 0)  # deleting even rows
                    hdur = fits.PrimaryHDU(nprawredfinal)
                    Redfile = (curdir + '/Red/' + os.path.basename(raw_filenames[j]).rsplit('.', 1)[
                        0] + '-Red' + '.fit')
                    hdur.writeto(Redfile, overwrite=True)
                nprawg1 = np.delete(npraw, oddx, 1)  # deleting odd columns
                nprawg1final = np.delete(nprawg1, eveny, 0)  # deleting even rows

                if Green1 == 1:
                    hdug1 = fits.PrimaryHDU(nprawg1final)
                    Green1file = (curdir + '/Green1/' + os.path.basename(raw_filenames[j]).rsplit('.', 1)[
                        0] + '-G1' + '.fit')
                    hdug1.writeto(Green1file, overwrite=True)
                nprawg2 = np.delete(npraw, evenx, 1)  # deleting even columns
                nprawg2final = np.delete(nprawg2, oddy, 0)  # deleting even rows

                if Green2 == 1:
                    hdug2 = fits.PrimaryHDU(nprawg2final)
                    Green2file = (curdir + '/Green2/' + os.path.basename(raw_filenames[j]).rsplit('.', 1)[
                        0] + '-G2' + '.fit')
                    hdug2.writeto(Green2file, overwrite=True)

                # Zelene kanaly mozes spriemerovat alebo scitat
                if GpG == 1:
                    nprawgplus = (nprawg1final + nprawg2final)
                    hdug = fits.PrimaryHDU(nprawgplus)
                    GpGfile = (curdir + '/Gsum/' + os.path.basename(raw_filenames[j]).rsplit('.', 1)[
                        0] + '-(G+G)' + '.fit')
                    hdug.writeto(GpGfile, overwrite=True)

                if GavG == 1:
                    nprawgaver = (nprawg1final + nprawg2final) // 2
                    hdug = fits.PrimaryHDU(nprawgaver)
                    GavGfile = (curdir + '/Gaverage/' + os.path.basename(raw_filenames[j]).rsplit('.', 1)[
                        0] + '-G(average)' + '.fit')
                    hdug.writeto(GavGfile, overwrite=True)


extract_button = ttk.Button(master=frame, text='Extract', command=channelextract, width=18)
extract_button.place(x=5, y=35)

root.mainloop()