from flask import Flask, request
from flask_pymongo import PyMongo
from pymongo import MongoClient
from bson.objectid import ObjectId
from secres import db_username, db_pswd
from werkzeug import exceptions
import json
from bson import json_util

app = Flask(__name__)

uri = "mongodb+srv://"+db_username+":"+db_pswd+"@cluster0.wzkev.mongodb.net/API-Noticias?retryWrites=true&w=majority"
app.config['MONGO_URI'] = uri
client = MongoClient(uri)
mongo = PyMongo(app)

def createNewAutor(dados):
    autores = client.get_database("API-Noticias").Autores
    new_autor = {
        'nome': dados['autor'],
        'empresa': dados['empresa']
    }
    insert_query = autores.insert_one(new_autor)
    autor_id = insert_query.inserted_id
    return autor_id

def checkIfAutorExists(autor):
    autores = client.get_database("API-Noticias").Autores
    autor_exists = list(autores.find({"nome": autor}))
    return autor_exists

def return405():
    message = {
        "status": "error",
        "code": 405,
        "data": "",
        "message": "Method not allowed"
    }

    return json.dumps(message)

def return401(message):
    message = {
        "status": "error",
        "code": 401,
        "data": "",
        "message": message
    }

    return json.dumps(message)

def returnSuccess(message, data):
    message = {
        "status": "success",
        "code": 200,
        "data": data,
        "message": message
    }
    return json.dumps(message, indent=4, default=json_util.default, ensure_ascii=False)

@app.route("/search", methods=['GET'])
def queryForNoticia():
    dados = request.args
    query_type = dados['query_type']
    param = dados['termo']
    db = client.get_database("API-Noticias")
    noticias = db.Noticias
    query_param = ".*"+param+"*."
    if query_type == 'texto':
        noticias_list = list(noticias.find({"texto": {"$regex": query_param}}))
    elif query_type == 'titulo':
        noticias_list = list(noticias.find({"titulo": {"$regex": query_param}}))
    elif query_type == 'autor':
        autores = db.Autores
        autor = list(autores.find({"nome" : {"$regex": query_param}}))
        if len(autor) > 1:
            noticias_list = list(noticias.find({"autor": {"$regex": query_param}}))
        elif len(autor) == 1:
            id = autor[0]['_id']
            noticias_list = list(noticias.find({"autor" : id}))
        else:
            noticias_list = {}
    else:
        return return401("query_type nao permitido")

    return returnSuccess("Noticias econtradas", noticias_list)

@app.route("/publish", methods= ['POST'])
def publishNewNoticia():
    if request.method == 'POST':

        dados = json.loads(request.data.decode('utf8'))
        if 'titulo' not in dados:
            return return401("Campo 'titulo' nao pode estar em branco")
        if 'autor' not in dados:
            return return401("Campo 'autor' nao pode estar em branco")
        if 'texto' not in dados:
            return return401("Campo 'texto' nao pode estar em branco")

        db = client.get_database("API-Noticias")
        noticias = db.Noticias
        autores = db.Autores

        #procurar se autor já existe
        autor_exists = checkIfAutorExists(dados['autor'])
        if not autor_exists:
            #se for um autor novo, o usuario deve enviar a empresa para que esse novo autor seja cadastrado
            if not 'empresa' in dados:
                return return401("Campo 'empresa' nao pode estar em branco para cadastrar uma noticia de um novo autor")
            #se não existir autor, criar um novo autor na tabela Autores e armazenar seu id
            autor_id = createNewAutor(dados)

        else:
            autor_id = autor_exists[0]['_id']

        new_noticia = {
            'titulo': dados['titulo'],
            'autor': autor_id,
            'texto': dados['texto']
        }

        noticias.insert_one(new_noticia)
        return returnSuccess("Noticia publicada", new_noticia)
    else:
        return return405()

@app.route("/update", methods= ['POST'])
def updateNoticia():
    if request.method == 'POST':
        db = client.get_database("API-Noticias")
        noticias = db.Noticias

        dados = json.loads(request.data.decode('utf8'))
        try:
            id = dados['id']
        except KeyError:
            return return401("O id da noticia a ser atualizada deve ser enviado corretamente")

        if 'titulo' not in dados and 'texto' not in dados and "autor" not in dados:
            return return401("Pelo menos um campo deve ser enviado")

        #buscar dados atuais da noticia
        try:
            noticia = list(noticias.find({"_id": ObjectId(id)}))[0]
        except IndexError:
            return return401("Nao existe noticia com o ID enviado")

        if 'titulo' in dados:
            noticia['titulo'] = dados['titulo']

        if 'autor' in dados:
            # procurar se autor já existe
            autor_exists = checkIfAutorExists(dados['autor'])
            if not autor_exists:
                # se for um autor novo, o usuario deve enviar a empresa para que esse novo autor seja cadastrado
                if not 'empresa' in dados:
                    return return401("Campo 'empresa' nao pode estar em branco para cadastrar uma noticia de um novo autor")
                # se não existir autor, criar um novo autor na tabela Autores e armazenar seu id
                autor_id = createNewAutor(dados)
                noticia['autor'] = autor_id
            else:
                autor_id = autor_exists[0]['_id']
                noticia['autor'] = autor_id
        if 'texto' in dados:
            noticia['texto'] = dados['texto']

        noticias.replace_one({'_id': ObjectId(id)}, noticia, True)
        return returnSuccess("Noticia atualizada", noticia)

    else:
        return return405()

@app.route("/delete", methods= ['POST'])
def delNoticia():
    if request.method == 'POST':
        dados = json.loads(request.data.decode('utf8'))
        id_noticia = dados['id']
        db = client.get_database("API-Noticias")
        noticias = db.Noticias
        noticias.delete_one({"_id": ObjectId(id_noticia)})
        return returnSuccess("Noticia deletada", id_noticia)

    else:
        return return405()


if __name__  == "__main__":
    app.run(debug=True)