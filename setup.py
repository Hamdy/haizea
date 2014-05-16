from setuptools import setup
import os

SAMPLE_CONFIG = os.path.expanduser("~/.haizea/sample_config")
HOME = os.path.expanduser("~/.haizea")
TRACES_MULTI = os.path.expanduser("~/.haizea/traces/multi")
TRACES =  os.path.expanduser("~/.haizea/traces")

setup(name='haizea',
      version='1.0',
      description='Haizea',
      author='University of Chicago',
      author_email='borja@cs.uchicago.edu',
      url='https://github.com/Hamdy/haizea',
      package_dir = {'': 'src'},
      package_data={'': ['app.glade', '*.jpg']},
      install_requires = ['docutils', 'sqlalchemy', 'pygal', 'egenix-mx-base'],
      packages=['haizea', 
                'haizea.cli',
                'haizea.gui',
                'haizea.common', 
                'haizea.core', 
                'haizea.core.scheduler',
                'haizea.core.scheduler.preparation_schedulers',
                'haizea.core.enact',
                'haizea.core.frontends',
                'haizea.pluggable',
                'haizea.pluggable.policies',
                'haizea.pluggable.accounting'],
      scripts=['bin/haizea', 'bin/haizea-generate-configs', 'bin/haizea-generate-scripts', 'bin/haizea-convert-data', 
               'bin/haizea-cancel-lease', 'bin/haizea-list-leases', 'bin/haizea-list-hosts', 'bin/haizea-request-lease',
               'bin/haizea-show-queue', 'bin/haizea-statistics', 'bin/haizea-experiments-list', 'bin/haizea-experiments-clear',
               'bin/haizea-experiments-delete', 'bin/haizea-experiments-describe', 'bin/haizea-experiments-statistics-list', 'bin/haizea-gui',
               'bin/haizea-experiments-line-graph-accepted-ar', 'bin/haizea-experiments-bar-graph-accepted-ar',
               'bin/haizea-experiments-bar-graph-rejected-ar', 'bin/haizea-experiments-line-graph-rejected-ar',
               'bin/haizea-experiments-line-graph-accepted-im', 'bin/haizea-experiments-bar-graph-accepted-im',
               'bin/haizea-experiments-bar-graph-rejected-im', 'bin/haizea-experiments-line-graph-rejected-im',
               'bin/haizea-experiments-bar-graph-completed-be','bin/haizea-experiments-line-graph-completed-be',
               'bin/haizea-experiments-bar-graph-queue-be', 'bin/haizea-experiments-line-graph-queue-be',
               'bin/haizea-experiments-bar-graph-avg-cpu-utillization',
               'bin/haizea-experiments-bar-graph-avg-memory-utillization', 
               'bin/haizea-experiments-bar-graph-avg-disk-utillization',
               'bin/haizea-experiments-bar-graph-avg-net-in-utillization', 
               'bin/haizea-experiments-bar-graph-avg-net-out-utillization',
               
               ],
      
      data_files=[(HOME, ['etc/haizea.conf'],
                   SAMPLE_CONFIG, [
                          'etc/sample_trace.conf', 
                          'etc/sample_trace_barebones.conf', 
                          'etc/sample_opennebula.conf',
                          'etc/sample_opennebula_barebones.conf',
                          'etc/sample_multi.conf',
                          'etc/condor.template',
                          'etc/run.sh.template']),
                  (TRACES, ['traces/sample.lwf',
                             'traces/sample.images']),
                  (TRACES_MULTI, ['traces/multi/inj1.lwf',
                                                 'traces/multi/inj2.lwf',
                                                 'traces/multi/withprematureend.lwf',
                                                 'traces/multi/withoutprematureend.lwf']),
                  ],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Environment :: No Input/Output (Daemon)',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Scientific/Engineering',
          'Topic :: System :: Distributed Computing'
          ]
     )
