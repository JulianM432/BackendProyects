# uvicorn users:app --reload
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class User(BaseModel):
    nombre: str
    apellido: str
    dni: int
    edad: int


users = [
    User(nombre="John", apellido="Gomez", dni=12212121, edad=22),
    User(nombre="Maria", apellido="Moreira", dni=23323232, edad=55),
    User(nombre="Jose", apellido="Fernandez", dni=43343434, edad=44),
]


@app.get("/")
async def root():
    return {"message": "Hace algo"}


@app.get("/users/")
async def getUsers():
    return users


@app.get("/users/{name}")
async def getUser(name: str):
    for unUser in users:
        if unUser.nombre == name:
            return unUser
    raise HTTPException(status_code=404, detail="User not found")


@app.post("/users/")
async def createUser(unUser: User):
    try:
        if type(searchUserByDNI(unUser.dni)) == User:  # Si devuelve un User, existe
            return {"Error": "El usuario existe"}
        else:
            users.append(unUser)
            return unUser
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e).split("\n"))


@app.put("/users/")
async def updateUser(unUser: User):
    try:
        user = searchUserByDNI(userID=unUser.dni)  # User a reemplazar
        if type(user) == User:
            users[users.index(user)] = unUser
            return {"message": "User updated!"}
    except Exception as e:
        raise Exception(str(e).split("\n"))


@app.delete("/users/{dni}")
async def deleteUser(dni: int):
    try:
        userToDelete = searchUserByDNI(userID=dni)
        users.remove(userToDelete)
        return {"message": "User deleted!"}
    except Exception as e:
        raise HTTPException(status_code=405, detail=str(e).split("\n"))


def searchUserByDNI(userID: int):
    for user in users:
        if user.dni == userID:
            return user
