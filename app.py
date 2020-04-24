from bson.objectid import ObjectId
from bson.json_util import dumps
from flask import Flask, abort, request, jsonify, g, url_for
from flask_mongoengine import MongoEngine
from mongoengine import *
from mongoengine import connect
from mongoengine.connection import disconnect
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'very secretpassword'
app.config['MONGODB_DB'] = 'user_service'
db = MongoEngine(app)
connect('db',host='localhost', port=27017,alias='userauthdb')

auth = HTTPBasicAuth()


class UserDetails(Document):

    username = StringField(index=True)
    password_hash = StringField()
    mobileno=IntField()
    aadhaarno=IntField()
    email=EmailField()
    address=StringField()

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = User.objects.get(data['id'])
        return user

disconnect(alias='userauthdb')


@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.objects.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True

@app.route('/adduser', methods=['POST'])
def new_user():
    userid=0
    username = request.json["username"]
    password = request.json['password']
    mobileno = request.json['mobileno']
    aadhaarno = request.json['aadhaarno']
    email = request.json['email']
    address = request.json['address']
    if username and password and mobileno and aadhaarno and email and address and request.method == 'POST':

        existinguser = UserDetails.objects.filter(username=username).count()

        if existinguser==0:

            user = UserDetails.objects.create(username=username,mobileno=mobileno, aadhaarno=aadhaarno,
                                  email=email, address=address)
            result=user.save(commit=False)
            result.hash_password(password)
            result.save()
            userid=result._id
            print(userid)
        return (jsonify({'username': username,'mobileno': mobileno, 'aadhaarno': aadhaarno,
              'email': email}), 201,
            {'Location': url_for('get_user', id=userid, _external=True)})
    else:
            abort(400)  # missing arguments


@app.route('/users/<int:id>')
def get_user(id):
    user = User.objects.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})

@app.route('/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})


@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user.username})

# @app.route('/adduser',methods=['POST'])
# def add_user():
#     addusers=mongo.db.addusers
#     name = request.json['name']
#     mobileno = request.json['mobileno']
#     aadhaarno=request.json['aadhaarno']
#     email = request.json['email']
#     address = request.json['address']
#
#     if name and mobileno and aadhaarno and email and address and request.method=='POST':
#         userinsert_id=addusers.insert({'name':name, 'mobileno':mobileno,'aadhaarno':aadhaarno,
#                                    'email':email,'address':address})
#         new_user = addusers.find_one({'_id': userinsert_id})
#         output = {'name': new_user['name'], 'mobileno': new_user['mobileno'], 'aadhaarno': new_user['aadhaarno'],'email': new_user['email'],
#                   'address': new_user['address']}
#         return jsonify({'result': output})

@app.route('/update/<id>', methods=['PUT'])
@auth.login_required
def update_user(id):
    name = request.json['name']
    email = request.json['email']
    mobileno = request.json['mobileno']
    aadhaarno = request.json['aadhaarno']
    address = request.json['address']

    # validate the received values
    if name and email and mobileno and aadhaarno and address and request.method == 'PUT':
        # save edits
        User.objects.update_one({'_id': ObjectId(id)}, {'$set': {'name': name, 'email':email, 'mobileno': mobileno,
                                                               'aadhaarno': aadhaarno,'address': address}})
        resp = jsonify('User updated successfully!')
        return resp
    else:
        return not_found()

@app.route('/delete/<id>', methods=['DELETE'])
@auth.login_required
def delete_user(id):
    User.objects.delete_one({'_id': ObjectId(id)})
    resp = jsonify('User deleted successfully!')
    resp.status_code = 200
    return resp

@app.route('/users', methods=['GET'])
@auth.login_required
def users_list():
    resp=User.objects.find()
    resp=dumps(resp)
    return resp

@app.route('/users/<name>', methods=['GET'])
@auth.login_required
def userslist(name):
    resp=User.objects.find_one({'name':name})
    resp=dumps(resp)
    return resp

@app.route('/oneuser/<id>', methods=['GET'])
@auth.login_required
def user_based_id(id):
    resp=User.objects.find_one({'_id': ObjectId(id)})
    resp=dumps(resp)
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5001,debug=True)