
from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'user_service'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/user_service'
mongo = PyMongo(app)

# app.config['MONGODB_SETTINGS'] = {
#     'host': 'mongodb://localhost/user_service',
#     'connect': False,
# }
# db = MongoEngine(app)
#
# import mongoengine as  me

# class user(me.Document):
#     # id = me.IntField(primary_key=True)
#     name = me.StringField(max_length=50)
#     mobileno = me.IntField()
#     aadhaarno=me.IntField()
#     email=me.EmailField(max_length=20)
#     address=me.StringField()

@app.route('/adduser',methods=['POST'])
def add_user():
    addusers=mongo.db.addusers
    name = request.json['name']
    mobileno = request.json['mobileno']
    aadhaarno=request.json['aadhaarno']
    email = request.json['email']
    address = request.json['address']

    if name and mobileno and aadhaarno and email and address and request.method=='POST':
        userinsert_id=addusers.insert({'name':name, 'mobileno':mobileno,'aadhaarno':aadhaarno,
                                   'email':email,'address':address})
        new_user = addusers.find_one({'_id': userinsert_id})
        output = {'name': new_user['name'], 'mobileno': new_user['mobileno'], 'aadhaarno': new_user['aadhaarno'],'email': new_user['email'],
                  'address': new_user['address']}
        return jsonify({'result': output})

@app.route('/update/<id>', methods=['PUT'])
def update_user(id):
    updateusers = mongo.db.addusers
    name = request.json['name']
    email = request.json['email']
    mobileno = request.json['mobileno']
    aadhaarno = request.json['aadhaarno']
    address = request.json['address']

    # validate the received values
    if name and email and mobileno and aadhaarno and address and request.method == 'PUT':
        # save edits
        updateusers.update_one({'_id': ObjectId(id)}, {'$set': {'name': name, 'email':email, 'mobileno': mobileno,
                                                               'aadhaarno': aadhaarno,'address': address}})
        resp = jsonify('User updated successfully!')
        return resp
    else:
        return not_found()

@app.route('/delete/<id>', methods=['DELETE'])
def delete_user(id):
    deleteusers = mongo.db.addusers
    deleteusers.delete_one({'_id': ObjectId(id)})
    resp = jsonify('User deleted successfully!')
    resp.status_code = 200
    return resp

# from flask import Flask
# app = Flask(__name__)
#
#
# @app.route('/')
# def hello():
#     return "Hello World!"

if __name__ == '__main__':
    app.run(debug=True)