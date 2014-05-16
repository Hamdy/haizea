import pygal
from pygal.style import LightStyle

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
    
    def graph_probes(self, experiments, type):
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
            
        x_labels, data = self.prepare_probes_data(experiments, type)
        self.chart.x_labels = map(str, x_labels)
        for k, v in data.iteritems():
            self.chart.add(k, v)
            
        self.chart.render_in_browser()
    