# PySimpleGUI

import PySimpleGUI as psg

#vytvori okno podla rozmerov monitora
width, height = psg.Window.get_screen_size()

#tlacidlo = [[psg.Text("Nazdar")], [psg.Button("OK")]]

#window = psg.Window("Demo", layout).read()
tlacidlo = [  [psg.Text('Some text on Row 1')],
            [psg.Text('Enter something on Row 2'), psg.InputText()],
            [psg.Button('Ok'), psg.Button('Cancel')] ]

plocha = psg.Window(title = "Ahoj kokot!", layout = tlacidlo, location = (0,0),
                    margins=(width/2, height/2),  keep_on_top=True).read()

while True:
    event, values = plocha.read()
    if event == psg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        break
    print('You entered ', values[0])

plocha.close()
