import PySimpleGUI as sg #pip install PySimpleGUI
import yaml #pip install pyyaml
import os.path
from os import path
from datetime import datetime

############################# BACKEND ###############################

def loadFileSET(fileName):
    setFile = []
    dict_item = {}
    list_data = []

    with open(fileName) as f:
        line = f.readline()
        setFile.append({'name':'File','data':fileName})
        list_data = []
        while line:
            if line[0] == '$':
                if len(dict_item) > 0:
                    dict_item.update({'data': list_data})
                    setFile.append(dict_item)
                    #Hasta este momento se agrega el elemento, por lo que si no tiene datos, y sólo es el titulo no se agrega
                    #Esto no lo he visto como un error, pues el único que le pasa esto es a $ END OF MODEL FILE, que siempre
                    # va al final y lo agrego manualmente al guardar el archivo.
                    #Avis Phoenix - 01 Jul 2020
                if line[2:6] != 'File':
                    line= line.rstrip('\n')
                    dict_item = {'name':line[2:]}
                    list_data = []
                    
            else:
                if len(line) > 1: #Evitamos los saltos de línea
                    list_data.append(line)
            line = f.readline()
        f.close()

    return setFile

def saveFileSET(fileName, setFile):

    with open(fileName, 'w') as f:
        f.write('$ File ' + fileName + ' saved ' + datetime.today().strftime('%m/%d/%Y %I:%M:%S %p') + '\n\n')
        for section in setFile:
            #Formato de fecha: https://strftime.org/
            if section.get('name') != 'File':
                sectionData = [ '$ ' +section.get('name') + '\n']
                sectionData.extend(section.get('data'))
                sectionData.append('\n')
                f.writelines(sectionData)
        f.write('$ END OF MODEL FILE')
        f.close()

    return setFile

def getSectionsFileSET(setFile):
    sections = []

    for item in setFile:
        sections.append(item.get('name'))
    
    return sections

def getSectionByName(setFile,sectionName):
    i = 0
    while i < len(setFile) and setFile[i].get('name') != sectionName:
        i = i+1
    
    if i >= len(setFile):
        i = -1
    
    return i

def verifyUnit(setFile1,setFile2):
    i1 = getSectionByName(setFile1,'CONTROLS')
    i2 = getSectionByName(setFile2,'CONTROLS')

    errors = []

    if i1 >= 0 and i2 >= 0:
        controls1 = setFile1[i1]
        controls2 = setFile2[i2]
        i1 = getSectionByName(setFile1,'File')
        if controls1.get('data') is not None:
            if controls1.get('data')[0] != controls2.get('data')[0]:
                errors.append({'msg':'Se esperaba "' + controls2.get('data')[0] + '"', 'file': setFile1[i1].get('data'), 'unit': controls1.get('data')[0]})
        else:
            errors.append({'msg':'Sin unidad', 'file': setFile1[i1].get('data'), 'unit': '?'})

    return errors

def validSETFile(setFile):
    #Validación básica del archivo
    errors=[]

    if len( setFile ) > 0:
        iFile = getSectionByName(setFile,'File')
        if iFile < 0:
            errors.append({'msg':'No tiene un registro del archivo', 'file': '??', 'unit': '?'})
        i = getSectionByName(setFile,'CONTROLS')
        if i < 0:
            errors.append({'msg':'No tiene seccion de CONTROLS', 'file': setFile[iFile].get('data'), 'unit': '?'})
    else:
        errors.append({'msg':'Archivo vacío', 'file': '??', 'unit': '?'})
        
    return errors
       
def substituteSection1to2(setFile1,setFile2,sectionName):
    i1 = getSectionByName(setFile1,sectionName)
    i2 = getSectionByName(setFile2,sectionName)

    error=[]
    if i1 < 0:
        i1 = getSectionByName(setFile1,'File')
        error.append({'msg':'No existe la sección ' + sectionName, 'file': setFile1[i1].get('data'), 'unit':'?' })
    if i2 < 0:
        i2 = getSectionByName(setFile2,'File')
        error.append({'msg':'No existe la sección ' + sectionName, 'file': setFile2[i2].get('data'), 'unit':'?' })
    if i1 > 0 and i2 > 0:
        setFile2[i2].update({'data':setFile1[i1].get('data')})
    
    return error

def appendSection1to2(setFile1,setFile2,sectionName):
    i1 = getSectionByName(setFile1,sectionName)
    i2 = getSectionByName(setFile2,sectionName)

    error=[]
    if i1 < 0:
        i1 = getSectionByName(setFile1,'File')
        error.append({'msg':'No existe la sección ' + sectionName, 'file': setFile1[i1].get('data'), 'unit':'?' })
    if i2 < 0:
        i2 = getSectionByName(setFile2,'File')
        error.append({'msg':'No existe la sección ' + sectionName, 'file': setFile2[i2].get('data'), 'unit':'?' })
    if i1 >= 0 and i2 >= 0:
        listF = setFile2[i2].get('data').extend(setFile1[i1].get('data'))
        setFile2[i2].update({'data':listF})
    
    return error

