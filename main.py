import json
import logging
from hashlib import sha512
from flask import Flask, request
from google.appengine.ext import ndb

app = Flask(__name__)
SALT = 'gUjowxfJPz2kJJpUlCLWvZqzKbJPbSFg3hPpXZ9CSOI='


def hash_password(password):
    return sha512(SALT + password).hexdigest()


class User(ndb.Model):
    email = ndb.StringProperty()
    password = ndb.StringProperty()
    name = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)

    def to_object(self):
        data = {}
        data['email'] = self.email
        data['name'] = self.name
        data['created'] = self.created.isoformat() + 'Z'
        data['updated'] = self.updated.isoformat() + 'Z'
        return data


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        response = {}
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query(User.email == email).fetch(keys_only=True)
        if user:
            user = user[0].get()
            logging.debug(user)
            if user.password == hash_password(password):
                return json.dumps(user.to_object())
            else:
                response['message'] = 'Invalid password'
        else:
            response['message'] = 'Invalid email'
        return json.dumps(response)


@app.route('/register', methods=['POST'])
def register():
    response = {}
    email = request.form.get('email')
    password = request.form.get('password')
    name = request.form.get('name')
    user = User.query(User.email == email).fetch(keys_only=True)
    if not user:
        user = User()
        user.email = email
        user.password = hash_password(password)
        user.name = name
        user.put()
        return json.dumps(user.to_object())
    else:
        response['message'] = 'Email already exist'
    return json.dumps(response)