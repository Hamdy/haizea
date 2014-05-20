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

from haizea.core.manager import Manager
from haizea.common.utils import generate_config_name, unpickle
from haizea.core.configfile import HaizeaConfig, HaizeaMultiConfig
from haizea.core.accounting import AccountingDataCollection
from haizea.common.config import ConfigException
from haizea.cli.optionparser import Option
from haizea.cli import Command
from mx.DateTime import TimeDelta
import haizea.common.defaults as defaults
import sys
import os
import errno
import signal
from time import sleep
from haizea.pluggable.accounting import Database
from haizea.pluggable.accounting.models import Experiment
from haizea.cli.rpc_commands import console_table_printer
from haizea.gui import HaizeaGuiApp
from haizea.pluggable.accounting.graph import Graph

try:
    import xml.etree.ElementTree as ET
except ImportError:
    # Compatibility with Python <=2.4
    import elementtree.ElementTree as ET 

class haizea_gui(Command):
    name = "haizea-gui"
    
    """
    Haizea GUI
    """
    
    def __init__(self, argv):
        Command.__init__(self, argv)
        
        self.optparser.add_option(Option("-c", "--conf", action="store", type="string", dest="conf",
                                         help = """
                                         The location of the Haizea configuration file. If not
                                         specified, Haizea will first look for it in
                                         /etc/haizea/haizea.conf and then in ~/.haizea/haizea.conf.
                                         """))
        
        
            
    
    def run(self):
        self.parse_options()
        
        pidfile = defaults.DAEMON_PIDFILE # TODO: Make configurable

        if os.path.exists(pidfile):
            pf  = file(pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
 
            try:
                os.kill(pid, signal.SIG_DFL)
            except OSError, (err, msg):
                if err == errno.ESRCH:
                    # Pidfile is stale. Remove it.
                    os.remove(pidfile)
                else:
                    msg = "Unexpected error when checking pid file '%s'.\n%s\n" %(pidfile, msg)
                    sys.stderr.write(msg)
                    sys.exit(1)
            else:
                msg = "Haizea seems to be already running (pid %i)\n" % pid
                sys.stderr.write(msg)
                sys.exit(1)
                    
        try:
            configfile=self.opt.conf
            if configfile == None:
                # Look for config file in default locations
                for loc in defaults.CONFIG_LOCATIONS:
                    if os.path.exists(loc):
                        config = HaizeaConfig.from_file(loc)
                        break
                else:
                    print >> sys.stdout, "No configuration file specified, and none found at default locations."
                    print >> sys.stdout, "Make sure a config file exists at:\n  -> %s" % "\n  -> ".join(defaults.CONFIG_LOCATIONS)
                    print >> sys.stdout, "Or specify a configuration file with the --conf option."
                    exit(1)
            else:
                config = HaizeaConfig.from_file(configfile)
            
            app = HaizeaGuiApp(Manager, config, pidfile)
            app.run()

        except ConfigException, msg:
            print >> sys.stderr, "Error in configuration file:"
            print >> sys.stderr, msg
            exit(1)
            
        

class haizea(Command):
    """
    This is the main Haizea command. By default, it will start Haizea as a daemon, which
    can receive requests via RPC or interact with other components such as OpenNebula. It can
    also start as a foreground process, and write all log messages to the console. All
    Haizea options are specified through the configuration file."""
    
    name = "haizea"
    
    def __init__(self, argv):
        Command.__init__(self, argv)
        
        self.optparser.add_option(Option("-c", "--conf", action="store", type="string", dest="conf",
                                         help = """
                                         The location of the Haizea configuration file. If not
                                         specified, Haizea will first look for it in
                                         /etc/haizea/haizea.conf and then in ~/.haizea/haizea.conf.
                                         """))
        self.optparser.add_option(Option("-f", "--fg", action="store_true",  dest="foreground",
                                         help = """
                                         Runs Haizea in the foreground.
                                         """))
        self.optparser.add_option(Option("--stop", action="store_true",  dest="stop",
                                         help = """
                                         Stops the Haizea daemon.
                                         """))
                
    def run(self):
        self.parse_options()

        pidfile = defaults.DAEMON_PIDFILE # TODO: Make configurable

        if self.opt.stop == None:
            # Start Haizea
             
            # Check if a daemon is already running
            if os.path.exists(pidfile):
                pf  = file(pidfile,'r')
                pid = int(pf.read().strip())
                pf.close()
     
                try:
                    os.kill(pid, signal.SIG_DFL)
                except OSError, (err, msg):
                    if err == errno.ESRCH:
                        # Pidfile is stale. Remove it.
                        os.remove(pidfile)
                    else:
                        msg = "Unexpected error when checking pid file '%s'.\n%s\n" %(pidfile, msg)
                        sys.stderr.write(msg)
                        sys.exit(1)
                else:
                    msg = "Haizea seems to be already running (pid %i)\n" % pid
                    sys.stderr.write(msg)
                    sys.exit(1)
     
            try:
                configfile=self.opt.conf
                if configfile == None:
                    # Look for config file in default locations
                    for loc in defaults.CONFIG_LOCATIONS:
                        if os.path.exists(loc):
                            config = HaizeaConfig.from_file(loc)
                            break
                    else:
                        print >> sys.stdout, "No configuration file specified, and none found at default locations."
                        print >> sys.stdout, "Make sure a config file exists at:\n  -> %s" % "\n  -> ".join(defaults.CONFIG_LOCATIONS)
                        print >> sys.stdout, "Or specify a configuration file with the --conf option."
                        exit(1)
                else:
                    config = HaizeaConfig.from_file(configfile)
            except ConfigException, msg:
                print >> sys.stderr, "Error in configuration file:"
                print >> sys.stderr, msg
                exit(1)
                
            daemon = not self.opt.foreground
        
            manager = Manager(config, daemon, pidfile)
        
            manager.start()
        elif self.opt.stop: # Stop Haizea
            # Based on code in:  http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66012
            try:
                pf  = file(pidfile,'r')
                pid = int(pf.read().strip())
                pf.close()
            except IOError:
                msg = "Could not stop, pid file '%s' missing.\n"
                sys.stderr.write(msg % pidfile)
                sys.exit(1)
            try:
                while 1:
                    os.kill(pid, signal.SIGTERM)
                    sleep(1)
            except OSError, err:
                err = str(err)
                if err.find("No such process") > 0:
                    os.remove(pidfile)
                else:
                    print str(err)
                    sys.exit(1)

class haizea_statistics(Command):
    name = "haizea-statisitcs"
    
    """
    Haizea Statistics graphing framework.
    """
    
    def __init__(self, argv):
        Command.__init__(self, argv)
        
        self.optparser.add_option(Option("-c", "--conf", action="store", type="string", dest="conf",
                                         help = """
                                         The location of the Haizea configuration file. If not
                                         specified, Haizea will first look for it in
                                         /etc/haizea/haizea.conf and then in ~/.haizea/haizea.conf.
                                         """))
        
        
            
    
    def run(self):
        self.parse_options()
        
        try:
            configfile=self.opt.conf
            if configfile == None:
                # Look for config file in default locations
                for loc in defaults.CONFIG_LOCATIONS:
                    if os.path.exists(loc):
                        config = HaizeaConfig.from_file(loc)
                        break
                else:
                    print >> sys.stdout, "No configuration file specified, and none found at default locations."
                    print >> sys.stdout, "Make sure a config file exists at:\n  -> %s" % "\n  -> ".join(defaults.CONFIG_LOCATIONS)
                    print >> sys.stdout, "Or specify a configuration file with the --conf option."
                    exit(1)
            else:
                config = HaizeaConfig.from_file(configfile)
        except ConfigException, msg:
            print >> sys.stderr, "Error in configuration file:"
            print >> sys.stderr, msg
            exit(1)
            
        
class haizea_experiments_list(Command):
    name = "haizea-experiments-list"
    
    def __init__(self, argv):
        Command.__init__(self, argv)
        
        self.optparser.add_option(Option("-c", "--conf", action="store", type="string", dest="conf",
                                         help = """
                                         The location of the Haizea configuration file. If not
                                         specified, Haizea will first look for it in
                                         /etc/haizea/haizea.conf and then in ~/.haizea/haizea.conf.
                                         """))
        
        
    def run(self):
        self.parse_options()
        
        try:
            configfile=self.opt.conf
            if configfile == None:
                # Look for config file in default locations
                for loc in defaults.CONFIG_LOCATIONS:
                    if os.path.exists(loc):
                        config = HaizeaConfig.from_file(loc)
                        break
                else:
                    print >> sys.stdout, "No configuration file specified, and none found at default locations."
                    print >> sys.stdout, "Make sure a config file exists at:\n  -> %s" % "\n  -> ".join(defaults.CONFIG_LOCATIONS)
                    print >> sys.stdout, "Or specify a configuration file with the --conf option."
                    exit(1)
            else:
                config = HaizeaConfig.from_file(configfile)
            db = Database(os.path.expanduser(config.get("datafile"))).db
            
            experiments = []
            for e in db.query(Experiment).order_by("-id").all():
                d = {"id":e.id, "description":e.description,
                     "accepted_ar":e.total_accepted_ar,
                     "rejected_ar" : e.total_rejected_ar,
                     "accepted_im":e.total_accepted_im,
                     "rejected_im" : e.total_rejected_im,
                     "total_completed_be" : e.total_completed_be,
                     "be_finish_time" : e.be_completed_after
                     }
                experiments.append(d)
            
            fields = [("id","ID", 3),
                  ("description","Description", 15),
                  ("accepted_ar","Total Accepted AR", 18),
                  ("rejected_ar","Total Rejected AR", 18),
                   ("accepted_im","Total Accepted IM", 18),
                   ("rejected_im","Total Rejected IM", 18),
                  ("total_completed_be", "Total completed BE", 10),
                  ("be_finish_time","BE Finished after (min)", 1)               
                  ]
            
            console_table_printer(fields, experiments)
            
        except ConfigException, msg:
            print >> sys.stderr, "Error in configuration file:"
            print >> sys.stderr, msg
            exit(1)

class haizea_experiments_delete(Command):
    name = "haizea-experiments-delete"
    
    def __init__(self, argv):
        Command.__init__(self, argv)
        
        self.optparser.add_option(Option("-c", "--conf", action="store", type="string", dest="conf",
                                         help = """
                                         The location of the Haizea configuration file. If not
                                         specified, Haizea will first look for it in
                                         /etc/haizea/haizea.conf and then in ~/.haizea/haizea.conf.
                                         """))
        
    def run(self):
        self.parse_options()
        
        try:
            configfile=self.opt.conf
            if configfile == None:
                # Look for config file in default locations
                for loc in defaults.CONFIG_LOCATIONS:
                    if os.path.exists(loc):
                        config = HaizeaConfig.from_file(loc)
                        break
                else:
                    print >> sys.stdout, "No configuration file specified, and none found at default locations."
                    print >> sys.stdout, "Make sure a config file exists at:\n  -> %s" % "\n  -> ".join(defaults.CONFIG_LOCATIONS)
                    print >> sys.stdout, "Or specify a configuration file with the --conf option."
                    exit(1)
            else:
                config = HaizeaConfig.from_file(configfile)
            
            import sys
            
            if len(sys.argv) == 1:
                print >> sys.stdout, "You must provide experimetns to delete"
                print >> sys.stdout, "Example: haizea-experiments-delete 1"
                print >> sys.stdout, "         haizea-experimetns-delete 1 2 3 4  (List of experiments)"
                exit(1)
            

            db = Database(os.path.expanduser(config.get("datafile"))).db
            
            try:
                ids = map(int, sys.argv[1:])
                db.query(Experiment).filter(Experiment.id.in_(ids)).delete(synchronize_session=False)
                db.commit()
                
            except Exception:
                print >> sys.stderr, "Invalid ID(s)"

            
        except ConfigException, msg:
            print >> sys.stderr, "Error in configuration file:"
            print >> sys.stderr, msg
            exit(1)

class haizea_experiments_describe(Command):
    name = "haizea-experiments-describe"
    
    def __init__(self, argv):
        Command.__init__(self, argv)
        
        self.optparser.add_option(Option("-c", "--conf", action="store", type="string", dest="conf",
                                         help = """
                                         The location of the Haizea configuration file. If not
                                         specified, Haizea will first look for it in
                                         /etc/haizea/haizea.conf and then in ~/.haizea/haizea.conf.
                                         """))
        
    def run(self):
        self.parse_options()
        
        try:
            configfile=self.opt.conf
            if configfile == None:
                # Look for config file in default locations
                for loc in defaults.CONFIG_LOCATIONS:
                    if os.path.exists(loc):
                        config = HaizeaConfig.from_file(loc)
                        break
                else:
                    print >> sys.stdout, "No configuration file specified, and none found at default locations."
                    print >> sys.stdout, "Make sure a config file exists at:\n  -> %s" % "\n  -> ".join(defaults.CONFIG_LOCATIONS)
                    print >> sys.stdout, "Or specify a configuration file with the --conf option."
                    exit(1)
            else:
                config = HaizeaConfig.from_file(configfile)
            
            import sys
            
            if len(sys.argv) != 3:
                print >> sys.stdout, "You must provide experiment ID & Description"
                print >> sys.stdout, "Example: haizea-experiments-describe 1 \"Experiment 1\""
                exit(1)
            

            db = Database(os.path.expanduser(config.get("datafile"))).db
            
            try:
                id = int(sys.argv[1])
                db.query(Experiment).filter_by(id=id).update({'description':str(sys.argv[2])})
                db.commit()
            except Exception:
                print >> sys.stderr, "Invalid ID(s)"
            
        except ConfigException, msg:
            print >> sys.stderr, "Error in configuration file:"
            print >> sys.stderr, msg
            exit(1)


class haizea_experiments_clear(Command):
    name = "haizea-experiments-clear"
    
    def __init__(self, argv):
        Command.__init__(self, argv)
        
        self.optparser.add_option(Option("-c", "--conf", action="store", type="string", dest="conf",
                                         help = """
                                         The location of the Haizea configuration file. If not
                                         specified, Haizea will first look for it in
                                         /etc/haizea/haizea.conf and then in ~/.haizea/haizea.conf.
                                         """))
        
        
    def run(self):
        self.parse_options()
        
        try:
            configfile=self.opt.conf
            if configfile == None:
                # Look for config file in default locations
                for loc in defaults.CONFIG_LOCATIONS:
                    if os.path.exists(loc):
                        config = HaizeaConfig.from_file(loc)
                        break
                else:
                    print >> sys.stdout, "No configuration file specified, and none found at default locations."
                    print >> sys.stdout, "Make sure a config file exists at:\n  -> %s" % "\n  -> ".join(defaults.CONFIG_LOCATIONS)
                    print >> sys.stdout, "Or specify a configuration file with the --conf option."
                    exit(1)
            else:
                config = HaizeaConfig.from_file(configfile)

            ans = raw_input("Are you sure you want to clear all the experiments from databas? Y/N? ")
            
            if ans == 'Y' or ans == 'y':
                from sqlalchemy.engine import reflection
                from sqlalchemy import create_engine
                from sqlalchemy.schema import (
                    MetaData,
                    Table,
                    DropTable,
                    ForeignKeyConstraint,
                    DropConstraint,
                    )
                
                engine = create_engine('sqlite:///%s' % os.path.expanduser(config.get("datafile")), echo=False)

                conn = engine.connect()
                
                # the transaction only applies if the DB supports
                # transactional DDL, i.e. Postgresql, MS SQL Server
                trans = conn.begin()
                
                inspector = reflection.Inspector.from_engine(engine)
                
                # gather all data first before dropping anything.
                # some DBs lock after things have been dropped in 
                # a transaction.
                
                metadata = MetaData()
                
                tbs = []
                all_fks = []
                
                for table_name in inspector.get_table_names():
                    fks = []
                    for fk in inspector.get_foreign_keys(table_name):
                        if not fk['name']:
                            continue
                        fks.append(
                            ForeignKeyConstraint((),(),name=fk['name'])
                            )
                    t = Table(table_name,metadata,*fks)
                    tbs.append(t)
                    all_fks.extend(fks)
                
                for fkc in all_fks:
                    conn.execute(DropConstraint(fkc))

                for table in tbs:
                    conn.execute(DropTable(table))
                
                trans.commit()
                                
           
            
        except ConfigException, msg:
            print >> sys.stderr, "Error in configuration file:"
            print >> sys.stderr, msg
            exit(1)
   
        
class haizea_experiments_statistics_list(Command):
    name = "haizea-experiments-statistics-list"
    
    def __init__(self, argv):
        Command.__init__(self, argv)
        
        self.optparser.add_option(Option("-c", "--conf", action="store", type="string", dest="conf",
                                         help = """
                                         The location of the Haizea configuration file. If not
                                         specified, Haizea will first look for it in
                                         /etc/haizea/haizea.conf and then in ~/.haizea/haizea.conf.
                                         """))
        
    def run(self):
        self.parse_options()
        
        try:
            configfile=self.opt.conf
            if configfile == None:
                # Look for config file in default locations
                for loc in defaults.CONFIG_LOCATIONS:
                    if os.path.exists(loc):
                        config = HaizeaConfig.from_file(loc)
                        break
                else:
                    print >> sys.stdout, "No configuration file specified, and none found at default locations."
                    print >> sys.stdout, "Make sure a config file exists at:\n  -> %s" % "\n  -> ".join(defaults.CONFIG_LOCATIONS)
                    print >> sys.stdout, "Or specify a configuration file with the --conf option."
                    exit(1)
            else:
                config = HaizeaConfig.from_file(configfile)
            
            import sys
            
            if len(sys.argv) != 2:
                print >> sys.stdout, "You must provide an experimetn ID to show it's lease statistics"
                print >> sys.stdout, "Example: haizea-experiments-statistics-list 1"
                exit(1)
            

            db = Database(os.path.expanduser(config.get("datafile"))).db
            
            try:
                id = int(sys.argv[1])
                exp = db.query(Experiment).filter_by(id=id).first()
                
                if not exp:
                    sys.exit(1)
                    
                lease_statistics = exp.lease_statistics
                
                print "\n"
                
                fields = [("name","Statistic metric", 40),
                          ("value","Value", 4)]
                
                values = [
                    {"name":"Total best-effort completed", "value":exp.total_completed_be},
                    {"name":"BE leases finished after (mins)", "value":exp.be_completed_after},
                    {"name":"Total accepted AR", "value":exp.total_accepted_ar},
                    {"name":"Total rejected AR", "value":exp.total_rejected_ar},
                    {"name":"Total accepted Immediate", "value":exp.total_accepted_im},
                    {"name":"Total rejected Immediate", "value":exp.total_rejected_im}]
                
                console_table_printer(fields, values)
                        
                print "\n"
    
                fields = [("id","Best Effort Lease ID", 20),
                      ("waiting","Waiting time (mins)", 20),
                      ("slowdown" , "Slow down Ratio", 10),
                      ]
                values = []
                
                for e in lease_statistics:
                    d = {"id":e.lease_id, "waiting":e.waiting_time, "slowdown":e.slowdown}
                    values.append(d)
                
                console_table_printer(fields, values)
                print "\n"
        
                
            except Exception:
                print >> sys.stderr, "Invalid ID"

            
        except ConfigException, msg:
            print >> sys.stderr, "Error in configuration file:"
            print >> sys.stderr, msg
            exit(1)

class haizea_generate_configs(Command):
    """
    Takes an Haizea multiconfiguration file and generates the individual
    configuration files. See the Haizea manual for more details on multiconfiguration
    files."""
    
    name = "haizea-generate-configs"

    def __init__(self, argv):
        Command.__init__(self, argv)
        
        self.optparser.add_option(Option("-c", "--conf", action="store", type="string", dest="conf", required=True,
                                         help = """
                                         Multiconfiguration file.
                                         """))
        self.optparser.add_option(Option("-d", "--dir", action="store", type="string", dest="dir", required=True,
                                         help = """
                                         Directory where the individual configuration files
                                         must be created.
                                         """))
                
    def run(self):    
        self.parse_options()
        
        configfile=self.opt.conf
        multiconfig = HaizeaMultiConfig.from_file(configfile)
        
        etcdir = self.opt.dir
        
        configs = multiconfig.get_configs()
        
        etcdir = os.path.abspath(etcdir)    
        if not os.path.exists(etcdir):
            os.makedirs(etcdir)
            
        for c in configs:
            profile = c.get_attr("profile")
            tracefile = c.get("tracefile")
            injfile = c.get("injectionfile")
            configname = generate_config_name(profile, tracefile, injfile)
            configfile = etcdir + "/%s.conf" % configname
            fc = open(configfile, "w")
            c.config.write(fc)
            fc.close()

class haizea_generate_scripts(Command):
    """
    Generates a script, based on a script template, to run all the individual 
    configuration files generated by haizea-generate-configs. This command 
    requires Mako Templates for Python (http://www.makotemplates.org/)."""
    
    name = "haizea-generate-scripts"

    def __init__(self, argv):
        Command.__init__(self, argv)
        
        self.optparser.add_option(Option("-c", "--conf", action="store", type="string", dest="conf", required=True,
                                         help = """
                                         Multiconfiguration file used in haizea-generate-configs.
                                         """))
        self.optparser.add_option(Option("-d", "--confdir", action="store", type="string", dest="confdir", required=True,
                                         help = """
                                         Directory containing the individual configuration files.
                                         """))
        self.optparser.add_option(Option("-t", "--template", action="store", type="string", dest="template", required=True,
                                         help = """
                                         Script template (sample templates are included in /usr/share/haizea/etc)
                                         """))
        self.optparser.add_option(Option("-m", "--only-missing", action="store_true",  dest="onlymissing",
                                         help = """
                                         If specified, the generated script will only run the configurations
                                         that have not already produced a datafile. This is useful when some simulations
                                         fail, and you don't want to have to rerun them all.
                                         """))
                
    def run(self):        
        self.parse_options()
        
        configfile=self.opt.conf
        multiconfig = HaizeaMultiConfig.from_file(configfile)
                
        try:
            from mako.template import Template
        except Exception, e:
            print "You need Mako Templates for Python to run this command."
            print "You can download them at http://www.makotemplates.org/"
            exit(1)
    
        configs = multiconfig.get_configs()
        
        etcdir = os.path.abspath(self.opt.confdir)    
        if not os.path.exists(etcdir):
            os.makedirs(etcdir)
            
        templatedata = []    
        for c in configs:
            profile = c.get_attr("profile")
            tracefile = c.get("tracefile")
            injfile = c.get("injectionfile")
            datafile = c.get("datafile")
            configname = generate_config_name(profile, tracefile, injfile)
            if not self.opt.onlymissing or not os.path.exists(datafile):
                configfile = etcdir + "/%s.conf" % configname
                templatedata.append((configname, configfile))
    
        template = Template(filename=self.opt.template)
        print template.render(configs=templatedata, etcdir=etcdir)


class haizea_convert_data(Command):
    """
    Converts Haizea datafiles into another (easier to process) format.
    """
    
    name = "haizea-convert-data"

    def __init__(self, argv):
        Command.__init__(self, argv)
        
        self.optparser.add_option(Option("-t", "--type", action="store",  dest="type",
                                         choices = ["per-run", "per-lease", "counter"],
                                         help = """
                                         Type of data to produce.
                                         """))
        self.optparser.add_option(Option("-c", "--counter", action="store",  dest="counter",
                                         help = """
                                         Counter to print out when using '--type counter'.
                                         """))
        self.optparser.add_option(Option("-f", "--format", action="store", type="string", dest="format",
                                         help = """
                                         Output format. Currently supported: csv
                                         """))
        self.optparser.add_option(Option("-l", "--list-counters", action="store_true",  dest="list_counters",
                                         help = """
                                         If specified, the command will just print out the names of counters
                                         stored in the data file and then exit, regardless of other parameters.
                                         """))
                
    def run(self):            
        self.parse_options()

        datafiles=self.args[1:]
        if len(datafiles) == 0:
            print "Please specify at least one datafile to convert"
            exit(1)
        
        datafile1 = unpickle(datafiles[0])
        
        counter_names = datafile1.counters.keys()
        attr_names = datafile1.attrs.keys()
        lease_stats_names = datafile1.lease_stats_names
        stats_names = datafile1.stats_names

        if self.opt.list_counters:
            for counter in counter_names:
                print counter
            exit(0)
        
        if self.opt.type == "per-run":
            header_fields = attr_names + stats_names
        elif self.opt.type == "per-lease":
            header_fields = attr_names + ["lease_id"] + lease_stats_names
        elif self.opt.type == "counter":
            counter = self.opt.counter
            if not datafile1.counters.has_key(counter):
                print "The specified datafile does not have a counter called '%s'" % counter
                exit(1)
            header_fields = attr_names + ["time", "value"]
            if datafile1.counter_avg_type[counter] != AccountingDataCollection.AVERAGE_NONE:
                header_fields.append("average")                

        header = ",".join(header_fields)
            
        print header
        
        for datafile in datafiles:
            data = unpickle(datafile)
        
            attrs = [data.attrs[attr_name] for attr_name in attr_names]
                        
            if self.opt.type == "per-run":
                fields = attrs + [`data.stats[stats_name]` for stats_name in stats_names]
                print ",".join(fields)
            elif self.opt.type == "per-lease":
                leases = data.lease_stats
                for lease_id, lease_stat in leases.items():
                    fields = attrs + [`lease_id`] + [`lease_stat.get(lease_stat_name,"")` for lease_stat_name in lease_stats_names]
                    print ",".join(fields)
            elif self.opt.type == "counter":
                for (time, lease_id, value, avg) in data.counters[counter]:
                    fields = attrs + [`time`, `value`]
                    if data.counter_avg_type[counter] != AccountingDataCollection.AVERAGE_NONE:
                        fields.append(`avg`)
                    print ",".join(fields)
                    


class haizea_lwf2xml(Command):
    """
    Converts old Haizea LWF file into new XML-based LWF format
    """
    
    name = "haizea-lwf2xml"

    def __init__(self, argv):
        Command.__init__(self, argv)
        
        self.optparser.add_option(Option("-i", "--in", action="store",  type="string", dest="inf",
                                         help = """
                                         Input file
                                         """))
        self.optparser.add_option(Option("-o", "--out", action="store", type="string", dest="outf",
                                         help = """
                                         Output file
                                         """))
                
    def run(self):            
        self.parse_options()

        infile = self.opt.inf
        outfile = self.opt.outf
        
        root = ET.Element("lease-workload")
        root.set("name", infile)
        description = ET.SubElement(root, "description")
        time = TimeDelta(seconds=0)
        lease_id = 1
        requests = ET.SubElement(root, "lease-requests")
        
        
        infile = open(infile, "r")
        for line in infile:
            if line[0]!='#' and len(line.strip()) != 0:
                fields = line.split()
                submit_time = int(fields[0])
                start_time = int(fields[1])
                duration = int(fields[2])
                real_duration = int(fields[3])
                num_nodes = int(fields[4])
                cpu = int(fields[5])
                mem = int(fields[6])
                disk = int(fields[7])
                vm_image = fields[8]
                vm_imagesize = int(fields[9])
                
                
        
                lease_request = ET.SubElement(requests, "lease-request")
                lease_request.set("arrival", str(TimeDelta(seconds=submit_time)))
                if real_duration != duration:
                    realduration = ET.SubElement(lease_request, "realduration")
                    realduration.set("time", str(TimeDelta(seconds=real_duration)))
                
                lease = ET.SubElement(lease_request, "lease")
                lease.set("id", `lease_id`)

                
                nodes = ET.SubElement(lease, "nodes")
                node_set = ET.SubElement(nodes, "node-set")
                node_set.set("numnodes", `num_nodes`)
                res = ET.SubElement(node_set, "res")
                res.set("type", "CPU")
                if cpu == 1:
                    res.set("amount", "100")
                else:
                    pass
                res = ET.SubElement(node_set, "res")
                res.set("type", "Memory")
                res.set("amount", `mem`)
                
                start = ET.SubElement(lease, "start")
                if start_time == -1:
                    lease.set("preemptible", "true")
                else:
                    lease.set("preemptible", "false")
                    exact = ET.SubElement(start, "exact")
                    exact.set("time", str(TimeDelta(seconds=start_time)))

                duration_elem = ET.SubElement(lease, "duration")
                duration_elem.set("time", str(TimeDelta(seconds=duration)))

                software = ET.SubElement(lease, "software")
                diskimage = ET.SubElement(software, "disk-image")
                diskimage.set("id", vm_image)
                diskimage.set("size", `vm_imagesize`)
                
                    
                lease_id += 1
        tree = ET.ElementTree(root)
        print ET.tostring(root)
        #tree.write("page.xhtml")


        
class haizea_experiments_graph(Command):
    name = "haizea-experiments-delete"
    
    def __init__(self, argv, type):
        Command.__init__(self, argv)
        self.type = type
        
        self.optparser.add_option(Option("-c", "--conf", action="store", type="string", dest="conf",
                                         help = """
                                         The location of the Haizea configuration file. If not
                                         specified, Haizea will first look for it in
                                         /etc/haizea/haizea.conf and then in ~/.haizea/haizea.conf.
                                         """))
        
    def run(self):
        self.parse_options()
        
        try:
            configfile=self.opt.conf
            if configfile == None:
                # Look for config file in default locations
                for loc in defaults.CONFIG_LOCATIONS:
                    if os.path.exists(loc):
                        config = HaizeaConfig.from_file(loc)
                        break
                else:
                    print >> sys.stdout, "No configuration file specified, and none found at default locations."
                    print >> sys.stdout, "Make sure a config file exists at:\n  -> %s" % "\n  -> ".join(defaults.CONFIG_LOCATIONS)
                    print >> sys.stdout, "Or specify a configuration file with the --conf option."
                    exit(1)
            else:
                config = HaizeaConfig.from_file(configfile)
            
            import sys
            
            if len(sys.argv) == 1:
                print >> sys.stdout, "You must provide experimetns to graph"
                print >> sys.stdout, "Example: haizea-experiments-line-graph-ar 1"
                print >> sys.stdout, "         haizea-experiments-line-graph-ar 1 2 3 4  (List of experiments)"
                exit(1)
            

            db = Database(os.path.expanduser(config.get("datafile"))).db
            
            try:
                ids = map(int, sys.argv[1:])
                experiments = db.query(Experiment).filter(Experiment.id.in_(ids))
                g = Graph()
                g.graph(experiments, self.type)
            except Exception:
                print >> sys.stderr, "Invalid ID(s)"

            
        except ConfigException, msg:
            print >> sys.stderr, "Error in configuration file:"
            print >> sys.stderr, msg
            exit(1)

