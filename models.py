#!/usr/bin/env python

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship

Base = declarative_base()

class Status(Base):

    __tablename__ = 'babar_server_status'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    overdraft = Column(Integer)


class Customer(Base):

    __tablename__ = 'babar_server_customer'

    id = Column(Integer, primary_key=True)
    firstname = Column(String)
    nickname = Column(String)
    lastname = Column(String)
    email = Column(String)
    status_id = Column(Integer, ForeignKey('babar_server_status.id'))
    year = Column(Integer)

    status = relationship(Status, backref = 'customer')


class Product(Base):

    __tablename__ = 'babar_server_product'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Float)


class Payment(Base):

    __tablename__ = 'babar_server_payment'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    amount = Column(Float)
    customer_id = Column(Integer, ForeignKey('babar_server_customer.id'))

    customer = relationship(Customer, backref = 'payment')


class Purchase(Base):

    __tablename__ = 'babar_server_purchase'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    amount = Column(Float)
    customer_id = Column(Integer, ForeignKey('babar_server_customer.id'))
    product_id = Column(Integer, ForeignKey('babar_server_product.id'))

    customer = relationship(Customer, backref = 'purchase')
    product = relationship(Product, backref = 'purchase')


class TotalPayment(Base):

    __tablename__ = 'babar_server_total_payment'

    customer_id = Column(Integer, ForeignKey('babar_server_customer.id'), primary_key=True)
    total = Column(Float)

    customer = relationship(Customer, backref = 'totalpayment')


class TopProduct(Base):

    __tablename__ = 'babar_server_top_products'

    product_id = Column(Integer, ForeignKey('babar_server_product.id'), primary_key=True)
    amount = Column(Float)
    count = Column(Integer)

    product = relationship(Product, backref='topproduct')
