from flask import Flask, request, jsonify, make_response
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_marshmallow import Marshmallow
from marshmallow import ValidationError
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from werkzeug.security import generate_password_hash, check_password_hash, safe_str_cmp
from models.customers import CustomerModel
from models.loan import LoanModel
from functools import wraps
from db import db
import jwt
import datetime
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///BankDB.sqlite3'
app.config['SECRET_KEY'] = "THAMKEY27"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
api = Api(app)
BankDB = SQLAlchemy(app)
ma = Marshmallow(app)
INVALID_CREDENTIALS = "Invalid credentials!"

# jwt = JWTManager(app)

@app.before_first_request
def create_tables():
    db.create_all()

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = CustomerModel
class LoanSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LoanModel
class ViewCustomerSchema(ma.SQLAlchemySchema):
    class Meta:
        model = CustomerModel
    Username=auto_field()
    Address=auto_field()
    PAN=auto_field()
    Account_type=auto_field()

class ViewLoanSchema(ma.SQLAlchemySchema):
    class Meta:
        model = LoanModel		
    Customer_id=auto_field()
    Name=auto_field()
    Loan_id=auto_field()
    Loan_amount=auto_field()
    Loan_type=auto_field()

customer_schema = CustomerSchema()
viewcustomer_schema = ViewCustomerSchema()
viewloan_schema = ViewLoanSchema()
customers_schema = CustomerSchema(many=True)
loan_schema = LoanSchema()
loans_schema = LoanSchema(many=True)

def token_check(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = None
        if 'Bearer' in request.headers:
            token = request.headers['Bearer']
        if not token:
            return "This Token is Invalid"
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms = "HS256")
            current_user = CustomerModel.query.filter_by(Customer_id = data['public_id']).first()
            print(data)
            print(current_user)
        except:
            return "This Token is Invalid"
        return f(current_user, *args, *kwargs)
    return wrapper

class UpdateAccountDetails(Resource):  
    def put(self, Customer_id):      
        cust = CustomerModel.query.get_or_404(Customer_id)
        if 'Name' in request.json:
            cust.Name = request.json['Name']
        elif 'Username' in request.json:
            cust.Username = request.json['Username']
        elif 'Password' in request.json:
           cust.Password = generate_password_hash(request.json['Password'], method='sha256') #rrequest.json['Password']
        elif 'Address' in request.json:
           cust.Address = request.json['Address']
        elif 'State' in request.json:
           cust.State = request.json['State']
        elif 'Country' in request.json:
           cust.Country = request.json['Country']
        elif 'Email_address' in request.json:
           cust.Email_address = request.json['Email_address']   
        elif 'PAN' in request.json:
           cust.PAN = request.json['PAN']
        elif 'Contact_no' in request.json:
           cust.Contact_no = request.json['Contact_no']
        elif 'DOB' in request.json:
           cust.DOB = request.json['DOB']
        elif 'Account_type' in request.json:
           cust.Account_type = request.json['Account_type']         
        else:
            return {"message": 'Could not Find the Attribute to Update please check'}, 404
        
        cust.save_to_db()
        return customer_schema.dump(cust)

    @classmethod
    def delete(cls, customer_id: int):
        cust = CustomerModel.query.filter_by(Customer_id=customer_id).first()
        if cust:
            cust.delete_from_db()
            return {"message": 'Customer Deleted Successfully'}, 200

        return {"message": 'Customer Not Found'}, 404

@token_check
def get_current_user_id(current_user):
    newuser = CustomerModel.query.filter_by(Username = current_user.Username).first()
    return newuser
class View(Resource):
    def get(self):
        newuser = get_current_user_id()
        return customer_schema.jsonify(newuser)

class ViewCustomer(Resource):
    def get(self,customername):
        Cust = CustomerModel.query.filter_by(Username=customername).first_or_404(description='No Customer Exists with this Username {}. Kindly Re-check'.format(customername))
        return viewcustomer_schema.dump(Cust),200

