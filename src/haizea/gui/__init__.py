import sys
import logging
from haizea.core import manager as manager_module
from haizea.core import accounting as accounting_module
from gi.repository import Gtk
from mx.DateTime import TimeDelta, DateTime
from datetime import datetime

import os
from haizea.core.leases import Capacity, Nodes
from haizea.pluggable.accounting import Database
from haizea.pluggable.accounting.models import Experiment
from haizea.pluggable.accounting.graph import Graph

class TextAreaLoggingHandler(logging.Handler):
    def __init__(self, widget):
        logging.Handler.__init__(self)
        self.widget = widget
    
    def write(self, record):
        text = self.widget.get_text()
        self.widget.set_text("%s\n%s" % (text, record))
    
    def emit(self, record):
        text = self.widget.get_text()
        self.widget.set_text('%(text)s\n[%(haizeatime)s] %(name)-7s %(message)s' % {'text':text, 'haizeatime':record.haizeatime, 'message':record.msg, 'name':record.name})
        self.flush()

class HaizeaGuiApp(object):       
    def __init__(self, Manager, config, pidfile):
        self.config = config
        self.builder = Gtk.Builder()
        self.builder.add_from_file(''.join(os.path.join([os.path.dirname(__file__), os.sep, 'app.glade'])))
        self.builder.connect_signals(self)
        self.window = self.builder.get_object("window1")
        self.window.connect("delete-event", Gtk.main_quit)
        
        self.console = self.builder.get_object("console")
        self.gui_loggin_handler = TextAreaLoggingHandler(self.console)
        
        self.manager = Manager(config, False, logging_handler=self.gui_loggin_handler)
        self.site = self.manager.site
        
        # Load configuration values in UI
        self.reload_configuration()
        self.reload_physical_nodes()
        self.reload_experiments()
        
    
    def change_loglevel_callback(self, *args):
        loglevel_value = self.builder.get_object('loglevel').get_active_id()
        self.config._options['loglevel'] = loglevel_value
    
    def lease_preparation_changed_callback(self, *args):
        lease_prep_value = self.builder.get_object('lease_preparation').get_active_id()
        self.config._options['lease-preparation'] = lease_prep_value
        
    def lease_failure_handling_callback(self, *args):
        lease_failure_handling_value = self.builder.get_object('lease_failure_handling').get_active_id()
        self.config._options['lease-failure-handling'] = lease_failure_handling_value
        
    def mapper_changed_callback(self, *args):
        mapper_value = self.builder.get_object('mapper').get_active_id()
        self.config._options['mapper'] = mapper_value
        
    def admission_policy_changed_callback(self, *args):
        value = self.builder.get_object('policy-admission').get_active_id()
        self.config._options['policy.admission'] = value
        
    def preemption_policy_changed_callback(self, *args):
        value = self.builder.get_object('policy-preemption').get_active_id()
        self.config._options['policy.preemption'] = value
   

    def wakeup_interval_changed_callback(self, *args):
        h, m, s = (self.builder.get_object('wakeup-interval-hours').get_text(),
            self.builder.get_object('wakeup-interval-minutes').get_text(),
            self.builder.get_object('wakeup-interval-seconds').get_text())
     
        if not h:
            h = 0
        if not s:
            s = 0
        if not m:
            m = 0
        try:
            self.config._options['wakeup-interval'] = TimeDelta(seconds=int(s), minutes=int(m), hours=int(h))
        except:
            print "Invalid Wakeup interval value"
            self.config._options['wakeup-interval'] = TimeDelta(seconds=10)
    
    def backfilling_changed_callback(self, *args):
        val = self.builder.get_object('backfilling').get_active_id()
        self.config._options['backfilling'] = val
        backfilling_reservatons =  self.builder.get_object('backfilling-reservations')
        backfilling_reservatons_label =  self.builder.get_object('backfilling-reservations-label')
        
        if val == 'intermediate':
            backfilling_reservatons.show()
            backfilling_reservatons_label.show()
        else:
            backfilling_reservatons.hide()
            backfilling_reservatons_label.hide()

    def backfilling_reservations_changed_callback(self, *args):
        try:
            val = int(self.builder.get_object('backfilling-reservations').get_text())
        except:
            val = 0
        
        self.config._options['backfilling-reservations'] = val
    
    def suspension_changed_callback(self, *args):
        self.config._options['suspension'] = self.builder.get_object('suspension').get_active_id()

    def suspend_rate_changed_callback(self, *args):
        try:
            val = float(self.builder.get_object('suspend-rate').get_text())
        except:
            val = 32.0
        self.config._options['suspend-rate'] = val

    def resume_rate_changed_callback(self, *args):
        try:
            val = float(self.builder.get_object('resume-rate').get_text())
        except:
            val = 32.0
        self.config._options['resume-rate'] = val
        
    def suspendresume_exclusion_changed_callback(self, *args):
        self.config._options['suspendresume-exclusion'] = self.builder.get_object('suspendresume-exclusion').get_active_id()

    def scheduling_threshold_factor_changed_callback(self, *args):
        try:
            val = int(self.builder.get_object('scheduling-threshold-factor').get_text())
        except:
            val = 1
        self.config._options['scheduling-threshold-factor'] = val
    
    def override_suspend_time_changed_callback(self, *args):
        try:
            val = int(self.builder.get_object('override-suspend-time').get_text())
        except:
            val = None
        self.config._options['override-suspend-time'] = val
        
    def override_resume_time_changed_callback(self, *args):
        try:
            val = int(self.builder.get_object('override-resume-time').get_text())
        except:
            val = None
        self.config._options['override-resume-time'] = val

    def migration_changed_callback(self, *args):
        self.config._options['migration'] = self.builder.get_object('migration').get_active_id()

    def force_scheduling_threshold_changed_callback(self, *args):
        h, m, s = (self.builder.get_object('force-scheduling-threshold-hours').get_text(),
            self.builder.get_object('force-scheduling-threshold-minutes').get_text(),
            self.builder.get_object('force-scheduling-threshold-seconds').get_text())
     
        if not h:
            h = 0
        if not s:
            s = 0
        if not m:
            m = 0
        try:
            self.config._options['force-scheduling-threshold'] = TimeDelta(seconds=int(s), minutes=int(m), hours=int(h))
        except:
            print "Invalid Wakeup interval value"
            self.config._options['force-scheduling-threshold'] = None
    
    def non_schedulable_interval_changed_callback(self, *args):
        h, m, s = (self.builder.get_object('non-schedulable-interval-hours').get_text(),
            self.builder.get_object('non-schedulable-interval-minutes').get_text(),
            self.builder.get_object('non-schedulable-interval-seconds').get_text())
     
        if not h:
            h = 0
        if not s:
            s = 0
        if not m:
            m = 0
        try:
            self.config._options['non-schedulable-interval'] = TimeDelta(seconds=int(s), minutes=int(m), hours=int(h))
        except:
            print "Invalid non-schedulable-interval value"
            self.config._options['non-schedulable-interval'] = None
        

    def shutdown_time_changed_callback(self, *args):
            h, m, s = (self.builder.get_object('shutdown-time-hours').get_text(),
                self.builder.get_object('shutdown-time-minutes').get_text(),
                self.builder.get_object('shutdown-time-seconds').get_text())
         
            if not h:
                h = 0
            if not s:
                s = 0
            if not m:
                m = 0
            try:
                self.config._options['shutdown-time'] = TimeDelta(seconds=int(s), minutes=int(m), hours=int(h))
            except:
                print "Invalid shutdown-time value"
                self.config._options['shutdown-time'] = None

    def enactment_overhead_changed_callback(self, *args):
            h, m, s = (self.builder.get_object('enactment-overhead-hours').get_text(),
                self.builder.get_object('enactment-overhead-minutes').get_text(),
                self.builder.get_object('enactment-overhead-seconds').get_text())
         
            if not h:
                h = 0
            if not s:
                s = 0
            if not m:
                m = 0
            try:
                self.config._options['enactment-overhead'] = TimeDelta(seconds=int(s), minutes=int(m), hours=int(h))
            except:
                print "Invalid enactment-overhead value"
                self.config._options['enactment-overhead'] = None

    def imagetransfer_bandwidth_changed_callback(self, *args):
        try:
            val = int(self.builder.get_object('imagetransfer-bandwidth').get_text())
        except:
            val = 100
        self.config._options['imagetransfer-bandwidth'] = val
    
    def stop_when_changed_callback(self, *args):
        self.config._options['stop-when'] = self.builder.get_object('stop-when').get_active_id()
    
    def status_message_interval_changed_callback(self, *args):
        try:
            val = int(self.builder.get_object('status-message-interval').get_text())
        except:
            val = None
        self.config._options['status-message-interval'] = val

    def probes_changed_callback(self, *args):
        if self.probe_initializing:
            return
        
        probes = []
 
        if self.builder.get_object('ar').get_active():
            probes.append('ar')
             
        if self.builder.get_object('best-effort').get_active():
            probes.append('best-effort')
             
        if self.builder.get_object('immediate').get_active():
            probes.append('immediate')
         
        if self.builder.get_object('cpu_pnodes').get_active():
            probes.append('cpu_pnodes')
         
        if self.builder.get_object('disk_pnodes').get_active():
            probes.append('disk_pnodes')
         
        if self.builder.get_object('memory_pnodes').get_active():
            probes.append('memory_pnodes')
             
        if self.builder.get_object('net_in_pnodes').get_active():
            probes.append('net_in_pnodes')
         
        if self.builder.get_object('net_out_pnodes').get_active():
            probes.append('net_out_pnodes')
             
        self.config._options["accounting-probes"] = ' '.join(probes)
    
    def db_folder_changed_callback(self, *args):
        self.config._options["datafile"] = ''.join(os.path.join([self.builder.get_object('db_folder').get_filename(), os.sep, 'results.dat']))
        # reload db module so that 
        import haizea.pluggable.accounting as acc
        reload(acc)
        self.reload_experiments()

    def transfer_mechanism_changed_callback(self, *args):
        self.config._options['transfer-mechanism'] = self.builder.get_object('transfer-mechanism').get_active_id()

    def avoid_redundant_transfers_changed_callback(self, *args):
        val = True if self.builder.get_object('avoid-redundant-transfers').get_active_id() == "True" else False
        self.config._options['avoid-redundant-transfers'] = val

    def diskimage_reuse_changed_callback(self, *args):
        val = self.builder.get_object('diskimage-reuse').get_active_id()
        self.config._options['diskimage-reuse'] = val
        
        if val != 'none':
            self.builder.get_object('diskimage-cache-size').show()
            self.builder.get_object('diskimage-cache-size-label').show()
            self.builder.get_object('diskimage-cache-size-label2').show()
        else:
            self.builder.get_object('diskimage-cache-size').hide()
            self.builder.get_object('diskimage-cache-size-label').hide()
            self.builder.get_object('diskimage-cache-size-label2').hide()
        
        
    def diskimage_cache_size_changed_callback(self, *args):
        try:
            val = int(self.builder.get_object('diskimage-cache-size').get_text())
        except:
            val = 20480
        self.config._options['diskimage-cache-size'] = val

    def force_imagetransfer_time_changed_callback(self, *args):
        h, m, s = (self.builder.get_object('force-imagetransfer-time-hours').get_text(),
                self.builder.get_object('force-imagetransfer-time-minutes').get_text(),
                self.builder.get_object('force-imagetransfer-time-seconds').get_text())
         
        if not h:
            h = 0
        if not s:
            s = 0
        if not m:
            m = 0
        try:
            self.config._options['force-imagetransfer-time'] = TimeDelta(seconds=int(s), minutes=int(m), hours=int(h))
        except:
            print "Invalidforce-imagetransfer-time value"
            self.config._options['force-imagetransfer-time'] = None

    def runtime_slowdown_overhead_changed_callback(self, *args):
        try:
            val = int(self.builder.get_object('runtime-slowdown-overhead').get_text())
        except:
            val = None
        self.config._options['runtime-slowdown-overhead'] = val
    
    def add_overhead_changed_callback(self, *args):
        val = self.builder.get_object('add-overhead').get_active_id()
        self.config._options['add-overhead'] = val
        if val == 'none':
            self.builder.get_object('runtime-slowdown-overhead').hide()
            self.builder.get_object('runtime-slowdown-overhead-label').hide()
            self.builder.get_object('runtime-slowdown-overhead-label2').hide()
        else:
            self.builder.get_object('runtime-slowdown-overhead').show()
            self.builder.get_object('runtime-slowdown-overhead-label').show()
            self.builder.get_object('runtime-slowdown-overhead-label2').show()

    def bootshutdown_overhead_changed_callback(self, *args):
        h, m, s = (self.builder.get_object('bootshutdown-overhead-hours').get_text(),
                self.builder.get_object('bootshutdown-overhead-minutes').get_text(),
                self.builder.get_object('bootshutdown-overhead-seconds').get_text())
         
        if not h:
            h = 0
        if not s:
            s = 0
        if not m:
            m = 0
        try:
            self.config._options['bootshutdown-overhead'] = TimeDelta(seconds=int(s), minutes=int(m), hours=int(h))
        except:
            print "Invalid bootshutdown-overhead value"
            self.config._options['bootshutdown-overhead'] = None
    
    def add_remove_node_set_callback(self, button):
        if button.get_active():
            self.node_sets_to_be_removed.append(button)
        else:
            if button in self.node_sets_to_be_removed:
                self.node_sets_to_be_removed.remove(button)
    
    def delete_selected_button_clicked_callback(self, *args):
        
        for button in self.node_sets_to_be_removed:
            self.site.nodes.node_sets.remove(button.node_set)
            button.destroy()
        self.node_sets_to_be_removed = []
        select_all = self.builder.get_object('select_all')
        if select_all.get_active():
            select_all.set_active(False)
        
    
    def select_all_toggled_callback(self, *args):
        select_all = self.builder.get_object('select_all')
        state = select_all.get_active()
        for row in self.builder.get_object('pnode_area').get_children():
            for button in row.get_children():
                button.set_active(state)
    
    def add_physical_node_clicked_callback(self, *args):
        try:
            count = int(self.builder.get_object('num_nodes').get_text())
            cpu = int(self.builder.get_object('nodeset_cpu').get_text())
            mem = int(self.builder.get_object('nodeset_memory').get_text())
            disk = int(self.builder.get_object('nodeset_disk').get_text())
            net_in = int(self.builder.get_object('nodeset_net_in').get_text())
            net_out = int(self.builder.get_object('nodeset_net_out').get_text())
            
            capacity = Capacity(['Net-in', 'Net-out', 'Disk', 'CPU', 'Memory'])
            capacity.set_quantity('Net-in', net_in)
            capacity.set_quantity('Net-out', net_out)
            capacity.set_quantity('Disk', disk)
            capacity.set_quantity('CPU', cpu)
            capacity.set_quantity('Memory', mem)
            self.site.nodes.node_sets.append((count,capacity))
            self.reload_physical_nodes()
        except:
            pass
    
    def clear_physical_nodes_area(self):
        for row in self.builder.get_object('pnode_area').get_children():
            for button in row.get_children():
                button.destroy()
        self.node_sets_to_be_removed = []
        
    
    def reload_physical_nodes(self):
        self.node_sets_to_be_removed = []
        pnode_area = self.builder.get_object('pnode_area')
        
        # clear area
        self.clear_physical_nodes_area()
        
        # Re add
        for e in self.site.nodes.node_sets:
            button = Gtk.CheckButton(str(e))
            button.node_set = e
            button.connect("toggled", self.add_remove_node_set_callback)
            pnode_area.add(button)
            button.show()

    def add_remove_experiment_callback(self, button):
        if button.get_active():
            self.experiments_waiting_for_action.append(button)
        else:
            if button in self.experiments_waiting_for_action:
                self.experiments_waiting_for_action.remove(button)
    
    
    def select_all_experiments_toggled_callback(self, *args):
        select_all = self.builder.get_object('select-all-experiments')
        state = select_all.get_active()
        for row in self.builder.get_object('experiments_area').get_children():
            for button in row.get_children():
                button.set_active(state)
    
    def experiments_go_clicked_callback(self, *args):
        action = self.builder.get_object('experiments_actions').get_active_id()
        experiments =  self.db.query(Experiment).filter(Experiment.id.in_([b.experiment.id for b in self.experiments_waiting_for_action]))
        if action == 'delete':
            experiments.delete(synchronize_session=False)
            self.db.commit()
            
            for button in self.experiments_waiting_for_action:
                button.destroy()
        
        else:
            g = Graph()
            g.graph(experiments, action)
            
            for row in self.builder.get_object('experiments_area').get_children():
                for button in row.get_children():
                    if button in self.experiments_waiting_for_action:
                        button.set_active(False)

        self.experiments_waiting_for_action = []
        select_all = self.builder.get_object('select-all-experiments')
        if select_all.get_active():
            select_all.set_active(False)
    
    def reload_experiments(self):
        self.experiments_waiting_for_action = []
        experimets_area = self.builder.get_object('experiments_area')
        
        for row in self.builder.get_object('experiments_area').get_children():
            for button in row.get_children():
                button.destroy()
            row.destroy()
        
        self.db = Database(os.path.expanduser(self.config.get("datafile"))).db
        
        for e in self.db.query(Experiment).order_by("-id").all():
            button = Gtk.CheckButton("%s  %s" % (e.id, e.description))
            button.experiment = e
            button.connect("toggled", self.add_remove_experiment_callback)
            experimets_area.add(button)
            button.show()

    def reload_configuration(self):
        
        # Loglevel
        loglevel_value = self.config.get("loglevel")
        loglevel = self.builder.get_object('loglevel')
        loglevel.set_active_id(loglevel_value)
        
        # Mode always simulated for now
        self.config._options["mode"] = "simulated"
        self.config._options["policy-host-selection"] = "greedy"
        self.config._options["policy-matchmaking"] = "condor"
        self.config._options['clock'] = 'simulated'
        self.config._options['override-memory'] = -1 #no memory override
        now = datetime.now()
        
        self.config._options['starttime'] = DateTime(now.year, now.month, now.day, now.hour, now.minute, now.second)
        
        
        # Lease preparation
        lease_preparation_value = self.config.get("lease-preparation")
        lease_prep = self.builder.get_object('lease_preparation')
        lease_prep.set_active_id(lease_preparation_value)
        
        # lease failure handking
        lease_failure_handling_value = self.config.get("lease-failure-handling")
        lease_failure_handling = self.builder.get_object('lease_failure_handling')
        lease_failure_handling.set_active_id(lease_failure_handling_value)
        
        # mapper
        mapper_value = self.config.get("mapper")
        mapper = self.builder.get_object('mapper')
        mapper.set_active_id(mapper_value)
        
        # admission policy
        self.builder.get_object('policy-admission').set_active_id(self.config.get("policy.admission"))
        
        # preemption policy
        self.builder.get_object('policy-preemption').set_active_id(self.config.get("policy.preemption"))
        
        # wakeup interval
        h, m, s = (self.builder.get_object('wakeup-interval-hours'),
            self.builder.get_object('wakeup-interval-minutes'),
            self.builder.get_object('wakeup-interval-seconds'))
        
        values = str(self.config.get("wakeup-interval")).split(":")
        
        h.set_text(values[0])
        m.set_text(values[1])
        s.set_text(values[2].split('.')[0])
        
        # backfilling
        self.builder.get_object('backfilling').set_active_id(self.config.get("backfilling"))
        
        # backfilling reservations
        backfilling_reservations = self.builder.get_object('backfilling-reservations')
        backfilling_reservations.set_text(self.config.get("backfilling-reservations") or '')
        
        if self.config.get("backfilling") != 'intermediate':
            self.builder.get_object('backfilling-reservations-label').hide()
            backfilling_reservations.hide()
        
        # suspension
        self.builder.get_object('suspension').set_active_id(self.config.get("suspension"))
        
        # suspend rate
        self.builder.get_object('suspend-rate').set_text(str(self.config.get("suspend-rate")))

        # resume rate
        self.builder.get_object('resume-rate').set_text(str(self.config.get("resume-rate")))

        # suspendresume-exclusion
        self.builder.get_object('suspendresume-exclusion').set_active_id(self.config.get("suspendresume-exclusion"))

        # scheduling-threshold-factor
        self.builder.get_object('scheduling-threshold-factor').set_text(str(self.config.get("scheduling-threshold-factor")))
        
        # override-suspend-time
        self.builder.get_object('override-suspend-time').set_text(str(self.config.get("override-suspend-time") or ''))

        # override-resume-time
        self.builder.get_object('override-resume-time').set_text(str(self.config.get("override-resume-time") or ''))
        
        # migration
        self.builder.get_object('migration').set_active_id(self.config.get("migration"))


        # force-scheduling-threshold
        h, m, s = (self.builder.get_object('force-scheduling-threshold-hours'),
            self.builder.get_object('force-scheduling-threshold-minutes'),
            self.builder.get_object('force-scheduling-threshold-seconds'))
        
        values = self.config.get("force-scheduling-threshold")
        values = str(values).split(":") if values else ('', '', '')
        h.set_text(values[0])
        m.set_text(values[1]  )
        s.set_text(values[2].split('.')[0])
        
        # non-schedulable-interval
        h, m, s = (self.builder.get_object('non-schedulable-interval-hours'),
            self.builder.get_object('non-schedulable-interval-minutes'),
            self.builder.get_object('non-schedulable-interval-seconds'))
        
        values = str(self.config.get("non-schedulable-interval"))
        values = values.split(":") if values else ('', '', '')
        
        h.set_text(values[0])
        m.set_text(values[1])
        s.set_text(values[2].split('.')[0])
        
        # shutdown-time
        h, m, s = (self.builder.get_object('shutdown-time-hours'),
            self.builder.get_object('shutdown-time-minutes'),
            self.builder.get_object('shutdown-time-seconds'))
        
        values = self.config.get("shutdown-time")
        values = str(values).split(":") if values else ('', '', '')
        h.set_text(values[0])
        m.set_text(values[1])
        s.set_text(values[2].split('.')[0])
        
        # enactment-overhead
        h, m, s = (self.builder.get_object('enactment-overhead-hours'),
            self.builder.get_object('enactment-overhead-minutes'),
            self.builder.get_object('enactment-overhead-seconds'))
        
        values = self.config.get("enactment-overhead")
        values = str(values).split(":") if values else ('', '', '')
        h.set_text(values[0])
        m.set_text(values[1])
        s.set_text(values[2].split('.')[0])
        
        # imagetransfer-bandwidth
        self.builder.get_object('imagetransfer-bandwidth').set_text(str(self.config.get("imagetransfer-bandwidth")))
        
        #stop-when
        self.builder.get_object('stop-when').set_active_id(self.config.get("stop-when"))
        
        # status-message-interval
        self.builder.get_object('status-message-interval').set_text(str(self.config.get("status-message-interval") or '') )
        
        # probes
        
        self.probe_initializing = True
        
        if "ar" in self.config.get("accounting-probes"):
            self.builder.get_object('ar').set_active(True)
        
        if "best-effort" in self.config.get("accounting-probes"):
            self.builder.get_object('best-effort').set_active(True)
        
        if "immediate" in self.config.get("accounting-probes"):
            self.builder.get_object('immediate').set_active(True)
            
        if "cpu_pnodes" in self.config.get("accounting-probes"):
            self.builder.get_object('cpu_pnodes').set_active(True)
            
        if "disk_pnodes" in self.config.get("accounting-probes"):
            self.builder.get_object('disk_pnodes').set_active(True)
            
        if "memory_pnodes" in self.config.get("accounting-probes"):
            self.builder.get_object('memory_pnodes').set_active(True)
            
        if "net_in_pnodes" in self.config.get("accounting-probes"):
            self.builder.get_object('net_in_pnodes').set_active(True)
            
        if "net_out_pnodes" in self.config.get("accounting-probes"):
            self.builder.get_object('net_out_pnodes').set_active(True)
        
        self.probe_initializing = False
        
        # db_folder
        db_folder = os.sep.join(os.path.expanduser(self.config.get("datafile")).split(os.sep)[:-1])
        self.builder.get_object('db_folder').set_filename(db_folder)
        
        # transfer-mechanism
        self.builder.get_object('transfer-mechanism').set_active_id(self.config.get("transfer-mechanism"))
        
        #avoid-redundant-transfers
        val = "True" if self.config.get("avoid-redundant-transfers") else "False"
        self.builder.get_object('avoid-redundant-transfers').set_active_id(val)
        
        # diskimage-reuse
        self.builder.get_object('diskimage-reuse').set_active_id(self.config.get("diskimage-reuse"))
        
        if self.config.get("diskimage-reuse") == 'none':
            self.builder.get_object('diskimage-cache-size').hide()
            self.builder.get_object('diskimage-cache-size-label').hide()
            self.builder.get_object('diskimage-cache-size-label2').hide()
        
        # diskimage-cache-size
        self.builder.get_object('diskimage-cache-size').set_text(str(self.config.get("diskimage-cache-size")))
        
        #force-imagetransfer-time
        h, m, s = (self.builder.get_object('force-imagetransfer-time-hours'),
            self.builder.get_object('force-imagetransfer-time-minutes'),
            self.builder.get_object('force-imagetransfer-time-seconds'))
        
        values = self.config.get("force-imagetransfer-time")
        values = str(values).split(":") if values else ('', '', '')
        h.set_text(values[0])
        m.set_text(values[1])
        s.set_text(values[2].split('.')[0])
    
        # runtime-slowdown-overhead
        self.builder.get_object('runtime-slowdown-overhead').set_text(str(self.config.get("runtime-slowdown-overhead") or ''))
        
        # add-overhead
        val = self.config.get("add-overhead")
        self.builder.get_object('add-overhead').set_active_id(val)
        
        if val == 'none':
            self.builder.get_object('runtime-slowdown-overhead').hide()
            self.builder.get_object('runtime-slowdown-overhead-label').hide()
            self.builder.get_object('runtime-slowdown-overhead-label2').hide()

        
        #bootshutdown-overhead
        h, m, s = (self.builder.get_object('bootshutdown-overhead-hours'),
            self.builder.get_object('bootshutdown-overhead-minutes'),
            self.builder.get_object('bootshutdown-overhead-seconds'))
        
        values = self.config.get("bootshutdown-overhead")
        values = str(values).split(":") if values else ('', '', '')
        h.set_text(values[0])
        m.set_text(values[1])
        s.set_text(values[2].split('.')[0])
        
    
    def import_configuration_callback(self, *args):
        chooser = self.builder.get_object("configfilechooser")
        chooser.show()
    
    def load_configuration_from_file_callback(self, *args):
        pass
    
    def save_configuration_as_callback(self, *args):
        pass
     
    def run_experiment(self, *args):
        self.console.set_text("")
        self.manager.reload(self.config, False, None, logging_handler=self.gui_loggin_handler, site=self.site)
        self.manager.start()
        self.reload_experiments()
    
    def run(self):
        self.first_time_run = True
        self.window.show()
        
        # Suuport Ctrl+c from terminal
        import signal
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        
        # Start
        Gtk.main()