from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()


class Experiment(Base):
    __tablename__ = 'experiment'
    
    id = Column(Integer, primary_key=True)
    
    def __repr__(self):
        pass
    
    
class CPU(Base):
    __tablename__ = 'cpu'
    
    id = Column(Integer, primary_key=True)
 
    def __repr__(self):
        return ""
    
