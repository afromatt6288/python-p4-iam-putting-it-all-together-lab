# #!/usr/bin/env python3

from flask import request, session, make_response, jsonify
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Home(Resource):
    def get(self):   
        recipe_dict = ''' 
            <h1>"message": "Welcome to the Recipe RESTful API"</H1>
        '''
        response = make_response(recipe_dict, 200)
        return response
api.add_resource(Home, '/')

class Signup(Resource):
    def post(self):
        username = request.get_json().get('username')
        password = request.get_json().get('password')
        image_url = request.get_json().get('image_url')
        bio = request.get_json().get('bio')
        if username and password:
            new_user = User(username=username, image_url=image_url, bio=bio)
            new_user.password_hash = password
            try:
                db.session.add(new_user)
                db.session.commit()
                session['user_id'] = new_user.id
                return new_user.to_dict(), 201
            except IntegrityError:
                return {'error': '422 Unprocessable Entity'}, 422
        return {'error': '422 Unprocessable Entity'}, 422
api.add_resource(Signup, '/signup', endpoint='signup')
 
class CheckSession(Resource):
    def get(self):
        if session.get('user_id'):
            user = User.query.filter(User.id == session.get('user_id')).first()
            return user.to_dict(), 200 
        return {'message': '401 Unauthorized'}, 401  
api.add_resource(CheckSession, '/check_session', endpoint='check_session')

class Login(Resource):
    def post(self):
        username = request.get_json()['username']
        password = request.get_json()['password']
        user = User.query.filter(User.username == username).first()
        if user:
            if user.authenticate(password):
                session['user_id'] = user.id
                return user.to_dict(), 200     
        return {'error': '401 Unauthorized'}, 401
api.add_resource(Login, '/login', endpoint='login')

class Logout(Resource):
    def delete(self): 
        if session.get('user_id'):
            session['user_id'] = None
            return {'message': '204: No Content'}, 204  
        return {'error': '401 Unauthorized'}, 401
api.add_resource(Logout, '/logout')
    
class RecipeIndex(Resource):
    def get(self):
        if session.get('user_id'):
            user = User.query.filter(User.id == session['user_id']).first()
            return [recipe.to_dict() for recipe in user.recipes], 200        
        return {'error': '401 Unauthorized'}, 401
        
    def post(self):
        if session.get('user_id'):
            title=request.get_json()['title']
            instructions=request.get_json()['instructions']
            minutes_to_complete=request.get_json()['minutes_to_complete']
            user_id=session['user_id'],
            if title and instructions and minutes_to_complete and user_id:
                recipe = Recipe(
                    title=title,
                    instructions=instructions,
                    minutes_to_complete=minutes_to_complete,
                    user_id=user_id,
                )
                try:
                    db.session.add(recipe)
                    db.session.commit()
                    return recipe.to_dict(), 201
                except IntegrityError:
                    return {'error': '422 Unprocessable Entity'}, 422
            return {'error': '422 Unprocessable Entity'}, 422
        return {'error': '401 Unauthorized'}, 401
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
