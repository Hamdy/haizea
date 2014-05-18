import pygal
from pygal.style import LightStyle
import os
from datetime import datetime

class Graph(object):
    def __init__(self):
        self.chart = None

    def prepare_probes_data(self, experiments, type):
        # get data
        records = {}
        experiment_id_description = {}

        for e in experiments:
            experiment_id_description[e.id] = e.description
            
            db_records = []
            if type.endswith('accepted_ars'):
                db_records = e.accepted_ars
            elif type.endswith('rejected_ars'):
                db_records = e.rejected_ars
            elif type.endswith('accepted_ims'):
                db_records = e.accepted_ims
            elif type.endswith('rejected_ims'):
                db_records = e.rejected_ims
            elif type.endswith('completed_bes'):
                db_records = e.completed_bes
            elif type.endswith('queue_size_bes'):
                db_records = e.queue_size_bes
            
            for record in db_records:
                records[record.time] = records.get(record.time, {})
                records[record.time][e.id] = record.count

        # prepare for graphing
        x_labels = []
        data = {}
        
        for k in sorted(records):
            x_labels.append(k)
            for e in experiment_id_description:
                if e not in records[k]:
                    records[k][e] = None

            for k2, v2 in records[k].iteritems():
                desc = experiment_id_description[k2]
                data[desc] =  data.get(desc, [])
                data[desc].append(v2)
        
        return x_labels, data
    
    
    def prepare_utilization_data(self, experiments, type):
        # get data
        records = {}
        experiment_id_description = {}
        records_repetitions = {}
        x_labels = set()
        for e in experiments:
            experiment_id_description[e.id] = e.description
            
            db_records = []
            if type.endswith('cpu_avg_utilization'):
                db_records = e.pnodes_cpu_load
            elif type.endswith('memory_avg_utilization'):
                db_records = e.pnodes_memory_load
            elif type.endswith('disk_avg_utilization'):
                db_records = e.pnodes_disk_load
            elif type.endswith('net_in_avg_utilization'):
                db_records = e.pnodes_net_in_load
            elif type.endswith('net_out_avg_utilization'):
                db_records = e.pnodes_net_out_load

            
            for record in db_records:
                x_labels.add(record.node)
                records[e.id] = records.get(e.id, {})
                records_repetitions[e.id] = records_repetitions.get(e.id, {})

                if record.node not in records[e.id]:
                    records[e.id][record.node] = record.value
                    records_repetitions[e.id][record.node] = 1
                else:
                    records[e.id][record.node] = (records[e.id][record.node] + record.value)
                    records_repetitions[e.id][record.node] = records_repetitions[e.id][record.node] + 1
        
        x_labels = sorted(x_labels)
        data = {}
        
        for k, v in records.iteritems():
            res = []
            for e in x_labels:
                if e in v:
                    res.append(v[e] / records_repetitions[k][e])
                else:
                    res.append(None)
            data[experiment_id_description[k]] = res

        return x_labels, data
    
    def graph(self, experiments, type):
        if type.startswith('line'):
            self.chart = pygal.Line(style=LightStyle)
        else:
            self.chart = pygal.Bar(style=LightStyle)

        if type == "line_accepted_ars" or type == "bar_accepted_ars":
            self.chart.title = 'Number of Accepted Advance Reservation Leases through time (Mins)'
        elif type == "line_rejected_ars" or type == "bar_rejected_ars":
            self.chart.title = 'Number of Rejected Advance Reservation Leases through time (Mins) '
        elif type == "line_accepted_ims" or type == "bar_accepted_ims":
            self.chart.title = 'Number of Accepted Immediate Leases'
        elif type == "line_rejected_ims" or type == "bar_rejected_ims":
            self.chart.title = 'Number of Rejected Immediate Leases through time (Mins)'
        elif type == "line_completed_bes" or type == "bar_completed_bes": 
            self.chart.title = 'Number of Completed Best effort leases through time (Mins)'
        elif type == "line_queue_size_bes" or type == "bar_queue_size_bes": 
            self.chart.title = 'Queue size for Best effort leases through time (Mins)'
        elif type == "bar_cpu_avg_utilization": 
            self.chart.title = 'Average Cpu usages on physical nodes'
        elif type == "bar_memory_avg_utilization": 
            self.chart.title = 'Average Memory usages on physical nodes'
        elif type == "bar_disk_avg_utilization": 
            self.chart.title = 'Average Disk usages on physical nodes'
        elif type == "bar_net_in_avg_utilization": 
            self.chart.title = 'Average Net in bandwidth on physical nodes'
        elif type == "bar_net_out_avg_utilization": 
            self.chart.title = 'Average Net out bandwidth on physical nodes'
             
        if type.endswith('utilization'):
            x_labels, data = self.prepare_utilization_data(experiments, type)
        else:
            x_labels, data = self.prepare_probes_data(experiments, type)
        
        self.chart.x_labels = map(str, x_labels)
        for k, v in data.iteritems():
            self.chart.add(k, v)
        
        try:
            dir_path = os.path.expanduser("~/.haizea/graphs")
            if not os.path.exists(dir_path):
                os.mkdir(dir_path)
            file_name = str(datetime.now())
            self.chart.render_to_file("%s/chart-%s.svg" % (dir_path, file_name))
        except:
            pass
        
        self.chart.render_in_browser()
        
        
    