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

  for dir in piddir:
    comm = file("/proc/"+dir+"/comm").read().rstrip()

    # IO
    io = file("/proc/"+dir+"/io").read()
    read_bytes = re.search('(?<=read_bytes: ).*',io).group(0)
    write_bytes = re.search('(?<=write_bytes: ).*',io).group(0)
    vl = collectd.Values(type='io_octets')
    vl.dispatch(plugin=plugin_name, plugin_instance=dir, values=[read_bytes,write_bytes])

    # Stat
    # stat array start in 0, but stat_map start in 0, so -1 it is needed
    stat = file("/proc/"+dir+"/stat").read().split(" ")

    # Time, in seconds
    utime = stat[stat_map.get('utime')-1] / jiffpersec
    stime = stat[stat_map.get('stime')-1] / jiffpersec
    vl = collectd.Values(type='ps_cputime')
    vl.dispatch(plugin=plugin_name, plugin_instance=dir, values=[utime,stime])

    accutime = (utime + stime) / jiffpersec
    vl = collectd.Values(type='ps_time')
    vl.dispatch(plugin=plugin_name, plugin_instance=dir, values=[accutime])

    # Threads

    # Page faults

    # Memory (VSZ,RSS) percentage?

  # Aggregated data by comm?


    break


collectd.register_config(config_processes)
collectd.register_init(init_processes)
collectd.register_read(read_processes)
