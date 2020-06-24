import PySimpleGUI as sg #pip install PySimpleGUI
import yaml #pip install pyyaml
import os.path
from os import path

sg.theme('Reddit')   # Add a touch of color

def loadFileSET(fileName):
    pass

def createMainWindow( checkboxes, templetaFileText='', sourcesDirText='', outputDirText='', overwriteFiles=True ):
    mainLayout= [[sg.Text('Plantilla')],
             [sg.Input(templetaFileText, key='-templateFile-', enable_events=True), sg.FileBrowse('...',target='-templateFile-',file_types=(("Archivos Set", "*.$et"),),key="-templateBtn-")],
             [sg.Frame('Secciones', checkboxes,key='-secctionesGpb-') ],
             [sg.Button('Configurar secciones',disabled=not templetaFileText, key='-setupBtn-')],
             [sg.Text('Carpeta de documentos originales')],
             [sg.Input(sourcesDirText, key='-sourcesDir-',enable_events=True), sg.FolderBrowse('...',target='-sourcesDir-',key='-sourcesBtn-')],
             [sg.Checkbox('Sobreescribir archivos',default=overwriteFiles, key="-overwriteFiles-",enable_events=True)],
             [sg.Text('Carpeta de documentos de salida')],
             [sg.Input(outputDirText, key='-outputDir-',disabled=overwriteFiles), sg.FolderBrowse('...',target='-outputDir-',disabled=overwriteFiles,key="-outputBtn-")],
             [sg.Button('Ejecutar',key="-runBtn-")],
             [sg.ProgressBar(100,visible=False, size=(30,10),orientation='horizontal',key="-progressBar-")],
             [sg.Text('0/0', visible=False,key="-countFiles-"),sg.Text('archivos', visible=False, key="-fileLbl-")],
             [sg.Table(values=[['','','']], key='-errorTable-', visible=False,headings=['Archivo','Unidad','Error'],col_widths=[20,10,20],auto_size_columns=False,num_rows=1)]
            ]
    return sg.Window('Copia en lote', mainLayout)

def createConfigurationWindow(availableList, unavailableList):
    col1= [[sg.Text('Disponibles')],
            [sg.Listbox(availableList, select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, size=(20,10), key="-availableList-")]
            ]
    col2= [[sg.Button('▶',key='-rightBtn-')],[sg.Button('◀',key='-leftBtn-')]]
    col3= [[sg.Text('No disponibles')],
            [sg.Listbox(unavailableList, select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, size=(20,10), key="-unavailableList-")]
            ]
    layout= [[sg.Column(col1),sg.Column(col2),sg.Column(col3)], [sg.Button('Guardar',key='-saveBtn-'),sg.Button('Cancelar',key='-cancelBtn-')]]
    return sg.Window('Configurar secciones', layout)

def loadConfigurationFile(sections):
    confFile='conf.yaml'
    unavailableList=[]
    if path.exists(confFile):
        with open(confFile) as file:
            document = yaml.full_load(file)
            for item, doc in document.items():
                if item == 'Unavailable':
                    unavailableList = doc
    if len(unavailableList) > 0 and len(sections) > 0:
        # Si hay elementos no disponibles los intersectamos con las secciones existentes
        # Nota este método de intersección no es eficiente con listas muy grandes
        unavailableList = list(set(sections) & set(unavailableList))
    return unavailableList

def saveConfigurationFile(availableList,unavailableList):
    confFile='conf.yaml'
    # Obtener la lista de no disponibles ya existente
    oldUnavailableList = loadConfigurationFile([])
    # Unimos la lista de no disponibles (hay que cuidar no tener repetidos, por eso lo convertimos en conjuntos)
    # Nota este método de unión no es eficiente con listas muy grandes
    unavailableListFinal = list((set(unavailableList) | set(oldUnavailableList)) - set(availableList))
    dict_file = {'Unavailable': unavailableListFinal}
    with open(confFile, 'w') as file:
        yaml.dump(dict_file,file)

