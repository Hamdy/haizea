# -------------------------------------------------------------------------- #
# Copyright 2006-2009, University of Chicago                                 #
# Copyright 2008-2009, Distributed Systems Architecture Group, Universidad   #
# Complutense de Madrid (dsa-research.org)                                   #
#                                                                            #
# Licensed under the Apache License, Version 2.0 (the "License"); you may    #
# not use this file except in compliance with the License. You may obtain    #
# a copy of the License at                                                   #
#                                                                            #
# http://www.apache.org/licenses/LICENSE-2.0                                 #
#                                                                            #
# Unless required by applicable law or agreed to in writing, software        #
# distributed under the License is distributed on an "AS IS" BASIS,          #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.   #
# See the License for the specific language governing permissions and        #
# limitations under the License.                                             #
# -------------------------------------------------------------------------- #
from haizea.pluggable.accounting.models import AcceptedAR, Experiment,\
    RejectedAR, AcceptedIM, RejectedIM, CompletedBE, QueueSizeBE,\
    LeaseStatistics

"""Accounting probes that collect data from leases"""

from haizea.core.accounting import AccountingProbe, AccountingDataCollection
from haizea.core.leases import Lease
                
class ARProbe(AccountingProbe):
    """
    Collects information from Advance Reservation leases
    
    * Counters
    
      - "Accepted AR": Number of accepted AR leases 
      - "Rejected AR": Number of rejected AR leases

    * Per-run data
    
      - "Total accepted AR": Final number of accepted AR leases
      - "Total rejected AR": Final number of rejected AR leases

    """
    COUNTER_ACCEPTED="Accepted AR"
    COUNTER_REJECTED="Rejected AR"
    STAT_ACCEPTED="Total accepted AR"
    STAT_REJECTED="Total rejected AR"
    
    def __init__(self, accounting):
        """See AccountingProbe.__init__"""
        AccountingProbe.__init__(self, accounting)
        self.accounting.create_counter(ARProbe.COUNTER_ACCEPTED, AccountingDataCollection.AVERAGE_NONE)
        self.accounting.create_counter(ARProbe.COUNTER_REJECTED, AccountingDataCollection.AVERAGE_NONE)
        self.accounting.create_stat(ARProbe.STAT_ACCEPTED)
        self.accounting.create_stat(ARProbe.STAT_REJECTED)

    def finalize_accounting(self, db):
        """See AccountingProbe.finalize_accounting"""        
        self._set_stat_from_counter(ARProbe.STAT_ACCEPTED, ARProbe.COUNTER_ACCEPTED)
        self._set_stat_from_counter(ARProbe.STAT_REJECTED, ARProbe.COUNTER_REJECTED)
        
        
        accepted_ars = []
        rejected_ars = []
        
        experiment = db.query(Experiment).order_by("-id").first()
        
        for e in self.accounting.data.counters[ARProbe.COUNTER_ACCEPTED]:
            d = {}
            d['experiment_id'] = experiment.id
            d['time'] = e[0] / 60.0
            d['lease_id'] = e[1]
            d['count'] = e[2]
            accepted_ars.append(d)
            
        for e in self.accounting.data.counters[ARProbe.COUNTER_REJECTED]:
            d = {}
            d['experiment_id'] = experiment.id
            d['time'] = e[0] / 60.0
            d['lease_id'] = e[1]
            d['count'] = e[2]
            rejected_ars.append(d)
        
        db.execute(AcceptedAR.__table__.insert(), accepted_ars)
        db.execute(RejectedAR.__table__.insert(), rejected_ars)

        #save stats
        experiment.total_accepted_ar = self.accounting.data.stats['Total accepted AR']
        experiment.total_rejected_ar = self.accounting.data.stats['Total rejected AR']
        
        db.commit()

    def at_lease_request(self, lease):
        """See AccountingProbe.at_lease_request"""                
        if lease.get_type() == Lease.ADVANCE_RESERVATION:
            if lease.get_state() == Lease.STATE_PENDING:
                self.accounting.incr_counter(ARProbe.COUNTER_ACCEPTED, lease.id)
            elif lease.get_state() == Lease.STATE_REJECTED:
                self.accounting.incr_counter(ARProbe.COUNTER_REJECTED, lease.id)

    def at_lease_done(self, lease):
        """See AccountingProbe.at_lease_done"""
        if lease.get_type() == Lease.ADVANCE_RESERVATION:
            if lease.get_state() == Lease.STATE_REJECTED:
                self.accounting.incr_counter(ARProbe.COUNTER_REJECTED, lease.id)