def mergeSection1to2(setFile1,setFile2,sectionName):
    i1 = getSectionByName(setFile1,sectionName)
    i2 = getSectionByName(setFile2,sectionName)

    error=[]
    if i1 < 0:
        i1 = getSectionByName(setFile1,'File')
        error.append({'msg':'No existe la sección ' + sectionName, 'file': setFile1[i1].get('data'), 'unit':'?' })
    if i2 < 0:
        i2 = getSectionByName(setFile2,'File')
        error.append({'msg':'No existe la sección ' + sectionName, 'file': setFile2[i2].get('data'), 'unit':'?' })
    if i1 >= 0 and i2 >= 0:
        #Mal desempeño en listas muy largas
        diff = list( set(setFile1[i1].get('data')) - set(setFile2[i2].get('data')))
        # Ordenamos la lista en el orden del archivo original
        diffGoodOrder = []
        for item in setFile1[i1].get('data'):
            if item in diff:
                diffGoodOrder.append(item)

        if len(diffGoodOrder) > 0:
            listF = setFile2[i2].get('data').extend(diffGoodOrder)
            setFile2[i2].update({'data':listF})
    
    return error

def getFileNames(folder):
    files = []
    for entry in os.listdir(folder):
        if os.path.isfile(os.path.join(folder, entry)) and entry[-3:] == '$et':
            files.append(entry)
    return files

def processingFile(sections,setTemplateFile, fileIn, fileOut):
    errors=[]

    setFileIn = loadFileSET(fileIn)

    errors.extend( validSETFile(setFileIn) )
    errors.extend( verifyUnit(setTemplateFile,setFileIn) )

    if len(errors) == 0:
        for section in sections:
            if section.get('type') == 0:
                errors.extend(substituteSection1to2(setTemplateFile,setFileIn,section.get('section')))
            elif section.get('type') == 1:
                errors.extend(mergeSection1to2(setTemplateFile,setFileIn,section.get('section')))
        
        saveFileSET(fileOut,setFileIn)

    return errors

############################# FRONTEND ###############################

sg.theme('Reddit')   # Add a touch of color

def truncateString(string, maxLen):
    maxLen = 12
    if len(string) > maxLen:
        string = string[0:maxLen-3] + '...'
    return string

