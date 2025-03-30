from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import spacy

app = Flask(__name__)

api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.SentencesDatabase
users = db["Users"]



class Register(Resource):
    def post(self):
        postedData = request.get_json()
        print(postedData)

        username = postedData['username']
        password= postedData['password']

        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        users.insert_one({
            "Username": username,
            "Password": hashed_pw,
            "Sentence": "",
            "Tokens": 6
        })
        retJson = {
            'status': 200,
            'msg': "You have successfully signed up for the API."
        }
        return jsonify(retJson)
    

def UserExist(username):
    if users.find_one({"Username": username}):
        return True
    return False

class Detect(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData['username']
        password = postedData['password']
        text1 = postedData['text1']
        text2 = postedData['text2']

        if not UserExist(username):
            retJson = {
                "status": 301,
                "msg": "Invalid Username"
            }
            return jsonify(retJson)
        
        correct_pw = verifyPw(username, password)
        if not correct_pw:
            retJson = {
                'status': 302
            }        
            return jsonify(retJson)
        
        num_tokens = countTokens(username)
        if num_tokens <= 0:
            retJson = {
                "status": 301,
                "msg": "You are out of tokens"
            }
            return jsonify(retJson)
        
        nlp = spacy.load('en_core_web_sm')
        text1 = nlp('text1')
        text2 = nlp('text2')

        ratio = text1.similarity(text2)

        retJson = {
            "status": 200,
            "similarity": ratio,
            "msg": "Similarity score calculated successfully"
        }
        current_tokens = countTokens(username)
        users.update_one({
            "Username": username,
        },{
            "$set": {
                "Tokens": current_tokens-1
            }
        })
        return jsonify(retJson)
    




class Refill(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["admin_pw"]
        refill_amount = postedData["refill"]

        if not UserExist(username):
            retJson = {
                "status": 301,
                "msg": "Invalid Username"
            }
            return jsonify(retJson)

        correct_pw = "abc123"
        if not password == correct_pw:
            retJson = {
                "status": 304,
                "msg": "Invalid admin password"
            }
            return jsonify(retJson)
        
        current_tokens = countTokens(username)
        users.update({
            "Username": username
        },{
            "$set":{
                "Tokens": refill_amount+current_tokens
            }
        })
        retJson = {
            "status": 200,
            "msg": "Refilled successfully"
        }
        return jsonify(retJson)




def verifyPw(username, password):

    if not UserExist(username):
        return False
    hashed_pw = users.find({
        "Username": username
    })[0]['Password']

    if bcrypt.hashpw(password.encode('utf-8'), hashed_pw) == hashed_pw:
        return True
    else:
        return False
    
def countTokens(username):
    tokens = users.find({
        "Username": username
    })[0]['Tokens']
    return tokens







api.add_resource(Register, '/register')
api.add_resource(Detect, '/det')
api.add_resource(Refill, '/refill')


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)