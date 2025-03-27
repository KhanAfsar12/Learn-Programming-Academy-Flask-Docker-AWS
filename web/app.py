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
        users.update({
            "Username": username,
        },{
            "$set": {
                "Tokens": current_tokens-1
            }
        })
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



# class Store(Resource):
#     def post(self):
#         postedData = request.get_json()
#         print(postedData)
#         print("-------------------------------------------------------------------")
#         username = postedData['username']
#         password= postedData['password']
#         sentence = postedData['sentence']

#         correct_pw = verifyPw(username, password)

#         if not correct_pw:
#             retJson = {
#                 'status': 302
#             }        
#             return jsonify(retJson)
        
#         num_tokens = countTokens(username)
#         if num_tokens <= 0:
#             retJson = {
#                 "status": 301
#             }
#             return jsonify(retJson)
        
#         users.update_one({
#             "Username": username
#         },
#         {
#             "$set": {
#                 "Sentence": sentence,
#                 "Tokens": num_tokens-1
#             }
#         })

#         retJson = {
#                 "status": 301,
#                 "msg": "Sentence saved successfully"
#             }
#         return jsonify(retJson)



# class Get(Resource):
#     def post(self):
#         postedData = request.get_json()

#         username = postedData['username']
#         password= postedData['password']

#         correct_pw = verifyPw(username, password)

#         if not correct_pw:
#             retJson = {
#                 'status': 302
#             }        
#             return jsonify(retJson)
        
#         num_tokens = countTokens(username)
#         if num_tokens <= 0:
#             retJson = {
#                 "status": 301
#             }
#             return jsonify(retJson)
        

#         users.update_one({
#             "Username": username
#         },
#         {
#             "$set": {
#                 "Tokens": num_tokens-1
#             }
#         })
        
#         sentence = users.find({
#             "Username": username
#         })[0]['Sentence']

#         retJson = {
#             "status": 200,
#             "sentence": sentence
#         }
#         return jsonify(retJson)


# api.add_resource(Store, '/store')
api.add_resource(Register, '/register')
# api.add_resource(Get, '/get')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)