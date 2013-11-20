import collectd
import os,re

# global variables


# True if dir is only numbers
def ispid(dir):
  return re.match('^[0-9]*$',dir) != None

def config_processes(conf):
  collectd.info('processes: configuring...')

def init_processes():
  collectd.info('processes: initing...')

def read_processes(data=None):
  procdir = os.listdir("/proc")
  piddir = filter(ispid, procdir)

  for dir in piddir:
    comm = file("/proc/"+dir+"/comm").read().rstrip()

    # IO
    io = file("/proc/"+dir+"/io").read()
    read_bytes = re.search('(?<=read_bytes: ).*',io).group(0)
    write_bytes = re.search('(?<=write_bytes: ).*',io).group(0)
    vl = collectd.Values(type='io_octets')
    vl.dispatch(plugin="procv2",plugin_instance=dir, values=[read_bytes,write_bytes])

    # Time

    # Threads

    # Page faults

    # Memory (VSZ,RSS) percentage?

  # Aggregated data by comm?


    break


collectd.register_config(config_processes)
collectd.register_init(init_processes)
collectd.register_read(read_processes)
