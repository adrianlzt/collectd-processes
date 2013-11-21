import collectd
import os,re

plugin_name = "processes"

# http://www.unix.com/man-page/linux/7/time/
jiffpersec = os.sysconf(os.sysconf_names['SC_CLK_TCK'])

# https://www.kernel.org/doc/Documentation/filesystems/proc.txt
# name: position
stat_map = {
    'min_flt':     10,
    'maj_flt':     12,
    'utime':       14,
    'stime':       15,
    'num_threads': 20,
    'VSZ':         23,
    'RSS':         24,
    'blkio_ticks': 42
}

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

  # Dict to aggregate data
  agg = {}

  for dir in piddir:
    comm = file("/proc/"+dir+"/comm").read().rstrip()

    # IO
    io = file("/proc/"+dir+"/io").read()
    read_bytes = re.search('(?<=read_bytes: ).*',io).group(0)
    agg[comm+":read_bytes"] = read_bytes
    write_bytes = re.search('(?<=write_bytes: ).*',io).group(0)
    agg[comm+":write_bytes"] = write_bytes
    vl = collectd.Values(type='io_octets')
    vl.dispatch(plugin=plugin_name, plugin_instance=dir, values=[read_bytes,write_bytes])

    # Stat
    # stat array start in 0, but stat_map start in 0, so -1 it is needed
    stat = file("/proc/"+dir+"/stat").read().split(" ")

    # Time, in seconds
    utime = int(stat[stat_map.get('utime')-1]) / jiffpersec
    agg[comm+":utime" ] = utime 
    stime = int(stat[stat_map.get('stime')-1]) / jiffpersec
    agg[comm+":stime"] = stime 
    vl = collectd.Values(type='ps_cputime')
    vl.dispatch(plugin=plugin_name, plugin_instance=dir, values=[utime,stime])

    accutime = (utime + stime) / jiffpersec
    agg[comm+":accutime"] = accutime 
    vl = collectd.Values(type='ps_time')
    vl.dispatch(plugin=plugin_name, plugin_instance=dir, values=[accutime])

    # Threads
    threads = stat[stat_map.get('num_threads')-1]
    agg[comm+":threads"] = threads 
    vl = collectd.Values(type='threads')
    vl.dispatch(plugin=plugin_name, plugin_instance=dir, values=[threads])

    # Page faults
    min_flt = stat[stat_map.get('min_flt')-1]
    agg[comm+":min_flt"] = min_flt 
    maj_flt = stat[stat_map.get('maj_flt')-1]
    agg[comm+":maj_flt"] = maj_flt 
    vl = collectd.Values(type='ps_pagefaults')
    vl.dispatch(plugin=plugin_name, plugin_instance=dir, values=[min_flt,maj_flt])

    # Memory (VSZ,RSS)
    rss = stat[stat_map.get('RSS')-1]
    agg[comm+":rss"] = rss 
    vl = collectd.Values(type='ps_rss')
    vl.dispatch(plugin=plugin_name, plugin_instance=dir, values=[rss])

    vsz = stat[stat_map.get('VSZ')-1]
    agg[comm+":vsz"] = vsz 
    vl = collectd.Values(type='ps_vm')
    vl.dispatch(plugin=plugin_name, plugin_instance=dir, values=[vsz])

  # Aggregated data by comm
  for k,v in agg.iteritems():
    keys = k.split(":")
    comm = keys[0]
    metric = keys[1]

    if metric == "read_bytes":
      vl = collectd.Values(type='io_octets')
      write_bytes = agg[comm+":write_bytes"]
      vl.dispatch(plugin=plugin_name, plugin_instance=comm, values=[v,write_bytes])
      break
    elif metric == "utime":
      vl = collectd.Values(type='ps_cputime')
      stime = agg[comm+":stime"]
      vl.dispatch(plugin=plugin_name, plugin_instance=comm, values=[v,stime])
      break
    elif metric == "accutime":
      vl = collectd.Values(type='ps_time')
      vl.dispatch(plugin=plugin_name, plugin_instance=comm, values=[v])
      break
    elif metric == "threads":
      vl = collectd.Values(type='threads')
      vl.dispatch(plugin=plugin_name, plugin_instance=comm, values=[v])
      break
    elif metric == "min_flt":
      vl = collectd.Values(type='ps_pagefaults')
      maj_flt = agg[comm+":maj_flt"]
      vl.dispatch(plugin=plugin_name, plugin_instance=comm, values=[v,maj_flt])
      break
    elif metric == "rss":
      vl = collectd.Values(type='ps_rss')
      vl.dispatch(plugin=plugin_name, plugin_instance=comm, values=[v])
      break
    elif metric == "vsz":
      vl = collectd.Values(type='ps_vm')
      vl.dispatch(plugin=plugin_name, plugin_instance=comm, values=[v])
      break


collectd.register_config(config_processes)
collectd.register_init(init_processes)
collectd.register_read(read_processes)
