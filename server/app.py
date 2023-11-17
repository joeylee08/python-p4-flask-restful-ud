#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Newsletter

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newsletters.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

class Home(Resource):

    def get(self):
        
        response_dict = {
            "message": "Welcome to the Newsletter RESTful API",
        }
        
        response = make_response(
            response_dict,
            200,
        )

        return response

api.add_resource(Home, '/')

class Newsletters(Resource):

    def get(self):
        
        response_dict_list = [n.to_dict() for n in Newsletter.query.all()]

        response = make_response(
            response_dict_list,
            200,
        )

        return response

    def post(self):
        
        new_record = Newsletter(
            title=request.form['title'],
            body=request.form['body'],
        )

        db.session.add(new_record)
        db.session.commit()

        response_dict = new_record.to_dict()

        response = make_response(
            response_dict,
            201,
        )

        return response

api.add_resource(Newsletters, '/newsletters')

class NewsletterByID(Resource):

    def get(self, id):
        response_dict = Newsletter.query.filter_by(id=id).first().to_dict()
        response = make_response(
            response_dict,
            200,
        )
        return response
    
    def patch(self, id):
        record = Newsletter.query.filter(Newsletter.id == id).first()
        try:
            data = request.form
            #this didn't work for some reason
            # data = request.get_json()
            for k, v in data.items():
                setattr(record, k, v)
            db.session.commit()
            return make_response(record.to_dict(), 200)
        except Exception as e:
            db.session.rollback()
            return {"Error": str(e)}, 400
        
    def delete(self, id):
        record = Newsletter.query.filter_by(id=id).first()
        try:
            db.session.delete(record)
            db.session.commit()
            #returned message not showing up on postman
            return make_response({"message": "delete successful"}, 204)
        except Exception as e:
            db.session.rollback()
            return make_response({"error" : str(e)}, 400)

api.add_resource(NewsletterByID, '/newsletters/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)