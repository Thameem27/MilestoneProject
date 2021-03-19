from db import db

class CustomerModel(db.Model):
    __tablename__ = "Customers"
    Customer_id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    Username = db.Column(db.String(30), nullable=False)
    Password = db.Column(db.String(1000), nullable=False)
    Address = db.Column(db.String(500), nullable=False)
    State = db.Column(db.String(20), nullable=False)
    Country = db.Column(db.String(20), nullable=False)
    Email_address = db.Column(db.String(100), nullable=False)
    PAN = db.Column(db.String(20), nullable=False)
    Contact_no= db.Column(db.Integer, nullable=False)
    DOB = db.Column(db.String(20), nullable=False)
    Account_type = db.Column(db.String(20), nullable=False)
    
    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
    
    def __repr__(self):
        return '<User %r is now Created with an Account Type %r >' % (self.Username, self.Account_type)
