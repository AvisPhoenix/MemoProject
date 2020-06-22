import PySimpleGUI as sg

sg.theme('Reddit')   # Add a touch of color

#MainWindows
checkboxes= [[sg.Text('Abre una plantilla')]]
mainLayout= [[sg.Text('Plantilla')],
             [sg.Input('', key='-templateFile-', enable_events=True), sg.FileBrowse('...',target='-templateFile-',file_types=(("Archivos Set", "*.$et"),),key="-templateBtn-")],
             [sg.Frame('Secciones', checkboxes,key='-secctionesGpb-') ],
             [sg.Button('Configurar secciones', disabled=True)],
             [sg.Text('Carpeta de documentos originales')],
             [sg.Input('', key='-sourcesDir-',enable_events=True), sg.FolderBrowse('...',target='-sourcesDir-',key='-sourcesBtn-')],
             [sg.Checkbox('Sobreescribir archivos',default=True, key="-overwriteFiles-",enable_events=True)],
             [sg.Text('Carpeta de documentos de salida')],
             [sg.Input('', key='-outputDir-',disabled=True), sg.FolderBrowse('...',target='-outputDir-',disabled=True,key="-outputBtn-")],
             [sg.Button('Ejecutar',key="-runBtn-")],
             [sg.ProgressBar(100,visible=True, size=(30,10),orientation='horizontal',key="-progressBar-")],
             [sg.Text('0/0', visible=True,key="countFiles"),sg.Text('archivos', visible=True)],
             [sg.Table(values=[['','','']],headings=['Archivo','Unidad','Error'],col_widths=[20,10,20],auto_size_columns=False,num_rows=1)]
            ]
# Create the Window
window = sg.Window('Copia en lote', mainLayout)


# Event Loop to process "events" and get the "values" of the inputs
while True:
    if window is not None:
        event, values = window.read()
        if event is None:   # if user closes window
            print('Adiós')
            window.close()
            break #Termina el ciclo
        if event == '-templateFile-':
            #No se puede crear contenido dinámico en pySimpleGUI por que tengo que re hacer la vista
            #ref: https://www.reddit.com/r/PySimpleGUI/comments/cdrjat/is_it_possible_to_update_the_layout_of_a_column/
            #Avis Phoenix - 21/06/2020
            checkboxes = []
            checkboxes.append([sg.Checkbox('Seccion1',default=True, key="item1"),sg.Radio('Sustituir',0),sg.Radio('Mezclar',0, default=True)])
            checkboxes.append([sg.Checkbox('Seccion2',default=True, key="item2"),sg.Radio('Sustituir',1),sg.Radio('Mezclar',1, default=True)])
            checkboxes.append([sg.Checkbox('Seccion3',default=True, key="item3"),sg.Radio('Sustituir',2),sg.Radio('Mezclar',2, default=True)])
            mainLayout= [[sg.Text('Plantilla')],
             [sg.Input(values['-templateFile-'], key='-templateFile-', enable_events=True), sg.FileBrowse('...',target='-templateFile-',file_types=(("Archivos Set", "*.$et"),),key="-templateBtn-")],
             [sg.Frame('Secciones', checkboxes,key='-secctionesGpb-') ],
             [sg.Button('Configurar secciones',)],
             [sg.Text('Carpeta de documentos originales')],
             [sg.Input(values['-sourcesDir-'], key='-sourcesDir-',enable_events=True), sg.FolderBrowse('...',target='-sourcesDir-',key='-sourcesBtn-')],
             [sg.Checkbox('Sobreescribir archivos',default=values['-overwriteFiles-'], key="-overwriteFiles-",enable_events=True)],
             [sg.Text('Carpeta de documentos de salida')],
             [sg.Input(values['-outputDir-'], key='-outputDir-',disabled=values['-overwriteFiles-']), sg.FolderBrowse('...',target='-outputDir-',disabled=values['-overwriteFiles-'],key="-outputBtn-")],
             [sg.Button('Ejecutar',key="-runBtn-")],
             [sg.ProgressBar(100,visible=True, size=(30,10),orientation='horizontal',key="-progressBar-")],
             [sg.Text('0/0', visible=True,key="countFiles"),sg.Text('archivos', visible=True)],
             [sg.Table(values=[['','','']],headings=['Archivo','Unidad','Error'],col_widths=[20,10,20],auto_size_columns=False,num_rows=1)]
            ]
            window.close()
            window = sg.Window('Copia en lote', mainLayout)
        if event == '-overwriteFiles-':
            window['-outputDir-'].update(disabled=values['-overwriteFiles-'])
            window['-outputBtn-'].update(disabled=values['-overwriteFiles-'])
        if event == '-sourcesDir-' and values['-overwriteFiles-']:
            window['-outputDir-'].update(values['-sourcesDir-'])
        print('Evento ', event)
        print(values)
        
    else:
        sg.popup('Error inesperado :(', 'Disculpa')
        break
