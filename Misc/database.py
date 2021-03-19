from sqlalchemy import create_engine, exc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
Base = declarative_base()

class Customer(Base):
    __tablename__ = 'Customer'
    Customer_id = Column(Integer, primary_key=True)
    Name = Column(String(10), nullable=False)
    Username = Column(String(30), nullable=False)
    Password = Column(String(20), nullable=False)
    Address = Column(String(100), nullable=False)
    State = Column(String(20), nullable=False)
    Country = Column(String(20), nullable=False)
    Email_address = Column(String(50), nullable=False)
    PAN = Column(String(20), nullable=False)
    Contact_no= Column(Integer, nullable=False)
    DOB = Column(String(20), nullable=False)
    Account_type = Column(String(20), nullable=False)
    
    
    def __repr__(self):
        return '<User %r is now Created with an Account Type %r >' % (self.Username, self.Account_type)

class Loan(Base):
    __tablename__ = 'Loan'
    Loan_id = Column(Integer, primary_key=True)
    Customer_id = Column(Integer, ForeignKey('Customer.Customer_id'), unique=True)
    Name = Column(String(10), nullable=False)
    Loan_type = Column(String(30), nullable=False)
    Loan_amount= Column(Integer, nullable=False)
    Loan_date = Column(String(20), nullable=False)
    Rate_of_interest = Column(Integer, nullable=False)
    Duration = Column(Integer, nullable=False)
    
    def __repr__(self):
        return '<Loan account %r is now created with an loan Type %r >' % (self.Loan_id, self.Loan_type)

engine = create_engine('sqlite:///BankDB.sqlite3')
Base.metadata.create_all(engine)