class IMProbe(AccountingProbe):
    """
    Collects information from immediate leases
    
    * Counters
    
      - "Accepted Immediate": Number of accepted Immediate leases 
      - "Rejected Immediate": Number of rejected Immediate leases

    * Per-run data
    
      - "Total accepted Immediate": Final number of accepted Immediate leases
      - "Total rejected Immediate": Final number of rejected Immediate leases

    """
    COUNTER_ACCEPTED="Accepted Immediate"
    COUNTER_REJECTED="Rejected Immediate"
    STAT_ACCEPTED="Total accepted Immediate"
    STAT_REJECTED="Total rejected Immediate"
    
    def __init__(self, accounting):
        """See AccountingProbe.__init__"""        
        AccountingProbe.__init__(self, accounting)
        self.accounting.create_counter(IMProbe.COUNTER_ACCEPTED, AccountingDataCollection.AVERAGE_NONE)
        self.accounting.create_counter(IMProbe.COUNTER_REJECTED, AccountingDataCollection.AVERAGE_NONE)
        self.accounting.create_stat(IMProbe.STAT_ACCEPTED)
        self.accounting.create_stat(IMProbe.STAT_REJECTED)

    def finalize_accounting(self, db):
        """See AccountingProbe.finalize_accounting"""        
        self._set_stat_from_counter(IMProbe.STAT_ACCEPTED, IMProbe.COUNTER_ACCEPTED)
        self._set_stat_from_counter(IMProbe.STAT_REJECTED, IMProbe.COUNTER_REJECTED)
        
        accepted_ims = []
        rejected_ims = []
        
        experiment = db.query(Experiment).order_by("-id").first()
        
        for e in self.accounting.data.counters[IMProbe.COUNTER_ACCEPTED]:
            d = {}
            d['experiment_id'] = experiment.id
            d['time'] = e[0] / 60.0
            d['lease_id'] = e[1]
            d['count'] = e[2]
            accepted_ims.append(d)
            
        for e in self.accounting.data.counters[IMProbe.COUNTER_REJECTED]:
            d = {}
            d['experiment_id'] = experiment.id
            d['time'] = e[0] / 60.0
            d['lease_id'] = e[1]
            d['count'] = e[2]
            rejected_ims.append(d)
        
        #save stats
        experiment.total_accepted_im = self.accounting.data.stats['Total accepted Immediate']
        experiment.total_rejected_im = self.accounting.data.stats['Total rejected Immediate']
        
        db.execute(AcceptedIM.__table__.insert(), accepted_ims)
        db.execute(RejectedIM.__table__.insert(), rejected_ims)
        
        db.commit()


    def at_lease_request(self, lease):
        """See AccountingProbe.at_lease_request"""                        
        if lease.get_type() == Lease.IMMEDIATE:
            if lease.get_state() == Lease.STATE_PENDING:
                self.accounting.incr_counter(IMProbe.COUNTER_ACCEPTED, lease.id)
            elif lease.get_state() == Lease.STATE_REJECTED:
                self.accounting.incr_counter(IMProbe.COUNTER_REJECTED, lease.id)

    def at_lease_done(self, lease):
        """See AccountingProbe.at_lease_done"""        
        if lease.get_type() == Lease.IMMEDIATE:
            if lease.get_state() == Lease.STATE_REJECTED:
                self.accounting.incr_counter(IMProbe.COUNTER_REJECTED, lease.id)