def runConfigurationWindow(sections):
    unavailableList = loadConfigurationFile(sections)
    availableList = list(set(sections) - set(unavailableList))
    modalwindow= createConfigurationWindow(availableList,unavailableList)
    while True and modalwindow is not None:
        event, values = modalwindow.read()
        if event in (None,'-cancelBtn-'):
            #Salir
            modalwindow.close()
            break
        if event == '-rightBtn-':
            #Pasar de disponibles a no disponbles
            for item in values['-availableList-']:
                availableList.remove(item)
                unavailableList.append(item)
            modalwindow['-availableList-'].update(availableList)
            modalwindow['-unavailableList-'].update(unavailableList)
        if event == '-leftBtn-':
            #Pasar de no disnibles a disponibles
            for item in values['-unavailableList-']:
                unavailableList.remove(item)
                availableList.append(item)
            modalwindow['-availableList-'].update(availableList)
            modalwindow['-unavailableList-'].update(unavailableList)
        if event == '-saveBtn-':
            #Guardar y salir
            saveConfigurationFile(availableList,unavailableList)
            modalwindow.close()
            break

def createLayoutCheckBoxes(sections):
    layout=[]
    i = 1
    unavailableList = loadConfigurationFile(sections)
    availableList = list(set(sections) - set(unavailableList) )
    for section in availableList:
        layout.append([sg.Checkbox(section,default=True, key="-item" + str(i) + "-" ),sg.Radio('Sustituir',i,key="-item" + str(i) + "S-"),sg.Radio('Mezclar',i, default=True,key="-item" + str(i) + "M-")])
        i = i+1
    return layout

def updateCheckBoxes(sections):
    checkboxes = createLayoutCheckBoxes(sections)
    return createMainWindow(checkboxes,values['-templateFile-'],values['-sourcesDir-'],values['-outputDir-'],values['-overwriteFiles-'])

#MainWindows
checkboxes= [[sg.Text('Abre una plantilla')]]

# Create the Window
window = createMainWindow(checkboxes)
procesando = False
# Ciclo principal de la aplicación
while True:
    if window is not None:
        event, values = window.read()
        if event is None:   # if user closes window
            print('Adiós')
            window.close()
            break #Termina el ciclo
        if event == '-templateFile-':
            sections=['Seccion1','Seccion2','Seccion3']
            #No se puede crear contenido dinámico en pySimpleGUI por que tengo que re hacer la vista
            #ref: https://www.reddit.com/r/PySimpleGUI/comments/cdrjat/is_it_possible_to_update_the_layout_of_a_column/
            #Avis Phoenix - 21/06/2020 
            window.close()
            window = updateCheckBoxes(sections)
        if event == '-overwriteFiles-':
            # Habilitamos o deshabilitamos los controles de selección de carpeta de salida
            window['-outputDir-'].update(disabled=values['-overwriteFiles-'])
            window['-outputBtn-'].update(disabled=values['-overwriteFiles-'])
        if event == '-sourcesDir-' and values['-overwriteFiles-']:
            # Sobreescribimos el texto de la carpeta de salida
            window['-outputDir-'].update(values['-sourcesDir-'])
        if event == '-runBtn-':
            #Acciones del boton de ejecutar
            if procesando:
                window['-runBtn-'].update('Ejecutar')
            else:
                window['-runBtn-'].update('Cancelar')
            window['-progressBar-'].update(visible=not procesando)
            window['-countFiles-'].update(visible=not procesando)
            window['-fileLbl-'].update(visible=not procesando)
            window['-errorTable-'].update(visible=not procesando)
            procesando = not procesando
        if event == '-setupBtn-':
            sections=['Seccion1','Seccion2','Seccion3']
            runConfigurationWindow(sections)
            #No se puede crear contenido dinámico en pySimpleGUI por que tengo que re hacer la vista
            #ref: https://www.reddit.com/r/PySimpleGUI/comments/cdrjat/is_it_possible_to_update_the_layout_of_a_column/
            #Avis Phoenix - 21/06/2020 
            window.close()
            window = updateCheckBoxes(sections)
        print('Evento ', event)
        print(values)
        
    else:
        sg.popup('Error inesperado :(', 'Disculpa')
        break
