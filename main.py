# import _json
#
# from app import app, mongo
# from bson.json_util import dumps
# from bson.objectid import ObjectId
# from flask import jsonify, request
#
# @app.route('/add', methods=['POST'])
# def add_user():
# 	_json = request.json
# 	_name = _json['name']
# 	_email = _json['email']
# 	_mobileno = _json['mobileno']
#     _aadhaarno = _json['aadhaarno']
# 	# validate the received values
# 	if _name and _email and _mobileno and _aadhaarno and request.method == 'POST':
#
# 		# save details
# 		id = mongo.db.user.insert({'name': _name, 'email': _email})
# 		resp = jsonify('User added successfully!')
# 		resp.status_code = 200
# 		return resp
# 	else:
# 		return not_found()