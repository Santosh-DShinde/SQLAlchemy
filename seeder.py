"""python imports"""
import time
import logging
import traceback
from datetime import datetime

"""SQLAlchemy imports"""
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, String, Column, DateTime, ForeignKey, create_engine

"""logging configuration"""
logging.basicConfig(level=logging.INFO)


"""database credentials"""
username = "root"
password = "password"
host = "localhost"
port = "3306"
database = "employee"

# global variables
session = None
engine = None

def create_database_connection(max_retries=10):
    global session, engine
    retries = 0
    while retries < max_retries:
        try:
            engine = create_engine(
                f"mysql+mysqlconnector://{username}:{password}@{host}:{port}/{database}?connect_timeout=30",
                echo=True, pool_recycle=3600, pool_size=10, max_overflow=5
            )
            Session = sessionmaker(bind=engine)
            session = Session()
            return engine, session
        except OperationalError as e:
            retries += 1
            if retries < max_retries:
                time.sleep(6)

engine, session = create_database_connection()

Base = declarative_base()

"""Base Model"""
class BaseModel():
    __tablename__ = 'base'
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, index=True)
    __abstract__ = True


"""User Model"""
class Users(BaseModel, Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, nullable=False)  
    full_name = Column(String(255), nullable=True, index=True)
    username = Column(String(255), nullable=True, index=True)
    email = Column(String(255), nullable=True, index=True)
    password = Column(String(255), nullable=True, index=True)

    address_id = Column(Integer, ForeignKey('addresses.id', ondelete='CASCADE'),nullable=True)
    user = relationship('Addresses', backref='users')


"""Employee Model"""
class Employees(BaseModel, Base):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True, nullable=False)  
    birth_date = Column(DateTime, nullable=True, index=True)
    emp_id = Column(Integer, nullable=True, index=True)

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    user = relationship('Users', backref='employees')


"""Address Model"""
class Addresses(BaseModel, Base):
    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True)
    street = Column(String(255), nullable=True, index=True)
    city = Column(String(255), nullable=True, index=True)
    area = Column(String(255), nullable=True, index=True)


Base.metadata.create_all(engine)

def commit_session(model, data):
    try:
        global session
        instance = model(**data)
        session.add(instance)
        session.commit()
        return instance
    
    except Exception as e:
        session.rollback()
        logging.info(f"Failed to onboard employee ):\n {str(e)}")
        return None

def onboard_employee(address_data, user_data, employee_data):
    try:
        if address_instance := commit_session(Addresses, address_data):
            user_data['address_id'] = address_instance.id

        if user_instance := commit_session(Users, user_data):
            employee_data['user_id'] = user_instance.id

        if employee_instance := commit_session(Employees, employee_data):
            logging.info(f"Employee {employee_instance.id} onboarded successfully.")

    except Exception as e:
        logging.info(f"Failed to onboard the employee !!!\n {traceback.format_exc()}")


address_data = {"street":"DP Road","city":"Pune","area":"Bhlkenagar"}
user_data = {"full_name":"Santosh Shinde","username":"santosh@shinde","email":"santosh@gmail.com","password":"123456"}
employee_data = {"birth_date":"2000-04-28","emp_id":287}


def main():
    logging.info("SQLAlchemy database operations started !!!")
    onboard_employee(address_data, user_data, employee_data)

if __name__ == "__main__":
    main()
