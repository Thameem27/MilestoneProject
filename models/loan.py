from db import db

class LoanModel(db.Model):
    __tablename__ = "Loan"
    Loan_id = db.Column(db.Integer, primary_key=True)
    Customer_id = db.Column(db.Integer, db.ForeignKey("Customers.Customer_id"), nullable=False) # Column(Integer, ForeignKey('Customer.Customer_id'), unique=True)
    Name = db.Column(db.String(200), nullable=False)
    Loan_type = db.Column(db.String(30), nullable=False)
    Loan_amount= db.Column(db.Integer, nullable=False)
    Loan_date = db.Column(db.String(20), nullable=False)
    Rate_of_interest = db.Column(db.Integer, nullable=False)
    Duration = db.Column(db.Integer, nullable=False)
    Customer = db.relationship("CustomerModel")

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return '<Loan account %r is now created with an loan Type %r >' % (self.Loan_id, self.Loan_type)