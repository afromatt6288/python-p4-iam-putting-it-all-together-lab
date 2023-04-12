from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates

from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    _password_hash = db.Column(db.String)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())   
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())    

    recipes = db.relationship('Recipe', backref='user', cascade="all, delete, delete-orphan")

    @validates('username')
    def validate_username(self, key, username):
        users = User.query.all()
        names = [user.username for user in users]
        if not username:
            raise ValueError("User must have a username")
        elif username in names:
            raise ValueError("User Name must be unique")
        return username

    @hybrid_property
    def password_hash(self):
        raise AttributeError('Password hashes may not be viewed.')
        # return self._password_hash

    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(
            password.encode('utf-8'))           
        self._password_hash = password_hash.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(
            self._password_hash, password.encode('utf-8'))
    
def __repr__(self):
        return f'<User: Username:{self.username}, Image: {self.image_url}, Bio: {self.bio}>'

class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'
    __table_args__ = (
        db.CheckConstraint('length(instructions) >= 50'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())  
    updated_at = db.Column(db.DateTime, onupdate=db.func.now()) 

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # @validates('title')
    # def validate_title(self, key, title):
    #     if not title:
    #         raise ValueError("Recipe must have a title")
    #     return title

    # @validates('instructions')
    # def validate_instructions(self, key, string):
    #     if not string:
    #         raise ValueError("Recipe instructions must be present")
    #     if( key == 'instructions'):
    #         if len(string) <= 50:
    #             raise ValueError("Recipe instructions must be at least 50 characters long.")
    #     return string

    def __repr__(self):
        return f'<Recipe: Title:{self.title}, Instructions: {self.instructions}, User: {self.user.username}>'
