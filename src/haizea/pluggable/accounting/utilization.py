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
from haizea.common import constants

"""Accounting probes that collect data on resource utilization"""

from haizea.core.accounting import AccountingProbe, AccountingDataCollection
from haizea.common.utils import get_clock

class CPUUtilizationProbe(AccountingProbe):
    """
    Collects information on CPU utilization
    
    * Counters
    
      - "CPU utilization": Amount of CPU resources used in the entire site
        at a given time. The value ranges between 0 and 1.

    """    
    COUNTER_UTILIZATION="CPU utilization"        
    
    def __init__(self, accounting):
        """See AccountingProbe.__init__"""        
        AccountingProbe.__init__(self, accounting)
        self.accounting.create_counter(CPUUtilizationProbe.COUNTER_UTILIZATION, AccountingDataCollection.AVERAGE_TIMEWEIGHTED)
        
    def at_timestep(self, lease_scheduler):
        """See AccountingProbe.at_timestep"""
        util = lease_scheduler.vm_scheduler.get_utilization(get_clock().get_time())
        utilization = sum([v for k,v in util.items() if k != None])
        self.accounting.append_to_counter(CPUUtilizationProbe.COUNTER_UTILIZATION, utilization)
        
    def finalize_accounting(self, db):
        pass
    
class CpuLoadOnPhysicalNodes(AccountingProbe):
    COUNTER_CPU_LOAD_ON_PNODE="cpu_pnode"
    
    def __init__(self, accounting):
        """See AccountingProbe.__init__"""        
        AccountingProbe.__init__(self, accounting)
        self.accounting.create_counter(CpuLoadOnPhysicalNodes.COUNTER_CPU_LOAD_ON_PNODE, AccountingDataCollection.AVERAGE_NONE)
        self.all_pnode_capacities = {}
        
    def at_timestep(self, lease_scheduler):
        # Total cpu utilization of node (node_cpu at time stamp / total node cpu)  
        util = {}
        reservations = lease_scheduler.vm_scheduler.slottable.get_reservations_at(get_clock().get_time())
        for r in reservations:
            
            for node in r.resources_in_pnode:
                use = r.resources_in_pnode[node].get_by_type(constants.RES_CPU)
                util[node] = use + util.get(node, 0.0)
        self.accounting.append_to_counter(CpuLoadOnPhysicalNodes.COUNTER_CPU_LOAD_ON_PNODE, util)
        if not self.all_pnode_capacities:
            for pnode, cpacity in lease_scheduler.vm_scheduler.slottable.nodes.iteritems():
                self.all_pnode_capacities[pnode] = cpacity.capacity.get_by_type(constants.RES_CPU)  
        
    def finalize_accounting(self, db):
        pass
    

class DiskUsageProbe(AccountingProbe):
    """
    Collects information on disk usage
    
    * Counters
    
      - "Disk usage": Maximum disk space used across nodes.

    """    
    COUNTER_DISKUSAGE="Disk usage"
    
    def __init__(self, accounting):
        """See AccountingProbe.__init__"""        
        AccountingProbe.__init__(self, accounting)
        self.accounting.create_counter(DiskUsageProbe.COUNTER_DISKUSAGE, AccountingDataCollection.AVERAGE_NONE)
        
    def at_timestep(self, lease_scheduler):
        """See AccountingProbe.at_timestep"""
        usage = lease_scheduler.vm_scheduler.resourcepool.get_max_disk_usage()
        self.accounting.append_to_counter(DiskUsageProbe.COUNTER_DISKUSAGE, usage)
    
    def finalize_accounting(self, db):
        pass
    