class AddCustomer(Resource):
    def get(self):
        cust = CustomerModel.query.all()
        return customers_schema.dump(cust), 200
    def post(self):
        try:
            customer = customer_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400
            
        result = CustomerModel.query.filter_by(Username=request.json['Username']).first() 
        if result is None:
            new_cust = CustomerModel(
                Name = request.json['Name'],
                Username = request.json['Username'],
                Password = generate_password_hash(request.json['Password'], method='sha256'), #request.json['Password'],
                Address = request.json['Address'],
                State = request.json['State'],
                Country = request.json['Country'],
                Email_address = request.json['Email_address'],
                PAN = request.json['PAN'],
                Contact_no = request.json['Contact_no'],
                DOB = request.json['DOB'],
                Account_type = request.json['Account_type']
            )
            BankDB.session.add(new_cust)
            BankDB.session.commit()
            return viewcustomer_schema.dump(new_cust), 201
        else:
            return {"message":f"User {request.json['Username']} already Exists in the Table."},400

class UserLogin(Resource):
        def post(self):
            auth = request.authorization
            newuser = CustomerModel.query.filter_by(Username = auth.username).first()
            print(newuser)
            if newuser is None:
                response=make_response(jsonify({"message":"No Such User Exists in the Database"}),404)
                # return jsonify({"message":"No Such User Exists in the Database"}), 404
                return response
            print(newuser.Password, auth.password)
            
            if check_password_hash(newuser.Password, auth.password):
                token = jwt.encode({'public_id':newuser.Customer_id, 'exp':datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
                return token        
            
            response={"message": INVALID_CREDENTIALS}, 401 #make_response(jsonify({"message":"Not Verified"}),404)
            return response

class ApplyLoan(Resource):
    def get(self):
        loan = LoanModel.query.all()
        return loans_schema.dump(loan)
    def post(self):
        custexists = CustomerModel.query.filter_by(Customer_id=request.json['Customer_id']).first()
        if custexists:
            custid_check = LoanModel.query.filter_by(Customer_id=request.json['Customer_id']).first()
        else:
            response=make_response(jsonify({"message":f"Customer {request.json['Name']} doesnt exist "}),404)
            return response
        
        if custexists is not None and custid_check is None:
            # result = db.query(Customer).count()
            new_loan = LoanModel(
                Customer_id = request.json['Customer_id'],
                Name = request.json['Name'],
                Loan_type = request.json['Loan_type'],
                Loan_amount = request.json['Loan_amount'],
                Loan_date = request.json['Loan_date'],
                Rate_of_interest = request.json['Rate_of_interest'],
                Duration = request.json['Duration']
            )
            BankDB.session.add(new_loan)
            BankDB.session.commit()
            return loan_schema.dump(new_loan), 201
        else:
            response=make_response(jsonify({"message":f"A Loan on the name of {request.json['Name']} is already Applied."}),400)
            return response

class ViewLoan(Resource):
    def get(self,loan_id):
       loan = LoanModel.query.filter_by(Loan_id=loan_id).first_or_404(description='No loan Exists with this loan Id {}. Kindly Re-check'.format(loan_id))
       return viewloan_schema.dump(loan), 200

class UpdateLoanDetails(Resource):  
    def put(self, loan_id):
        loan = LoanModel.query.get_or_404(loan_id)
        if 'Name' in request.json:
            loan.Name = request.json['Name']
        if 'Loan_type' in request.json:
            loan.Loan_type = request.json['Username']
        if 'Loan_amount' in request.json:
           loan.Loan_amount = request.json['Account_type']         

        loan.save_to_db()
        return viewloan_schema.dump(cust)

    @classmethod
    def delete(cls, loan_id: int):
        cust = LoanModel.query.filter_by(Loan_id=loan_id).first()
        if cust:
            cust.delete_from_db()
            return {"message": f'Loan ID {loan_id} Details Deleted Successfully'}, 200

        return {"message": f'Loan {loan_id} Not Found'}, 404

api.add_resource(AddCustomer,'/addcustomer')
api.add_resource(View,'/viewcustomer')
api.add_resource(ViewCustomer,'/viewcustomer/<customername>')
api.add_resource(UpdateAccountDetails,'/updateaccount/<int:Customer_id>')    
api.add_resource(ApplyLoan,'/ApplyLoan')
api.add_resource(ViewLoan,'/GetLoanDetail/<int:loan_id>')
api.add_resource(UpdateLoanDetails,'/updateloan/<int:loan_id>')
api.add_resource(UserLogin, "/login")

if __name__ == '__main__':
    app.run(debug=True)  # important to mention debug=True