class BEProbe(AccountingProbe):
    """
    Collects information from best-effort leases
    
    * Counters
    
      - "Best-effort completed": Number of best-effort leases completed
        throughout the run
      - "Queue size": Size of the queue throughout the run

    * Per-lease data
    
      - "Waiting time": Time (in seconds) the lease waited in the queue
        before resources were allocated to it.
      - "Slowdown": Slowdown of the lease (time required to run the lease
        to completion divided by the time it would have required on a
        dedicated system)

    * Per-run data
    
      - "Total best-effort completed": Final number of completed best-effort leases
      - "all-best-effort": The time (in seconds) when the last best-effort
        lease was completed.

    """
        
    COUNTER_BESTEFFORTCOMPLETED="Best-effort completed"
    COUNTER_QUEUESIZE="Queue size"
    LEASE_STAT_WAITINGTIME="Waiting time"
    LEASE_STAT_SLOWDOWN="Slowdown"
    STAT_BESTEFFORTCOMPLETED="Total best-effort completed"
    STAT_ALLBESTEFFORT="all-best-effort"
    
    
    def __init__(self, accounting):
        """See AccountingProbe.__init__"""
        AccountingProbe.__init__(self, accounting)
        self.accounting.create_counter(BEProbe.COUNTER_BESTEFFORTCOMPLETED, AccountingDataCollection.AVERAGE_NONE)
        self.accounting.create_counter(BEProbe.COUNTER_QUEUESIZE, AccountingDataCollection.AVERAGE_TIMEWEIGHTED)
        self.accounting.create_lease_stat(BEProbe.LEASE_STAT_WAITINGTIME)
        self.accounting.create_lease_stat(BEProbe.LEASE_STAT_SLOWDOWN)
        self.accounting.create_stat(BEProbe.STAT_BESTEFFORTCOMPLETED)
        self.accounting.create_stat(BEProbe.STAT_ALLBESTEFFORT)
    
    def finalize_accounting(self, db):
        """See AccountingProbe.finalize_accounting"""        
        self._set_stat_from_counter(BEProbe.STAT_BESTEFFORTCOMPLETED, BEProbe.COUNTER_BESTEFFORTCOMPLETED)
        all_best_effort = self.accounting.get_last_counter_time(BEProbe.COUNTER_BESTEFFORTCOMPLETED)
        self.accounting.set_stat(BEProbe.STAT_ALLBESTEFFORT, all_best_effort)
        
        completed_bes = []
        queue_size_bes = []
        lease_stats = []
        
        experiment = db.query(Experiment).order_by("-id").first()
        
        for e in self.accounting.data.counters[BEProbe.COUNTER_BESTEFFORTCOMPLETED]:
            d = {}
            d['experiment_id'] = experiment.id
            d['time'] = e[0] / 60.0
            d['lease_id'] = e[1]
            d['count'] = e[2]
            completed_bes.append(d)
            
        for e in self.accounting.data.counters[BEProbe.COUNTER_QUEUESIZE]:
            d = {}
            d['experiment_id'] = experiment.id
            d['time'] = e[0] / 60.0
            d['lease_id'] = e[1]
            d['count'] = e[2]
            queue_size_bes.append(d)
        
        for k, v in self.accounting.data.lease_stats.iteritems():
            d = {}
            d['experiment_id'] = experiment.id
            d['lease_id'] = k
            d['waiting_time'] = v['Waiting time']/60.0
            d['slowdown'] = v['Slowdown']
            lease_stats.append(d)
        
        #save stats
        experiment.total_completed_be = self.accounting.data.stats['Total best-effort completed']
        experiment.be_completed_after = self.accounting.data.stats['all-best-effort'] / 60.0
        
        db.execute(CompletedBE.__table__.insert(), completed_bes)
        db.execute(QueueSizeBE.__table__.insert(), queue_size_bes)
        db.execute(LeaseStatistics.__table__.insert(), lease_stats)
        db.commit()
        
    def at_timestep(self, lease_scheduler):
        """See AccountingProbe.at_timestep"""        
        queue_len = lease_scheduler.queue.length()
        self.accounting.append_to_counter(BEProbe.COUNTER_QUEUESIZE, queue_len)

    def at_lease_done(self, lease):
        """See AccountingProbe.at_lease_done"""                        
        if lease.get_type() == Lease.BEST_EFFORT:
            wait = lease.get_waiting_time().seconds
            self.accounting.set_lease_stat(BEProbe.LEASE_STAT_WAITINGTIME, lease.id, wait)
            self.accounting.set_lease_stat(BEProbe.LEASE_STAT_SLOWDOWN, lease.id, lease.get_slowdown())
            self.accounting.incr_counter(BEProbe.COUNTER_BESTEFFORTCOMPLETED, lease.id)
