from flask import request, jsonify, url_for, g
from flask_restful import Api, Resource, fields, marshal_with, marshal, reqparse, abort

from app.models.sqlite import User
from app.lib.myauth import http_basic_auth, my_login_required, my_permission_required
from app.lib.mydecorator import viewfunclog
from app.myglobals import PERMISSIONS

api_auth = Api(prefix='/api/auth/')


fields_user_db = {
    'id': fields.Integer,
    'username': fields.String,
    'desc': fields.String,
}

fields_user_response = {
    'status': fields.Integer,
    'msg': fields.String,
    'data': fields.Nested(fields_user_db)
}

fields_users_response = {
    'status': fields.Integer,
    'msg': fields.String,
    'data': fields.List(fields.Nested(fields_user_db))
}



class ResourceUser(Resource):
    # @http_basic_auth.login_required
    @my_login_required
    @my_permission_required(PERMISSIONS.P6)
    @viewfunclog
    @marshal_with(fields_user_db)
    def get(self, id):
        return User.query.get(id)

class ResourceResetPassword(Resource):
    @my_login_required
    @my_permission_required(PERMISSIONS.P6)
    @viewfunclog
    def get(self):
        newpassword = request.form.get('newpassword')
        if len(newpassword) < 6:
            abort(403, status=406, username=g.user.username, msg='failed, new password format not acceptable')
        user = g.user
        user.password = newpassword
        if not user.save():
            abort(400, msg='failed to save database')
        response_obj = {
            'user': user.username,
            'msg': 'change password success'
        }
        return response_obj
    


class ResourceUsers(Resource):
    # @http_basic_auth.login_required
    @my_login_required
    @my_permission_required(PERMISSIONS.P6)
    @viewfunclog
    @marshal_with(fields_users_response)
    # 获取所有账号信息
    def get(self):
        users = User.query.all()
        response_obj = {
            'status': 202,
            'msg': 'all users data',
            'data': users
        }
        return response_obj

    # @http_basic_auth.login_required
    @my_login_required
    @my_permission_required(PERMISSIONS.P6)
    @viewfunclog
    @marshal_with(fields_user_response)
    # 注册新用户
    def post(self):
        # username = request.json.get('username')
        # password = request.json.get('password')
        newusername = request.form.get('newusername')
        newpassword = request.form.get('newpassword')
        if newusername is None or newpassword is None:
            # 406    NOT Acceptable    用户请求不被服务器接收（比如服务器期望客户端发送某个字段，但是没有发送）
            abort(406, msg='newusername and newpassword are required')
        if User.query.filter_by(username = newusername).first() is not None:
            abort(400, msg='user {} already exist'.format(newusername))
        # user = User(username = username)
        # user.hash_password(password)
        user = User()
        user.username = newusername
        user.password = newpassword
        if not user.save():
            abort(400, msg='failed to save database')
        # return jsonify({ 'username': user.username }), 200, {'Location': url_for('get_user', id = user.id, _external = True)}        
        response_obj = {
            'status': 201,
            'msg': 'user {} register success'.format(user.username),
            'data': user
        }
        return response_obj, 201, {'Location': url_for('get_user', id = user.id, _external = True)}

    
class ResourceToken(Resource):
    # @http_basic_auth.login_required
    @my_login_required
    @my_permission_required(PERMISSIONS.P6)
    @viewfunclog
    def get(self):
        token = g.user.generate_auth_token()
        return {
            'status': 200,
            'msg': 'login success',
            'username':g.user.username,
            # 'token': token.decode('ascii'),
            'token': token if type(token) is str else token.decode('ascii'),
            'duration': 600
        }
    
class ResourceLoginTest(Resource):
    # @http_basic_auth.login_required
    @my_login_required
    @my_permission_required(PERMISSIONS.P6)
    @viewfunclog
    def get(self):
        return {
            'status': 202,
            'username': g.user.username,
            'msg': "login success",
        }


api_auth.add_resource(ResourceUser, '/user/<int:id>', endpoint='get_user')
api_auth.add_resource(ResourceUsers, '/users', '/register', endpoint='get_users')
api_auth.add_resource(ResourceResetPassword, '/reset', endpoint='reset_password')
api_auth.add_resource(ResourceToken, '/token', '/login')
api_auth.add_resource(ResourceLoginTest, '/logintest')

# api verification example by crul
# 1. get token
# curl -u user1:123456 -i -X GET http://10.30.30.101:4000/api/auth/token
# curl -X GET 'http://10.30.30.101:4000/api/auth/token' --header 'Authorization: Basic dXNlcjE6MTIzNDU2'
# "user1:123456" --base64--> "dXNlcjE6MTIzNDU2"
# 2. login test by token
# curl -u eyJhbGciOiJIUzUxMiIsImlhdCI6MTU4OTA1MTUzMiwiZXhwIjoxNTg5MDUyMTMyfQ.eyJpZCI6MX0.igadnHdP7lKHh311dEVF7lRVbdg3JwdgyUHBtWxwEEvAnT-0D2Lnd2rkktmkPxj_Zdob4XBi2bYoqPgwpcu05w:password -i -X GET http://10.30.30.101:4000/api/auth/logintest



