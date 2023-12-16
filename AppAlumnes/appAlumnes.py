from tkinter import ttk
from tkinter import *
from connexio import *
from datetime import datetime
import re
import pandas as pd
import openpyxl
import matplotlib.pyplot as plt

class appAlumnes:
    def __init__(self,finestra,db):
        self.connexio = Connexio(db)
        self.finestra = finestra
        self.finestra.title('AlumnesApp')
        #Afegim un frame
        frame = LabelFrame(self.finestra,text="Alumne")
        frame.grid(row=0,column=0,columnspan=3,pady=20)
        #Input Nom
        Label(frame,text='Nom: ').grid(row=1,column=0,sticky=W)
        self.Nom = Entry(frame)
        self.Nom.grid(row=1,column=1)
        self.Nom.focus()
        #Input Cognoms
        Label(frame,text='Cognoms: ').grid(row=2,column=0,sticky=W)
        self.Cognoms = Entry(frame)
        self.Cognoms.grid(row=2,column=1)
        #Input Data Naixement
        Label(frame,text='Data Naixement (dd/mm/aaaa): ').grid(row=3,column=0,sticky=W)
        self.DataNaixement = Entry(frame)
        self.DataNaixement.grid(row=3,column=1)
        #Buto Afegir Alumne
        afegir = ttk.Button(frame,text = 'Afegir',command=self.addAlumne)
        afegir.grid(row=4,columnspan=2,sticky=W+E)
        #Missatges Error
        self.missatge = Label(text="",fg="red")
        self.missatge.grid(row =5,column=0,columnspan=2,sticky=W+E)
        #Taula
        self.tree = ttk.Treeview(height=10,columns=('Nom','Cognoms','Data'))
        self.tree.grid(row=8,column=0,columnspan=2)
        self.tree.heading("Nom",text="Nom",anchor=W)
        self.tree.heading("Cognoms",text="Cognoms",anchor=W)
        self.tree.heading("Data",text="Data Naixement",anchor=W)
        self.tree.column("#0", stretch=NO,  minwidth=0, width=0)
        #Llista despegable
        self.llista_despegable = ttk.Combobox(state = 'readonly')
        self.llista_despegable.grid(row = 7, column = 0, sticky = W)
        columnes = ['Id', 'Nom', 'Cognoms', 'DataNaixement']
        self.llista_despegable['values'] = columnes
        self.llista_despegable.set(" ")
        #Input per filtrar
        self.recerca = Entry(width = 35)
        self.recerca.grid(row = 7, column = 0, sticky = E)
        #Buidar Entry's
        ttk.Button(text = "Buidar dades", command = lambda:self.buidar_Entrys(self.Nom, self.Cognoms, self.DataNaixement)).grid(row=1,column=1, sticky = E)
        #Botons filtres
        ttk.Button(text = "🔍 Filtrar", command = self.Filtrar).grid(row=7, column = 1,sticky = W)
        ttk.Button(text = "Treure Filtre", command = self.TreureFiltre).grid(row=7, column = 1,sticky = E)
        #Botons per exportar
        ttk.Button(text = "📊 Exportar a Excel",command=self.guardaExcel).grid(row=6,column=0,sticky=W+E)
        ttk.Button(text = "📄 Exportar a Pdf",command=self.guardaPdf).grid(row=6,column=1,sticky=W+E)
        #Esborrar Alumne
        ttk.Button(text = "🗑️",command=lambda:self.eliminaAlumne(self.missatge)).grid(row=9,column=0,sticky=W+E)
        #Modificar Alumne
        ttk.Button(text = "⚙️",command=lambda:self.modificaAlumne(self.missatge)).grid(row=9,column=1,sticky=W+E)
        #Actualizacio de les dades
        self.carregaAlumnes()

    def dadesCorrectes(self, nom, cognoms, datanaixement, missatge):
        if re.match('^[^\d]*$', nom) and re.match('^[^\d]*$', cognoms):
            try:
                data = datetime.strptime(datanaixement, '%d/%m/%Y')
                missatge["text"]=""
                return True
            except ValueError:
                missatge["text"] = "La data es incorrecte" 
                return False
        else:
            missatge["text"] = "El nom o cognom es incorrecte"
            return False
        
    def addAlumne(self):
        try:
            self.missatge['text'] = ""
            if self.dadesCorrectes(self.Nom.get(),self.Cognoms.get(),self.DataNaixement.get(),self.missatge):
                #Agrega un 0 al dia o mes si no te una longitud de 2 digits
                data = self.DataNaixement.get()
                data = data.split("/")
                data_amb_ceros = []
                for numero in range(0,2):
                    data_amb_ceros.append(data[numero].zfill(2))
                data_amb_ceros.append(data[2])
                self.connexio.insertAlumne(self.Nom.get().lower(),self.Cognoms.get().lower(),"/".join(data_amb_ceros))
                self.carregaAlumnes()
                self.missatge['text'] = "S'ha afegit l'alumne {} correctament".format(self.Nom.get())
                self.buidar_Entrys(self.Nom, self.Cognoms, self.DataNaixement)
        except:
            self.missatge['text'] = "No s'ha pogut afegir l'alumne degut a algun error"

    def buidar_Entrys(self,nom,cognoms,data_naixement):
        nom.delete(0,END)
        cognoms.delete(0,END)
        data_naixement.delete(0,END) 

    def buidarTree(self):
        for fila in self.tree.get_children():
            self.tree.delete(fila)

    def carregaAlumnes(self):
        self.missatge['text'] = ''
        self.buidarTree()
        alumnes = self.connexio.getAlumnes()
        print(alumnes)
        for a in alumnes:
            self.tree.insert("",0,text=a[0],values=a[1:])
    
    def eliminaAlumne(self, missatge):
        try:
            pos = self.tree.selection()
        except:
            missatge["text"] = "Has de seleccionar un element"
        try:
            idAlumne = self.tree.item(pos)["text"]
            self.connexio.removeAlumne(idAlumne)
            self.carregaAlumnes()
            missatge["text"]="S'ha eliminat l'alumne correctament"
        except:
            missatge["text"] = "No s'ha eliminat l'alumne degut a un error"

    def modificaAlumne(self, missatge):
        missatge['text'] = ""
        try:
            registre = self.tree.item(self.tree.selection())
        except IndexError:
            missatge['text'] = "Has de seleccionar un element"
        #Extraccio de les dades per modificar
        idAlumne = registre["text"]
        nom = registre['values'][0]
        cognoms = registre['values'][1]
        data_naixement = registre['values'][2]
        #Finestra per modificar
        self.finestra_modificar = Toplevel()
        self.finestra_modificar.title("Editar Alumne")
        self.finestra_modificar.geometry("250x150")
        #Id
        Label(self.finestra_modificar, text = 'Id:').grid(row = 0, column = 1, sticky = W)
        Entry(self.finestra_modificar, textvariable = StringVar(self.finestra_modificar, value = idAlumne), state = 'readonly').grid(row = 0, column = 2)
        #Input Nom
        Label(self.finestra_modificar, text = 'Nom:').grid(row = 1, column = 1, sticky = W)
        nom_modificat = Entry(self.finestra_modificar, textvariable = StringVar(self.finestra_modificar, value = nom))
        nom_modificat.grid(row = 1, column = 2)
        #Input Cognoms
        Label(self.finestra_modificar, text = 'Cognoms:').grid(row = 2, column = 1, sticky = W)
        cognoms_modificat = Entry(self.finestra_modificar, textvariable = StringVar(self.finestra_modificar, value = cognoms))
        cognoms_modificat.grid(row = 2, column = 2)
        #Input Data de Naixement
        Label(self.finestra_modificar, text = 'Data naixement:').grid(row = 3, column = 1, sticky = W)
        naixement_modificat = Entry(self.finestra_modificar, textvariable = StringVar(self.finestra_modificar, value = data_naixement))
        naixement_modificat.grid(row = 3, column = 2)
        #Missatge Error
        missatge1 = Label(self.finestra_modificar, text="", fg="red")
        missatge1.grid(row = 5, column = 1, columnspan = 2, sticky = W+E)
        #Buto per actualitzar les dades
        Button(self.finestra_modificar, text = 'Actualitzar', command = lambda: self.Actualitzar(idAlumne, nom_modificat.get(), cognoms_modificat.get(), naixement_modificat.get(), missatge1)).grid(row = 4, column = 2, sticky = W)
        self.finestra_modificar.mainloop()
    
    def Actualitzar(self, id, nom, cognoms, data_naixement, missatge):
            self.missatge['text'] = ''
            if self.dadesCorrectes(nom, cognoms,data_naixement, missatge):
                try:
                    query = f"UPDATE Alumnes SET Nom = '{nom}', Cognoms = '{cognoms}', DataNaixement = '{data_naixement}' WHERE Id = {id}"
                    self.connexio.executarQuery(query)
                    self.finestra_modificar.destroy()
                    self.carregaAlumnes()
                    self.missatge['text'] = 'Alumne {} actualitzat correctament'.format(nom)
                except:
                    self.missatge['text'] = "El registre del alumne no s'ha pogut actualitzar"

    def guardarDades(self, Id, Nom, Cognoms, DataNaixement):
        self.missatge['text'] = ''
        try:
            for dada in self.tree.get_children():
                Id.append(self.tree.item(dada)['text'])
                Nom.append(self.tree.item(dada)['values'][0])
                Cognoms.append(self.tree.item(dada)['values'][1])
                DataNaixement.append(self.tree.item(dada)['values'][2])
        except:
            self.missatge["text"] = "Error al guardar les dades"

    def guardaExcel(self):
        self.missatge['text'] = ''
        Id, Nom, Cognoms, DataNaixement = [],[],[],[]
        try:
            self.guardarDades(Id, Nom, Cognoms, DataNaixement)
            taula = {'Nom':Nom, 'Cognoms':Cognoms, 'Data_Naixement':DataNaixement}
            df = pd.DataFrame(taula, columns= ['Nom', 'Cognoms', 'Data_Naixement'], index = Id).rename_axis('Id')
            df.to_excel((f'Dades.xlsx'))
            self.missatge['text'] = 'Dades exportades amb exit!'
        except:
            self.missatge['text'] = "No s'ha pogut exportar a causa d'un error"

    def guardaPdf(self):
        self.missatge['text'] = ''
        Id, Nom, Cognoms, DataNaixement = [],[],[],[]
        try:
            self.guardarDades(Id, Nom, Cognoms, DataNaixement)
            taula = {'Id':Id, 'Nom':Nom, 'Cognoms':Cognoms, 'Data_Naixement':DataNaixement}
            fig, ax = plt.subplots()
            ax.axis('off')
            ax.axis('tight')
            df = pd.DataFrame(taula, columns= ['Id', 'Nom', 'Cognoms', 'Data_Naixement'], index = Id).rename_axis('Id')
            ax.table(cellText=df.values, colLabels=df.columns, loc='center', cellLoc = 'left')
            fig.tight_layout()
            plt.savefig('Dades.pdf')
            self.missatge['text'] = 'Dades exportades amb exit!'
        except:
            self.missatge['text'] = "No s'ha pogut exportar a causa d'un error"

    def Filtrar(self):
        self.missatge['text'] = ''
        self.buidarTree()
        alumnes = self.connexio.findAlumnes(self.llista_despegable.get(),self.recerca.get().lower())
        for a in alumnes:
            self.tree.insert("",0,text=a[0],values=a[1:])
        if len(alumnes) == 0:
            self.missatge['text'] = "No hi ha ningun resultat al filtre"    
    def TreureFiltre(self):
        self.missatge['text'] = ''
        self.llista_despegable.set(" ")
        self.recerca.delete(0, END)
        self.carregaAlumnes()

if __name__ == '__main__':
    finestra = Tk()
    appAlumnes(finestra,'dbInstitut.db')
    finestra.mainloop()
