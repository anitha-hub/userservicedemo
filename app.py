from bson.objectid import ObjectId
from bson.json_util import dumps
from flask import Flask, abort, request, jsonify, url_for, make_response
from flask_mongoengine import MongoEngine
from mongoengine import *
from mongoengine import connect
from mongoengine.connection import disconnect
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import uuid
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Th1s1ss3cr3t'
app.config['MONGODB_DB'] = 'user_service'
db = MongoEngine(app)
connect('db', host='localhost', port=27017, alias='userauthdb')


class UserDetails(Document):
    username = StringField(index=True)
    password = StringField()
    mobileno = IntField()
    aadhaarno = IntField()
    email = EmailField()
    address = StringField()
    public_id = StringField()

    def to_json(self):
        return {
            "_id": str(self.pk),
            "username": self.username,
            "password": self.password,
            "mobileno": self.mobileno,
            "email": self.email,
            "aadhaarno": self.aadhaarno,
            "address": self.address,
            "public_id": self.public_id
        }


disconnect(alias='userauthdb')


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        # if 'x-access-tokens' in request.headers:
        #     token = request.headers['x-access-tokens']
        if 'X-Access-Token' in request.headers:
            token = request.headers['X-Access-Token']
        if not token:
            return jsonify({'message': 'a valid token is missing'})

        data=jwt.decode(token, app.config['SECRET_KEY'])
        current_user = UserDetails.objects.filter(public_id=data['public_id']).first()
        return f(current_user, *args, **kwargs)

    return decorator


@app.route('/register', methods=['POST'])
def signup_user():
    username = request.json["username"]
    password = request.json['password']
    mobileno = request.json['mobileno']
    aadhaarno = request.json['aadhaarno']
    email = request.json['email']
    address = request.json['address']
    if username and password and mobileno and aadhaarno and email and address and request.method == 'POST':

        existinguser = UserDetails.objects.filter(username=username).count()

        if existinguser == 0:
            hashed_password = generate_password_hash(password, method='sha256')
            user = UserDetails.objects.create(username=username, password=hashed_password, mobileno=mobileno,
                                              aadhaarno=aadhaarno,
                                              email=email, address=address, public_id=str(uuid.uuid4()))
            result = user.save(commit=False)
            result.save()
            return (jsonify({'username': username, 'mobileno': mobileno, 'aadhaarno': aadhaarno,
                         'email': email, 'address': address, 'password': hashed_password},
                        {'message': 'registered successfully'}), 201,
                {'Location': url_for('login_user', _external=True)})
    else:
        abort(400)  # missing arguments


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    auth = request.authorization
    # auth=requests.get("http://127.0.0.1:5000/login")
    if not auth or not auth.username or not auth.password:
        return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})

    user = UserDetails.objects.filter(username=auth.username).first()
    if check_password_hash(user.password, auth.password):
            token = jwt.encode(
                {'public_id': user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
                app.config['SECRET_KEY'])
            return jsonify({'token': token.decode('UTF-8')})

    return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})


@app.route('/update', methods=['PUT'])
@token_required
def update_user(current_user):
    username = request.json['username']
    email = request.json['email']
    mobileno = request.json['mobileno']
    aadhaarno = request.json['aadhaarno']
    address = request.json['address']
    password=request.json['password']

    # validate the received values
    if username and email and mobileno and aadhaarno and address and request.method == 'PUT':
        # save edits
        UserDetails.objects.filter(id=current_user.id).update(username=username, email=email, mobileno =mobileno,aadhaarno=aadhaarno, address=address,password=password)
        resp = jsonify('User updated successfully!')
        return resp
    else:
        return not_found()

@app.route('/oneuser', methods=['GET'])
@token_required
def get_user(current_user):
    user = UserDetails.objects.filter(id=current_user.id)
    if not user:
        abort(400)
    result = []
    for u in user:
        user_data = {}
        user_data['username'] = u.username
        user_data['mobileno'] = u.mobileno
        user_data['email'] = u.email
        user_data['aadhaarno'] = u.aadhaarno
        user_data['address'] = u.address

        result.append(user_data)

    return jsonify({'user': result})

@app.route('/userpublicid/<publicid>', methods=['GET'])
def getuserpid(publicid):
    user = UserDetails.objects.get(public_id=publicid)
    return user.to_json()

    # if not user:
    #     abort(400)
    # result = []
    # for u in user:
    #     user_data = {}
    #     user_data['id'] =str(u.pk())
    #     user_data['username'] = u.username
    #     user_data['mobileno'] = u.mobileno
    #     user_data['email'] = u.email
    #     user_data['aadhaarno'] = u.aadhaarno
    #     user_data['address'] = u.address
    #
    #     result.append(user_data)
    #
    # return jsonify({'user': result})

@app.route('/users', methods=['GET'])
def users_list():
    resp = UserDetails.objects.all()
    result = []
    for u in resp:
        user_data = {}

        user_data['username'] = u.username
        user_data['mobileno'] = u.mobileno
        user_data['email'] = u.email
        user_data['aadhaarno'] = u.aadhaarno
        user_data['address'] = u.address

        result.append(user_data)

    return jsonify({'user': result})

@app.route('/delete', methods=['DELETE'])
@token_required
def delete_user(current_user):
    result=UserDetails.objects.get(id=current_user.id)
    result.delete()
    resp = jsonify('User deleted successfully!')
    resp.status_code = 200
    return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
