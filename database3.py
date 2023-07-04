import os
from sqlalchemy import MetaData, Table, Column, String, Integer
#from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as db
from models import Models
from sqlalchemy import text
import pandas as pd

class Database():
    # replace the user, password, hostname and database according to your configuration according to your information
    db_connection_string = os.environ['DB_CONNECTION_STRING']
    
    connection_ssl_arg = {
      "ssl": {
        "ssl_ca": "/etc/ssl/cert.pem"
      }
    } 
        
  
    engine = db.create_engine(db_connection_string, connect_args = connection_ssl_arg)    
    #print(engine)
    #print(type(engine))
    #session = sessionmaker(autocommit=False, autoflush=False, bind=engine)  
    
    def __init__(self):
        #self.engine = engine
        #self.connection = self.engine.connect()
        #self.session = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)  
        print("DB Instance created")

    def fetchAllModels(self):
        # bind an individual Session to the connection
        results_to_dict = []
        session = sessionmaker(autocommit=False, autoflush=False, bind=self.engine) 
        session = session()
        models = session.query(Models).all()
        
        for each in models:
            #each_line = []
            #print(each.id)
            #print(each.name)
            #print(each.pathLocation)
            #print(each.userName)
            #each_line.append([each.id, each.name, each.pathLocation, each.userName])
            model_to_dict = each.columns_to_dict()
            print(model_to_dict)
            results_to_dict.append(model_to_dict)
            #print(each.as_dict())
        return results_to_dict

    # recordObject = {
    #     'name': record.name,
    #     'position': record.position,
    #     'team_name': record.team.name,
    #     'team_city': record.team.city
    # }      
        #results_to_dict.append(each.id, each.name, each.pathLocation, each.userName)
        #return results_to_dict

    #def search(self, searchClass, searchType, searchName):
    def search(self, modelName):      
        # bind an individual Session to the connection
        session = sessionmaker(autocommit=False, autoflush=False, bind=self.engine) 
        session = session()
        #modelName = 'Data Analyst'
        found = session.query(Models).filter(Models.name == modelName).first()
        if found:
          return True 
        else:
          return False
        #print(author)
        #author = session.query(searchClass).filter(searchType == searchName).first()
        
    def searchSelectedModel(self, id):      
        # bind an individual Session to the connection
        session = sessionmaker(autocommit=False, autoflush=False, bind=self.engine) 
        session = session()
        #found = session.query(Models).filter(Models.name == modelName).first()
        found = session.query(Models).filter(Models.id == id).first()
        #found = session.query(Models).get(id)      
        print(found)
        if found:
          return found.columns_to_dict()
        else:
          return None
        #print(author)
        #author = session.query(searchClass).filter(searchType == searchName).first()
  
    #def search(self, searchClass, searchType, searchName):
    def saveData(self, object):     
        # bind an individual Session to the connection
        session = sessionmaker(autocommit=False, autoflush=False, bind=self.engine) 
        session = session()
        #modelName = 'Data Analyst'
        session.add(object)
        session.commit()

    def create_from_pandas(self, table_name, df):

        df.to_sql(table_name, con=self.engine, if_exists='append', index=False)
        
        
        """
        if_exists: {'fail', 'replace', 'append'}, default 'fail'
             fail: If table exists, do nothing.
             replace: If table exists, drop it, recreate it, and insert data.
             append: If table exists, insert data. Create if does not exist.
        """

    def get_previous_results(self, table_name):


        # SQLAlchemy connectable
        conn = self.engine.connect()
         
        # table named 'employee' will be returned as a dataframe.
        df = pd.read_sql_table(table_name, conn)
        print(df)      
        # # establish the connection with the engine object
        # with self.engine.connect() as conn:
        #     # execute the SQL query "SELECT * FROM loan_data"
        #     result = conn.execute(text("SELECT * FROM " + table_name))

          
        #     # Fetch all the records from the result object
        #     print(result)
        #     records = result.fetchall()

        #     print(records)
        #     # Get the column names from the result object
        #     column_names = result.keys()
    
        #     # Create a pandas DataFrame from the fetched records and column names
        #     df = pd.DataFrame(records, columns=column_names)
    
        return df
        
    # engine = db.create_engine(db_connection_string, connect_args = connection_ssl_arg)
    # def __init__(self):
    #     #self.connection = self.engine.connect()
    #     self.connection = self.engine
    #     #self.session = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    #     print("DB Instance created")

    # def fetchAllUsers(self):
    #     # bind an individual Session to the connection
    #     #self.session = Session(bind=self.connection)   
        
    #     SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    #     customers = SessionLocal.query(Jobs).all()
      
    #     for cust in customers:
    #         print(cust)
