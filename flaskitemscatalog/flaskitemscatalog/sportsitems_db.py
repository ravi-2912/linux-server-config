# configuration
import sys
from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
#from sqlalchemy.exc import *
from sqlalchemy import create_engine

# configuration
Base = declarative_base()
DBURI = "postgresql://sportsitems:sportsitems@localhost:5432/sportsitems"


# class for users table
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    username = Column(String(32), index=True, unique=True)
    password = Column(String(32), nullable=False)
    email = Column(String(250), nullable=False, index=True, unique=True)


# class for table category
class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            "name": self.name,
            "id": self.id,
            "user_id": self.user_id
        }


# class for table items
class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False, index=True)
    description = Column(String(500))
    quantity = Column(Integer, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship(User)
    date_created = Column(DateTime, default=datetime.now())

    @property
    def serialize(self):
        return {
            "name": self.name,
            "id": self.id,
            "desc": self.desc,
            "qty": self.qty,
            "cat_id": self.cat_id
        }


# main function
def main():
    engine = create_engine(DBURI, pool_size=10, max_overflow=20)
    Base.metadata.create_all(engine)


# Database crud operation class
class CRUD:
    def __init__(self):
        engine = create_engine(DBURI, echo=True, pool_size=10, max_overflow=20)
        Base.metadata.bind = engine
        DBsession = sessionmaker(bind=engine)
        self.session = DBsession()

    def newUser(self, login_session):
        nUser = User(name=login_session["name"],
                     email=login_session["email"],
                     username=login_session["username"],
                     password=login_session["password"])
        self.session.add(nUser)
        self.session.commit()
        user = self.session.query(User)\
            .order_by(User.id.desc())\
            .first()
        return user.id

    def getUserID(self, username):
        user = self.session.query(User)\
            .filter_by(username=username)\
            .one()
        return user.id

    def getUserIDByEmail(self, email):
        try:
            user = self.session.query(User)\
                .filter_by(email=email)\
                .one()
            return user.id
        except:
            return False

    def getUserPwd(self, user_id):
        user = self.session.query(User)\
            .filter_by(id=user_id)\
            .one()
        return user.password

    def newCategory(self, name, user_id):
        try:
            nCat = Category(name=name, user_id=user_id)
            self.session.add(nCat)
            self.session.commit()
            cat = self.session.query(Category)\
                .order_by(Category.id.desc())\
                .first()
            return cat.id
        except:
            return None

    def getCategories(self):
        try:
            return self.session.query(Category).all()
        except:
            return None

    def getCategory(self, id):
        try:
            return self.session.query(Category)\
                   .filter_by(id=id).one()
        except:
            return None

    def editCategory(self, id, new_name):
        try:
            cat = self.session.query(Category)\
                .filter_by(id=id)\
                .one()
            cat.name = new_name
            self.session.add(cat)
            self.session.commit()
            return cat.id
        except:
            return None

    def deleteCategory(self, id):
        try:
            cat = self.session.query(Category)\
                .filter_by(id=id)\
                .one()
            self.session.delete(cat)
            self.session.commit()
            return True
        except:
            return False

    def newItem(self, name, description, quantity, category_id, user_id):
        try:
            nItem = Item(name=name,
                         description=description,
                         quantity=quantity,
                         category_id=category_id,
                         user_id=user_id)
            self.session.add(nItem)
            self.session.commit()
            item = self.session.query(Item)\
                .order_by(Item.id.desc())\
                .first()
            return item.id
        except:
            return None

    def editItem(self, id, name, description, quantity, category_id):
        try:
            item = self.session.query(Item)\
                   .filter_by(id=id)\
                   .one()
            item.name = name
            item.description = description
            item.quantity = quantity
            item.category_id = category_id
            self.session.add(item)
            self.session.commit()
            item = self.session.query(Item)\
                .order_by(Item.id.desc())\
                .first()
            return item.id
        except:
            return None

    def getAllItems(self):
        try:
            return self.session.query(Item).all()
        except:
            return None

    def getItemsByCategory(self, category_id):
        try:
            return self.session.query(Item)\
                   .filter_by(category_id=category_id)\
                   .all()
        except:
            return None

    def getItemByID(self, id):
        try:
            return self.session.query(Item)\
                   .filter_by(id=id)\
                   .one()
        except:
            return None

    def deleteItem(self, id):
        try:
            item = self.session.query(Item)\
                .filter_by(id=id)\
                .one()
            self.session.delete(item)
            self.session.commit()
            return True
        except:
            return False


if __name__ == "__main__":
    main()
