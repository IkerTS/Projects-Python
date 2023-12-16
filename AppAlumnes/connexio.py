import sqlite3
class Connexio:
    def __init__(self,bd):
        self.connexio = sqlite3.connect(bd)
        self.bd_name = bd
    
    def insertAlumne(self,nom,cognoms,datanaixement):
        cursor = self.connexio.cursor()
        sql = f"INSERT INTO Alumnes (Nom,Cognoms,DataNaixement) VALUES('{nom}','{cognoms}','{datanaixement}')"
        cursor.execute(sql)
        self.connexio.commit()
        cursor.close()
    
    def getAlumnes(self):
        cur = self.connexio.cursor()
        sql = "SELECT * FROM Alumnes" 
        cur.execute(sql)
        alumnes = cur.fetchall()
        return alumnes

    def findAlumnes(self, columna, valor):
        cur = self.connexio.cursor()
        sql = f"SELECT * FROM Alumnes WHERE LOWER({columna}) = LOWER('{valor}')"
        cur.execute(sql)
        alumnes= cur.fetchall()
        cur.close()     
        return alumnes

    def removeAlumne(self,id):
        cur = self.connexio.cursor()
        sql=f"DELETE FROM Alumnes WHERE Id = {id}"
        print(sql)
        cur.execute(sql)
        self.connexio.commit()    
        cur.close()
        
    def executarQuery(self, query):
        with sqlite3.connect(self.bd_name) as conn:
            cursor = conn.cursor()
            result = cursor.execute(query)
            conn.commit()
        return result