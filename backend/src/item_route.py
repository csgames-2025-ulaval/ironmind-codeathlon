import mariadb
import re
import requests
from fastapi import APIRouter

from src.item import Item

router = APIRouter()
sql_connection = mariadb.connect(host='db', port=3306, user="username", password="password", database="database")

emailRegex = r'\b[A-Za-z0-9._%+-]+@ulaval.ca\b'
idUser = -1

@router.get("/")
def index():
    return {"message": "Hello, World!"}


@router.get("/items")
def get_item():
    with sql_connection.cursor() as cursor:
        query = "SELECT name,description,price FROM items"
        cursor.execute(query)
        results = cursor.fetchall()
        return [Item(name=result[0], description=result[1], price=result[2]) for result in results]


@router.post("/item")
def add_item(item: Item):
    with sql_connection.cursor() as cursor:
        sql = "INSERT INTO items (name, description, price) VALUES (%s, %s, %s)"
        cursor.execute(sql, (item.name, item.description, item.price))
        sql_connection.commit()

# Route qui permet d'obtenir dans une liste de String tout les programmes présents dans la BD
@router.get("/programs")
def get_programs():
    with sql_connection.cursor() as cursor:
        query = "SELECT id, name FROM programs"
        cursor.execute(query)
        results = cursor.fetchall()
        return results

# Route qui permet d'obtenir dans une liste de String tout les sexes présents dans la BD
@router.get("/sexes")
def get_sexes():
    with sql_connection.cursor() as cursor:
        query = "SELECT id, name FROM sexes"
        cursor.execute(query)
        results = cursor.fetchall()
        return results

def accountInformationValid(firstName, lastName, sex, program, dateBirth, mail, password):
    if firstName == "" or lastName == "" or sex == "" or program == "" or dateBirth == "" or mail == "" or password == "":
        return False
    if not re.fullmatch(emailRegex, mail):
        return False
    if len(password) < 8 or False:
        return False

    return True

def connexionInformationValid(email, password):
    if email == "" or password == "":
        return False
    if not re.fullmatch(emailRegex, email):
        return False
    if len(password) < 8 or False:
        return False

    return True

def incrementIdUser():
    idUser += 1
    return idUser

#Genderize.io est payant avec une cle de api
def validateSexGenderize(name, gender):
    #Ne fonctionne pas pcq pour utiliser la cle API il faut payer
    #response = requests.get(f"https://api.genderize.io?name={name}&apikey=84027a78ea17bc90c23e76f78e0a4c35")
    response = requests.get(f"https://api.genderize.io/?name={name}")
    
    return response["gender"] == gender

def getGenderNumber(sex):
    if sex is "Male":
        return 0
    elif sex is "Female":
        return 1
    else:
        return 2

def getProgramNumber(program):
    if program is "IFT":
        return 0
    elif program is "GLO":
        return 1
    else:
        return 2

# Route qui permet cd créer un nouveau compte utilisateur avec les informations fournit si elles respectent les critères
@router.post("/account")
def add_account(firstName, lastName, sex, program, dateBirth, mail, password):
    with sql_connection.cursor() as cursor:
        sql = f"SELECT password FROM users WHERE password ={hash(password)}"
        cursor.execute(sql)
        if cursor.fetchall().isEmpty:
            if accountInformationValid(firstName, lastName, sex, program, dateBirth, mail, mdp):
                if sex is "Male" or sex is "Female":
                    if validateSexGenderize(firstName, sex):
                        sex = getGenderNumber(sex)
                        program = getProgramNumber(program)
                        sql = "INSERT INTO users (id, name, family_name, sexeId, programId, birthDate, email, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                        val = (incrementIdUser(), firstName, lastName, sex, program, dateBirth, mail,hash(password))
                else :
                    sql = "INSERT INTO users (id, name, family_name, sexeId, programId, birthDate, email, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                    val = (incrementIdUser(), firstName, lastName, sex, program, dateBirth, mail,hash(password))
            
    cursor.execute(sql, val)
    sql_connection.commit()
    results = cursor.fetchall()
    return results


# Route qui permet de se connecter en tant qu'utilisateur
@router.post("/connexion")
def add_account(email, password):
    if connexionInformationValid(firstName, lastName, sex, program, dateBirth, mail, mdp):
        return False
    with sql_connection.cursor() as cursor:
        sql = f"SELECT id FROM users WHERE password ={hash(password)}"
        cursor.execute(sql)
        if not cursor.fetchall().isEmpty:
            idUser = cursor.fetchone()
            return True
    return False


# Route qui permet de modifier les informations d'un compte utilisateur existant
@router.post("/modifyAccount")
def update_account(firstName, lastName, sex, program, dateBirth, mail, password):
    if idUser is not -1:
        with sql_connection.cursor() as cursor:
            sql = f"UPDATE users SET name = {firstName}, family_name = {lastName}, sexId = {sex}, programId = {program}, birthDate = {dateBirth}, email = {mail}, password = {password},  WHERE id = {idUser};"

# Route qui permet d'obtenir une liste de String qui contient tous les événements à venir
@router.get("/events")
def get_events():
    with sql_connection.cursor() as cursor:
        query = "SELECT id, section, price FROM events"  #TODO peut-être aussi ajouter une condition pour savoir si jamais l'événement ne s'est pas encore passé
        cursor.execute(query)
        results = cursor.fetchall()
        return results

@router.get("/reservations")
def get_reservations():
    if idUser is not -1:
        with sql_connection.cursor() as cursor:
            query = "SELECT id, seatId, eventId FROM reservations WHERE userId = {idUser}"
            cursor.execute(query)
            results = cursor.fetchall()
            return results

# Route qui permet d'obtenir la liste des billets qu'un utilisateur a réservé
@router.get("/tickets")
def get_tickets():
    if idUser is not -1:
        with sql_connection.cursor() as cursor:
            query = f"SELECT id, section, price FROM events WHERE userId = {idUser}"  #TODO: remplacer y par les champs de la table et x par le nom de la table et ajouter une condition pour seulement obtenir les billets de l'utilisateur courant
            cursor.execute(query)
            results = cursor.fetchall()
            return results #TODO: formater la réponse de la BD en fonction du nombre de champs vers un objet python

