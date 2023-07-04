from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Jobs(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(250), nullable=False)
    location = Column(String(250), nullable=False)
    salary = Column(Integer)
    currency = Column(String(10))
    responsabilities = Column(String(2000))
    requirements = Column(String(2000))

  
    def __repr__(self): 
        return "<Jobs(title='%s')>" % (self.title)

class Models(Base):
    __tablename__ = "models"
  
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    pathLocation = Column(String(255), nullable=False)
    userName = Column(String(255))
    date = Column(DateTime, nullable=False, default=datetime.utcnow())

    def columns_to_dict(self):
        dict_ = {}
        for key in self.__mapper__.c.keys():
            dict_[key] = getattr(self, key)
        return dict_
      
    def __repr__(self): 
      return "<Models(id='%s', name='%s')>" % (self.id, self.name)
      #return "<Customer(name='%s', age='%s', email='%s', address='%s', zip code='%s')>" % (self.name, self.age, self.email, self.address, self.zip_code)
