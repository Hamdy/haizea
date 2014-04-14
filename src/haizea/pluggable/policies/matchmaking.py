class Condor(object):
    def __init__(self, slottable):
        self.slottable = slottable

    def host_score(self, pnode, vnode_capacity):
        vnode_cpu = vnode_capacity.get_by_type("CPU")
        vnode_memory = vnode_capacity.get_by_type("Memory")
        vnode_net_in = vnode_capacity.get_by_type("Net-in")
        vnode_net_out = vnode_capacity.get_by_type("Net-out")
        vnode_disk = vnode_capacity.get_by_type("Disk")
        
        pnode_capacity = self.slottable.nodes[pnode].capacity
        pnode_cpu = pnode_capacity.get_by_type("CPU")
        pnode_memory = pnode_capacity.get_by_type("Memory")
        pnode_net_in = pnode_capacity.get_by_type("Net-in")
        pnode_net_out = pnode_capacity.get_by_type("Net-out")
        pnode_disk = pnode_capacity.get_by_type("Disk")
        
        
        if pnode_disk < vnode_disk:
            return 0
        elif pnode_memory < vnode_memory:
            return 0
        elif pnode_cpu < vnode_cpu:
            return 0
        elif pnode_net_in < vnode_net_in:
            return 0
        elif pnode_net_out < vnode_net_out:
            return 0
        
        score = 0.0
        
        if pnode_disk == vnode_disk:
            score += 1
        else:
            score += 1 - (pnode_disk - vnode_disk) / pnode_disk
        
        if pnode_memory == vnode_memory:
            score += 1
        else:
            score += 1 - (pnode_memory - vnode_memory) / pnode_memory
        
        if pnode_cpu == vnode_cpu:
            score += 1
        else:
            score += 1 - (pnode_cpu - vnode_cpu) / pnode_cpu
        
        if pnode_net_in == vnode_net_in:
            score += 1
        else:
            score += 1 - (pnode_net_in - vnode_net_in) / pnode_net_in
        
        if pnode_net_out == vnode_net_out:
            score += 1
        else:
            score += 1 - (pnode_net_out - vnode_net_out) / pnode_net_out
 
        return score / 5.0

    def lease_score(self):
        return 1
    
    def get_pnodes(self, vnode_capacity, pnode_ids,lease):
        result = []
        for pnode in pnode_ids:
            host_score = self.host_score(pnode, vnode_capacity)
            if host_score == 0.0:
                continue
            
            lease_score = self.lease_score()
            
            if lease_score == 0.0:
                continue
            
            avg_score = (host_score + lease_score) / 2.0
            result.append((pnode, avg_score))
            
        result.sort(key=lambda tup:tup[1], reverse=True)
        
        return [e[0] for e in result]