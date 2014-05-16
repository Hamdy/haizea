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
    
class CPUPnode(Base):
    __tablename__ = 'cpu_pnode_load'
    
    id = Column(Integer, primary_key=True)
    experiment_id = Column(Integer, ForeignKey('experiments.id'))
    experiment = relationship("Experiment", backref=backref('pnodes_cpu_load', order_by=id))
    time = Column(String)
    node = Column(String)
    value = Column(Float)

    def __repr__(self):
        return "Cpu Utilization for single physical node %s in experiment %s " % (self.node, self.experiment_id)

class DiskPnode(Base):
    __tablename__ = 'disk_pnode_load'
    
    id = Column(Integer, primary_key=True)
    experiment_id = Column(Integer, ForeignKey('experiments.id'))
    experiment = relationship("Experiment", backref=backref('pnodes_disk_load', order_by=id))
    time = Column(String)
    node = Column(String)
    value = Column(Float)

    def __repr__(self):
        return "Disk Utilization for single physical node %s in experiment %s " % (self.node, self.experiment_id)

class NetInPnode(Base):
    __tablename__ = 'net_in_pnode_load'
    
    id = Column(Integer, primary_key=True)
    experiment_id = Column(Integer, ForeignKey('experiments.id'))
    experiment = relationship("Experiment", backref=backref('pnodes_net_in_load', order_by=id))
    time = Column(String)
    node = Column(String)
    value = Column(Float)

    def __repr__(self):
        return "Net in Utilization for single physical node %s in experiment %s " % (self.node, self.experiment_id)

class NetOutPnode(Base):
    __tablename__ = 'net_out_pnode_load'
    
    id = Column(Integer, primary_key=True)
    experiment_id = Column(Integer, ForeignKey('experiments.id'))
    experiment = relationship("Experiment", backref=backref('pnodes_net_out_load', order_by=id))
    time = Column(String)
    node = Column(String)
    value = Column(Float)

class MemoryPnode(Base):
    __tablename__ = 'memory_pnode_load'
    
    id = Column(Integer, primary_key=True)
    experiment_id = Column(Integer, ForeignKey('experiments.id'))
    experiment = relationship("Experiment", backref=backref('pnodes_memory_load', order_by=id))
    time = Column(String)
    node = Column(String)
    value = Column(Float)

    def __repr__(self):
        return "Memory Utilization for single physical node %s in experiment %s " % (self.node, self.experiment_id)
 
    
class LeaseStatistics(Base):
    __tablename__ = 'lease_statistics'
    
    id = Column(Integer, primary_key=True)
    experiment_id = Column(Integer, ForeignKey('experiments.id'))
    experiment = relationship("Experiment", backref=backref('lease_statistics', order_by=id))
    lease_id = Column(Integer)
    waiting_time = Column(Float)
    slowdown = Column(Float)

class AcceptedAR(Base):
    __tablename__ = 'accepted_ar'
    
    id = Column(Integer, primary_key=True)
    experiment_id = Column(Integer, ForeignKey('experiments.id'))
    experiment = relationship("Experiment", backref=backref('accepted_ars', order_by=id))
    time = Column(Float)
    lease_id = Column(Integer)
    count = Column(Integer)

class AcceptedIM(Base):
    __tablename__ = 'accepted_im'
    
    id = Column(Integer, primary_key=True)
    experiment_id = Column(Integer, ForeignKey('experiments.id'))
    experiment = relationship("Experiment", backref=backref('accepted_ims', order_by=id))
    time = Column(Float)
    lease_id = Column(Integer)
    count = Column(Integer)
    
class RejectedAR(Base):
    __tablename__ = 'rejected_ar'
    
    id = Column(Integer, primary_key=True)
    experiment_id = Column(Integer, ForeignKey('experiments.id'))
    experiment = relationship("Experiment", backref=backref('rejected_ars', order_by=id))
    time = Column(Float)
    lease_id = Column(Integer)
    count = Column(Integer)
    
class RejectedIM(Base):
    __tablename__ = 'rejected_im'
    
    id = Column(Integer, primary_key=True)
    experiment_id = Column(Integer, ForeignKey('experiments.id'))
    experiment = relationship("Experiment", backref=backref('rejected_ims', order_by=id))
    time = Column(Float)
    lease_id = Column(Integer)
    count = Column(Integer)
    
class CompletedBE(Base):
    __tablename__ = 'completed_be'
    
    id = Column(Integer, primary_key=True)
    experiment_id = Column(Integer, ForeignKey('experiments.id'))
    experiment = relationship("Experiment", backref=backref('completed_bes', order_by=id))
    time = Column(Float)
    lease_id = Column(Integer)
    count = Column(Integer)

class QueueSizeBE(Base):
    __tablename__ = 'queue_size_be'
    
    id = Column(Integer, primary_key=True)
    experiment_id = Column(Integer, ForeignKey('experiments.id'))
    experiment = relationship("Experiment", backref=backref('queue_size_bes', order_by=id))
    time = Column(Float)
    lease_id = Column(Integer)
    count = Column(Integer)