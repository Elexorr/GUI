# program raw
import rawpy
from tkinter import *
# import imageio

path = 'rgb3.CR2'
# with rawpy.imread(path) as raw:
#     rgb = raw.postprocess()
# imageio.imsave('rgb.tiff', rgb)
rawfile = rawpy.imread(path)
print(rawfile.sizes)
print(rawfile.black_level_per_channel)
print(rawfile.white_level)
print("Typ raw snimku:", rawfile.raw_type)
print("Pocet farebnych filtrov =", rawfile.num_colors)
print("Farebna mriezka (0 - 3):", rawfile.color_desc)
# print(rawfile.raw_color(0,0), "", rawfile.raw_color(0,1))
# print(rawfile.raw_color(1,0), "", rawfile.raw_color(1,1))

print(rawfile.raw_pattern)

minvalue = 16000
maxvalue = 0
x = 0
y = 0

for i in range(1, (rawfile.sizes.height)):
    for j in range(1, (rawfile.sizes.width)):
        if rawfile.raw_image_visible[i,j] < minvalue:
            minvalue = rawfile.raw_image_visible[i,j]
        if rawfile.raw_image_visible[i,j] > maxvalue:
            maxvalue = rawfile.raw_image_visible[i,j]
print(minvalue, maxvalue)
#
# print(rawfile.raw_colors_visible)

        # print(i, j, rawfile.raw_value(i,j))
        # print(i, j, rawfile.raw_image_visible[i, j])

# print(rawfile.raw_colors)
# print(rawfile.raw_colors_visible)

# print(rawfile.raw_value(1000, 1000))
# print(rawfile.black_level_per_channel)
# print(rawfile.camera_white_level_per_channel)

# print(rawfile.raw_image)
# print(rawfile.raw_image_visible)

# root = Tk()
# canvas = Canvas(root, width = 1000, height = 1000)
# canvas.pack()
# img = PhotoImage(file="rgb6.CR2")
# canvas.create_image(20,20, anchor=NW, image=img)
# mainloop()

rawfile.close()