def createMainWindow( checkboxes, templetaFileText='', sourcesDirText='', outputDirText='', overwriteFiles=True ):
    mainLayout= [[sg.Text('Plantilla')],
             [sg.Input(templetaFileText, key='-templateFile-', enable_events=True), sg.FileBrowse('...',target='-templateFile-',file_types=(("Archivos Set", "*.$et"),),key="-templateBtn-")],
             [sg.Frame('Secciones', [[sg.Column(checkboxes, size=(315,150), scrollable=True)]],key='-secctionesGpb-', )],
             [sg.Button('Configurar secciones',disabled=not templetaFileText, key='-setupBtn-')],
             [sg.Text('Carpeta de documentos originales')],
             [sg.Input(sourcesDirText, key='-sourcesDir-',enable_events=True), sg.FolderBrowse('...',target='-sourcesDir-',key='-sourcesBtn-')],
             [sg.Checkbox('Sobreescribir archivos',default=overwriteFiles, key="-overwriteFiles-",enable_events=True)],
             [sg.Text('Carpeta de documentos de salida')],
             [sg.Input(outputDirText, key='-outputDir-',disabled=overwriteFiles), sg.FolderBrowse('...',target='-outputDir-',disabled=overwriteFiles,key="-outputBtn-")],
             [sg.Button('Ejecutar',key="-runBtn-")],
             [sg.ProgressBar(100,visible=False, size=(30,10),orientation='h',key="-progressBar-")],
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
            #Pasar de no disponibles a disponibles
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

def getAvailableList(sections):
    #Obtenemos la lista valida de secciones
    unavailableList = loadConfigurationFile(sections)
    availableList = list(set(sections) - set(unavailableList) )
    #Llenamos la lista de secciones con su indice asociado y en el orden en el que se cargó
    FinalList = []
    i=0
    for section in sections:
        if section in availableList:
            FinalList.append({'name': section, 'idx': i})
            i = i+1
    return FinalList

def createLayoutCheckBoxes(sections):
    layout=[]
    for section in availableList:
        i = section.get('idx')
        layout.append([sg.Checkbox(truncateString(section.get('name'),12),default=True, key="-item" + str(i) + "-", size=(13,10) ),sg.Radio('Sustituir',i, default=True,key="-item" + str(i) + "S-"),sg.Radio('Mezclar',i, key="-item" + str(i) + "M-")])
    return layout

def updateCheckBoxes(sections):
    checkboxes = createLayoutCheckBoxes(sections)
    return createMainWindow(checkboxes,values['-templateFile-'],values['-sourcesDir-'],values['-outputDir-'],values['-overwriteFiles-'])

def getCheckBoxesSelection(values,availableList):
    salida = []
    for section in availableList:
        i = section.get('idx')
        if values['-item' + str(i) + '-']:
            tipo = 1
            if values['-item' + str(i) + 'S-']:
                tipo = 0
            salida.append({'section': section.get('name'), 'type': tipo})
    return salida

def processingFiles(templateFile, folderIn, folderOut, sections, window):
    filesIn = getFileNames(folderIn)
    stop = False

    errors = validSETFile(templateFile)
    if len(errors) == 0:

        fechaHoy = datetime.today().strftime('%m_%d_%Y_%H_%M_%S')

        progressBar = window['-progressBar-']
        countFiles = window['-countFiles-']
        texto = "0 / " + str( len(filesIn) ) 
        countFiles.update(texto)

        errorsList = []
        tableErrors =  window['-progressBar-']
        tableErrors.update([['','','']])

        window['-runBtn-'].update('Detener')
        window['-progressBar-'].update(visible=True)
        window['-countFiles-'].update(visible=True)
        window['-fileLbl-'].update(visible=True)
        window['-errorTable-'].update(visible=True)

        i = 0

        while i < len(filesIn) and not stop:
            event, values = window.read(timeout=10)
            if event == '-runBtn-':
                stop = True
                window['-runBtn-'].update('Ejecutar')
                window['-progressBar-'].update(visible=False)
                window['-countFiles-'].update(visible=False)
                window['-fileLbl-'].update(visible=False)
                window['-errorTable-'].update(visible=False)
            if not stop:
                
                fileIn = os.path.join(folderIn, filesIn[i])
                fileOut = os.path.join(folderOut, filesIn[i][:-3] + '_' + fechaHoy + '.$et' )
                errors = processingFile(sections,templateFile,fileIn, fileOut)
                if len(errors) > 0:
                    for error in errors:
                        errorsList.append([error.get('file'),error.get('unit'),error.get('msg')])
                    tableErrors.update(errorsList)
                progressBar.UpdateBar(((i + 1)*100)/ len(filesIn))
                texto = str(i+1) + " / " + str( len(filesIn) ) 
                countFiles.update(texto )
            i =  i + 1
        
        window['-runBtn-'].update('Empezar')
    else:
        sg.popup('Plantilla erronea','El formato del archivo de plantilla es inválido.')

############################# CICLO PRINCIPAL ###############################
#Variables globales
procesando = False
plantilla_file=[]
sections=[]
# Create the Window
checkboxes= [[sg.Text('Abre una plantilla')]]
window = createMainWindow(checkboxes,overwriteFiles=False)
# Ciclo principal de la aplicación
while True:
    if window is not None:
        event, values = window.read()
        if event is None:   # if user closes window
            print('Adiós')
            window.close()
            break #Termina el ciclo
        if event == '-templateFile-':
            plantilla_file = loadFileSET(values['-templateFile-'])
            errors = validSETFile(plantilla_file)
            if len(errors) == 0:
                sections = getSectionsFileSET(plantilla_file)
                availableList = getAvailableList(sections)
                #No se puede crear contenido dinámico en pySimpleGUI por que tengo que re hacer la vista
                #ref: https://www.reddit.com/r/PySimpleGUI/comments/cdrjat/is_it_possible_to_update_the_layout_of_a_column/
                #Avis Phoenix - 21/06/2020 
                window.close()
                window = updateCheckBoxes(availableList)
            else:
                msg = ''
                for error in errors:
                    msg += error.get('msg') + '\n'
                sg.popup('Plantilla erronea','El formato del archivo de plantilla es inválido:\n' + msg)
        if event == '-overwriteFiles-':
            # Habilitamos o deshabilitamos los controles de selección de carpeta de salida
            window['-outputDir-'].update(disabled=values['-overwriteFiles-'])
            window['-outputBtn-'].update(disabled=values['-overwriteFiles-'])
            if values['-overwriteFiles-']:
                window['-outputDir-'].update(sg.popup('Plantilla erronea','El formato del archivo de plantilla es inválido.'))
        if event == '-sourcesDir-' and values['-overwriteFiles-']:
            # Sobreescribimos el texto de la carpeta de salida
            window['-outputDir-'].update(values['-sourcesDir-'])
        if event == '-runBtn-':
            #Acciones del boton de ejecutar
            sections2Process = getCheckBoxesSelection(values,availableList)
            processingFiles(plantilla_file, values['-sourcesDir-'], values['-outputDir-'], sections2Process, window )
        if event == '-setupBtn-':
            runConfigurationWindow(sections)
            #No se puede crear contenido dinámico en pySimpleGUI por que tengo que re hacer la vista
            #ref: https://www.reddit.com/r/PySimpleGUI/comments/cdrjat/is_it_possible_to_update_the_layout_of_a_column/
            #Avis Phoenix - 21/06/2020 
            window.close()
            availableList = getAvailableList(sections)
            window = updateCheckBoxes(availableList)
        
    else:
        sg.popup('Error inesperado :(', 'Disculpa')
        break

