from sqlalchemy import Column, Integer, Float, Date, DateTime, Text, Boolean, String, ForeignKey, or_, not_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship, query_expression
from sqlalchemy.sql import func
from database import Base, db_session, engine as db_engine
import datetime
from flask_login import UserMixin
#from eng import manager
class Shop(Base):
    __tablename__ = "shops"
    id = Column(Integer, primary_key=True)
    name = Column(String(200),nullable=False, default="")
    number = Column(String(100), nullable=False, default="")
    mail = Column(String(100), nullable=False, default="")
    reference1 = Column(String(150), nullable=False, default="")
    reference2 = Column(String(150), nullable=False, default="")
    reference3 = Column(String(150), nullable=False, default="")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    sex = Column(Boolean, default=False)
    image = Column(String(500), nullable=False,default="")
    name = Column(String(150),nullable=False,default="")
    cost = Column(Integer)
    color = Column(String(100), nullable=False, default="")
    size = Column(String(50),nullable=False, default="")
    article = Column(Integer)
    is_available = Column(Boolean,default=True)
    structure = Column(String(100),nullable=False, default="")
    origin_country = Column(String(100), nullable=False, default="")
    category_id = Column(Integer, ForeignKey('categories.id'))  # Указываем внешний ключ на таблицу 'categories'
    category = relationship("Categorie", back_populates="products", primaryjoin="Product.category_id == Categorie.id")

class Categorie(Base):
    __tablename__ = "categories"
    id = Column(Integer,primary_key=True)
    categories_name = Column(String(100),nullable=False,default="")
    sex = Column(Boolean, default=False)
    products = relationship("Product", back_populates="category")


class User(Base, UserMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(200),nullable=False, default="")
    surname = Column(String(200),nullable=False, default="")
    phone_number = Column(String(100),nullable=False, default="")
    mail = Column(String(200),nullable=False, default="")
    addres = Column(String(200),nullable=False, default="")
    login = Column(String(100),unique=True)
    password = Column(String(200))
    orders = relationship('Order', back_populates='user')


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    delivery_type = Column(String(200),nullable=False, default="")
    address = Column(String(200),nullable=False, default="")
    delivery_date = Column(Date)
    request_time = Column(DateTime)
    total = Column(Integer)
    pwz_id = Column(Integer, ForeignKey('pwz.id'))
    pwz = relationship("PWZ", back_populates="orders")
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='orders')
    order_items = relationship("OrderItems", back_populates="order")
    zakazi = relationship("Zakazi",back_populates="order")


class OrderItems(Base):
    __tablename__ = "orders_item"
    id = Column(Integer, primary_key=True)
    id_user = Column(Integer, ForeignKey("users.id"))
    id_order = Column(Integer, ForeignKey('orders.id'))
    order = relationship("Order", back_populates="order_items")
    id_product = Column(Integer, ForeignKey("products.id"))
    product = relationship("Product")  # Добавляем связь с объектом Product
    product_cost = Column(Integer, default=0)  # Стоимость продукта
    product_quantity = Column(Integer, default=0)  # Количество продукта

class Zakazi(Base):
    __tablename__ = "zakazi"
    id = Column(Integer, primary_key=True)
    id_user = Column(Integer, ForeignKey("users.id"))
    id_order = Column(Integer, ForeignKey('orders.id'))
    order = relationship("Order", back_populates="zakazi")
    id_product = Column(Integer, ForeignKey("products.id"))
    product = relationship("Product")  # Добавляем связь с объектом Product
    product_cost = Column(Integer, default=0)  # Стоимость продукта
    product_quantity = Column(Integer, default=0)  # Количество продукта

class PWZ(Base):
    __tablename__ = "pwz"
    id = Column(Integer, primary_key=True)
    name = Column(String(200),nullable=False, default="")
    addres = Column(String(100), nullable=False, default="")
    start_time = Column(Integer)
    end_time = Column(Integer)
    number = Column(String(200),nullable=False, default="")
    orders = relationship("Order", back_populates="pwz")

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    from database import engine
    Base.metadata.create_all(bind=engine)
    db_session.commit()

def print_schema(table_class):
    from sqlalchemy.schema import CreateTable, CreateColumn
    print(str(CreateTable(table_class.__table__).compile(db_engine)))

def print_columns(table_class, *attrNames):
   from sqlalchemy.schema import CreateTable, CreateColumn
   c = table_class.__table__.c
   print( ',\r\n'.join((str( CreateColumn(getattr(c, attrName)).compile(db_engine)) \
                            for attrName in attrNames if hasattr(c, attrName)
               )))



if __name__ == "__main__":
    init_db()
    #example_1()
    #example_3()
    #print_columns(Payment, "created")
    #print_schema(SoltButton)
