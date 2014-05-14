from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship, backref


Base = declarative_base()

class Experiment(Base):
    __tablename__ = 'experiments'
    
    def __init__(self):
        self.description = ""
    
    id = Column(Integer, primary_key=True)
    description = Column(String)
    total_accepted_ar = Column(Integer)
    total_rejected_ar = Column(Integer)
    total_accepted_im = Column(Integer)
    total_rejected_im = Column(Integer)
    total_completed_be = Column(Integer)
    be_completed_after = Column(Float)
    
    def __repr__(self):
        return self.description
    
    
class CPU(Base):
    __tablename__ = 'cpu_utilizations'
    
    id = Column(Integer, primary_key=True)
    experiment_id = Column(Integer, ForeignKey('experiments.id'))
    experiment = relationship("Experiment", backref=backref('cpu_utilizations', order_by=id))
    time = Column(String)
    node = Column(String)
    value = Column(String)
    avg = Column(String)

    def __repr__(self):
        return "Cpu Utilization for experiment %s" % self.experiment_id
    
class LeaseStatistics(Base):
    __tablename__ = 'lease_statistics'
    
    id = Column(Integer, primary_key=True)
    experiment_id = Column(Integer, ForeignKey('experiments.id'))
    experiment = relationship("Experiment", backref=backref('lease_statistics', order_by=id))
    lease_id = Column(Integer)
    waiting_time = Column(Float)
    slowdown = Column(Float)

    