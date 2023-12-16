import csv
import random
import string
import unicodedata
import re

def comprobarCompteExisteix(compte):
    with open("usuaris.csv", "r") as usuaris: # Obrir l'arxiu CSV que conté els registres dels usuaris.
        reader = csv.DictReader(usuaris) # Crear un objecte DictReader a partir de l'arxiu CSV.
        for registre in reader: # Iterar sobre cada registre de l'arxiu CSV.
            if registre["usuari"] == compte: # Comprovar si el nom d'usuari existeix en el registre actual.
                return True
        return False

def generaCompte(alumne):
    aleatori = random.randint(100,999) # Generar un número aleatori de tres xifres.
    compte = (alumne["Nom"][0] + "." + alumne["Cognom1"] + str(aleatori)).replace(" ","").replace("l*l", "l").replace("n*n","n").lower() # Crear un nom d'usuari utilitzant el nom i 
                                                                                                                                         # el primer cognom de l'alumne, el número 
                                                                                                                                         # aleatori generat i unes certes substitucions 
                                                                                                                                         # de caràcters.
    compte_2 = unicodedata.normalize('NFKD', compte).encode('ascii', 'ignore').decode('ascii') # Eliminar qualsevol caràcter no ASCII del nom d'usuari generat.
    if re.search("^[a-z].[a-z]*\d{3}$", compte_2): 
        if comprobarCompteExisteix(compte_2): # Comprovem si el nom de compte ja existeix 
                                              # en el fitxer CSV d'usuaris torna a generar 
                                              # una compte nova.
            generaCompte(alumne)
        else:
            return compte_2

def generaPassword(longitud):
    if longitud < 8: # Assegurar-se que la longitud de la contrasenya sigui almenys 8 caràcters
        longitud = 8
    while True:
        # Definir els caràcters que s'utilitzaran per a generar la contrasenya
        letters = string.ascii_letters
        simbols = '()/^?¿[]{}\-=+*'
        numbers = '0123456789'
        tots = letters + simbols + numbers
        # Generar una contrasenya aleatòria utilitzant els caràcters definits
        password = "".join(random.choices(tots, k = longitud))
        # Comprovar que la contrasenya generada sigui segura
        while not (re.search(r"[A-Z]", password) 
                  and re.search(r"[a-z]", password) 
                  and re.search(r"[()\^?¿\[\]{}\-=+*]", password)):
            # Si la contrasenya generada no es segura, generar una nova contrasenya
            password = "".join(random.choices(tots, k = longitud))
        # Retornar la contrasenya generada si és segura
        return password

# Llista per guardar els grups
grups = []
with open("./alumnes.csv", "r") as alumnes:
    reader = csv.DictReader(alumnes, delimiter=";") # Crea un objecte DictReader i estableix el delimitador de camps en ";"
    for x in reader: # Itera per cada fila del arxiu CSV
        if x['Grup'] not in grups: # Si el grup no está en la llista de grups, s'ha afegeix dintre de la llista
            grups.append(x['Grup'])

# Generem un nou fitxer amb els comptes d'usuaris en format csv
with open("./usuaris.csv", "w", newline = "") as usuaris, \
     open("./crearComptes.ps1", "w", newline = "") as nousComptes, \
     open("./correus.csv", "w", newline = "") as nouscorreus, \
     open("./correugrups.csv", "w", newline = "") as nouscorreus_g:

    
    # Camps per a l'arxiu CSV de comptes d'usuari
    camps_usuari = ["usuari", "password"]
    writer_usuari = csv.DictWriter(usuaris, fieldnames = camps_usuari) # Obrim el escriptor amb format DictWriter
    writer_usuari.writeheader() # Escrigui la primera fila de l'arxiu CSV (els noms dels camps)
    
    # Itera per cada grup en la llista de grups
    for x in grups:
        # Genera un nou arxiu CSV per cad grup
        with open(x + '.csv', "w", newline = "") as grups:
            camps_grup = ["Grup", "Cognom1", "Cognom2", "Nom", "NomCompte", "Password"] # Camps per els arxius CSV dels grups
            writer_grup = csv.DictWriter(grups, fieldnames = camps_grup)
            writer_grup.writeheader() # Escrigui la primera fila de l'arxiu CSV (els noms dels camps)
    
    # Camps per a l'arxiu CSV dels correus electrònics       
    camps_email = ["Email Address", "First name", "Last Name", "Password", "Org Unit Path"]
    writer_email = csv.DictWriter(nouscorreus, fieldnames = camps_email) # Escrigui la primera fila de l'arxiu CSV (els noms dels camps)
    writer_email.writeheader()

    # Camps per el arxiu CSV de grups de correu
    camps_email_g = ["Group Email", "Member Email", "Member Role"]
    writer_email_g = csv.DictWriter(nouscorreus_g, fieldnames = camps_email_g) # Escrigui la primera fila de l'arxiu CSV (els noms dels camps)
    writer_email_g.writeheader()

    #Obrim el fitxer d'alumnes per consultar les seves dades
    with open("./alumnes.csv", "r") as alumnes:
        reader = csv.DictReader(alumnes, delimiter=";")#Indiquem el delimintardor de camps, per defecte es la coma.
        # Ordena els alumnes per cognom1, cognom2 i nom
        alumnes_ordenats = sorted(reader, key=lambda x: (x['Cognom1'][0], x['Cognom2'][0], x['Nom'][0]))
        for alumne in alumnes_ordenats:
            # Nom d'usuari
            nomCompte = generaCompte(alumne)
            # Contrasenya
            password = generaPassword(10)
            # Nom alumne
            nom = alumne["Nom"]
            # Cognoms alumne
            cognoms = f'{alumne["Cognom1"]} {alumne["Cognom2"]}'
            # Grup
            grup = alumne["Grup"]
            # Data Nauxement
            data_n = alumne["DataNaixement"]
            # Contrasenya per les comandes de Powershell
            securePassword = f'ConvertTo-SecureString -String "{password}" -AsPlainText -Force'                                 
            # Comanda de creació del usuari amb Powershell
            crearCompteAD = f'New-ADuser -Name "{nomCompte}" `\n\
           -GivenName "{nom}" `\n\
           -SurName "{cognoms}" `\n\
           -DisplayName "{cognoms + ", " + nom}" `\n\
           -AccountPassword ({securePassword}) `\n\
           -Path "{f"ou={grup.lower()}, ou=alumnes, dc=sapalomera, dc=net"}" `\n\
           -Description "{data_n}" `\n\
           -Enabled $true \n\n' 
            nousComptes.write(crearCompteAD)
            nomcorreu = nomCompte + '@sapalomera.cat'

            writer_email_g.writerow({'Group Email':"g" + grup.lower() + "@sapalomera.cat", 'Member Email': nomcorreu, 'Member Role': "member"})
            writer_email.writerow({'Email Address': nomcorreu, 'First name': nom, 'Last Name': cognoms, 'Password': password, 'Org Unit Path': f'/alumnes/{grup.lower()}'})
            writer_usuari.writerow({'usuari':nomCompte, 'password':password})
            with open(grup + '.csv', "a", newline="") as grups_1:
                writer_grup = csv.DictWriter(grups_1, fieldnames = camps_grup)
                writer_grup.writerow({'Grup':grup, 'Cognom1':alumne["Cognom1"], 'Cognom2':alumne["Cognom2"], 'Nom': nom, 'NomCompte':nomCompte, 'Password': password})
