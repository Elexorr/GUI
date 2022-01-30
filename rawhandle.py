import os
from io import BytesIO
import matplotlib.pyplot as plt
import rawpy
import exifread
import numpy as np
import cv2
from tkinter import *
import PIL.Image
import PIL.ExifTags
from PIL import ImageTk,Image,ExifTags
from fractions import Fraction

raw_filename = 'test2.CR2'

# with rawpy.imread(raw_filename) as raw:
#     print(f'raw type:                     {raw.raw_type}')  # raw type (flat or stack, e.g., Foveon sensor)
#     print(
#         f'number of colors:             {raw.num_colors}')  # number of different color components, e.g., 3 for common RGB Bayer sensors with two green identical green sensors
#     print(f'color description:            {raw.color_desc}')  # describes the various color components
#     print(f'raw pattern:                  {raw.raw_pattern.tolist()}')  # decribes the pattern of the Bayer sensor
#     print(f'black levels:                 {raw.black_level_per_channel}')  # black level correction
#     print(f'white level:                  {raw.white_level}')  # camera white level
#     print(
#         f'color matrix:                 {raw.color_matrix.tolist()}')  # camera specific color matrix, usually obtained from a list in rawpy (not from the raw file)
#     print(
#         f'XYZ to RGB conversion matrix: {raw.rgb_xyz_matrix.tolist()}')  # camera specific XYZ to camara RGB conversion matrix
#     print(
#         f'camera white balance:         {raw.camera_whitebalance}')  # the picture's white balance as determined by the camera
#     print(f'daylight white balance:       {raw.daylight_whitebalance}')  # the camera's daylight white balance
#
# raw.close()

# f = open(raw_filename, 'rb')
# tags = exifread.process_file(f)
# data = list(tags. items())
# an_array = np. array(data)
# for i in range (0,len(an_array)):
#     if an_array[i][0] == 'EXIF ExposureTime':
#         print(an_array[i][1])
#         time = str(an_array[i][1])
#         # print(float(sum(Fraction(time) for time in time.split())))
#         timetime = float(sum(Fraction(time) for time in time.split()))
#         timetime = round(timetime,2)
#         print(timetime)

#
# root = Tk()
# canvas = Canvas(root, width = 1024, height = 768)
# canvas.pack()
#
# print(raw_filename)
# filename, _ = os.path.splitext(raw_filename)
# with rawpy.imread(raw_filename) as raw:
#
#
#
#     try:
#         thumb = raw.extract_thumb()
#     except rawpy.LibRawNoThumbnailError:
#         print('no thumbnail found')
#
#     else:
#
#
#
#         if thumb.format in [rawpy.ThumbFormat.JPEG, rawpy.ThumbFormat.BITMAP]:
#             if thumb.format is rawpy.ThumbFormat.JPEG:
#                 thumb_filename = filename + '_thumb.jpg'
#                 with open(thumb_filename, 'wb') as f:
#                     f.write(thumb.data)
#                 thumb_rgb = Image.open(BytesIO(thumb.data))
#             else:
#                 thumb_filename = filename + '_thumb.tiff'
#                 thumb_rgb = Image.fromarray(thumb.data)
#                 thumb_rgb.save(filename, 'tiff')
#
#         img = ImageTk.PhotoImage(Image.open(thumb_filename))
#         snimok = Image.open(thumb_filename)
#         resized=snimok.resize((1024, 768))
#         img = ImageTk.PhotoImage(resized)
#         canvas.create_image(1024, 768, anchor=SE, image=img)
#
#         histimg = cv2.imread(raw_filename, 0)
#         plt.hist(histimg.ravel(), 256, [0, 256]);
#         plt.show()
#
#
#
#
#
#
# root.mainloop()


