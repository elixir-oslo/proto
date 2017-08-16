# Parallel Python Software: http://www.parallelpython.com
# Copyright (c) 2005-2011, Vitalii Vanovschi
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the author nor the names of its contributors
#      may be used to endorse or promote products derived from this software
#      without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.
"""
Parallel Python Software, Execution Server

http://www.parallelpython.com - updates, documentation, examples and support
forums
"""

# Modified by Jonathan Lillesaeter as part of the Genomic HyperBrowser project

import os
import threading
import logging
import inspect
import sys
import types
import time
import atexit
import user
import cPickle as pickle
import pptransport
import ppauto
import ppcommon
import collections

from gold.application.LogSetup import logMessage, PARALLEL_LOGGER

copyright = "Copyright (c) 2005-2011 Vitalii Vanovschi. All rights reserved"
version = "1.6.1"

# Reconnect persistent rworkers in seconds.
RECONNECT_WAIT_TIME = 5

# Set timeout for socket operations in seconds.
SOCKET_TIMEOUT = 5

# If set to true prints out the exceptions which are expected.
SHOW_EXPECTED_EXCEPTIONS = False

# Number of seconds to calculate the load average over
LOAD_AVERAGE_PERIOD = 60 * 15 #15 minutes
#Load average polling interval in seconds
LOAD_AVERAGE_POLLING_INTERVAL = 5

# Number of seconds of inactivity before a Job is considered idle
# and removable
JOB_MAX_IDLE_TIME = 5

# we need to have set even in Python 2.3
try:
    set
except NameError:
    from sets import Set as set 
    
_USE_MULTIPROCESSING = False
try:
    import multiprocessing
    _USE_MULTIPROCESSING = True
except ImportError:
    pass

_USE_SUBPROCESS = False
try:
    import subprocess
    _USE_SUBPROCESS = True
except ImportError:
    import popen2

class _Task(object):
    """Class describing single task (job)
    """

    def __init__(self, server, tid, callback=None,
            callbackargs=(), group='default'):
        """Initializes the task"""
        self.lock = threading.Lock()
        self.lock.acquire()
        self.tid = tid
        self.server = server
        self.callback = callback
        self.callbackargs = callbackargs
        self.group = group
        self.finished = False
        self.unpickled = False

    def finalize(self, sresult):
        """Finalizes the task.

           For internal use only"""
        self.sresult = sresult
        if self.callback:
            self.__unpickle()
        self.lock.release()
        self.finished = True

    def __call__(self, raw_result=False):
        """Retrieves result of the task"""
        if not self.finished and self.server._exiting:
            raise DestroyedServerError("Server was destroyed before the job completion")
    
        self.wait()

        if not self.unpickled and not raw_result:
            self.__unpickle()

        if raw_result:
            return self.sresult
        else:
            return self.result

    def wait(self):
        """Waits for the task"""
        if not self.finished:
            self.lock.acquire()
            self.lock.release()

    def __unpickle(self):
        """Unpickles the result of the task"""
        self.result, sout = pickle.loads(self.sresult)
        self.unpickled = True
        if len(sout) > 0:
            print sout,
        if self.callback:
            args = self.callbackargs + (self.result, )
            self.callback(*args)


class _Worker(object):
    """Local worker class
    """
    command = [sys.executable, "-u",
            os.path.dirname(os.path.abspath(__file__))
            + os.sep + "ppworker.py"]

    command.append("2>/dev/null")

    def __init__(self, restart_on_free, pickle_proto):
        """Initializes local worker"""
        self.restart_on_free = restart_on_free
        self.pickle_proto = pickle_proto
        self.start()

    def start(self):
        """Starts local worker"""
        if _USE_MULTIPROCESSING:
            import ppworker
            localPipeEnd, remotePipeEnd = multiprocessing.Pipe()
            self.t = pptransport.CMultiprocessingPipeTransport(localPipeEnd)
            self.proc = multiprocessing.Process(target=ppworker._WorkerProcessRunner, args=(remotePipeEnd,))
            self.proc.start()
            
        elif _USE_SUBPROCESS:
            proc = subprocess.Popen(self.command, stdin=subprocess.PIPE, \
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, \
                    shell=False)
            self.t = pptransport.CPipeTransport(proc.stdout, proc.stdin)
        else:
            self.t = pptransport.CPipeTransport(\
                    *popen2.popen3(self.command)[:2])

        self.pid = int(self.t.receive())
        self.id = self.pid
        self.t.send(str(self.pickle_proto))
        self.is_free = True

    def stop(self):
        print "stopping worker %d" % self.pid
        """Stops local worker"""
        self.is_free = False
        self.t.send('EXIT') # can send any string - it will exit
        self.t.close()
        self.proc.join()
        print "...done stopping worker %d" % self.pid


    def restart(self):
        """Restarts local worker"""
        self.stop()
        self.start()

    def free(self):
        """Frees local worker"""
        if self.restart_on_free:
            self.restart()
        else:
            self.is_free = True
            
    def is_alive(self):
        return self.proc.is_alive()


class _RWorker(pptransport.CSocketTransport):
    """Remote worker class
    """

    def __init__(self, host, port, secret, server,  message=None, persistent=True):
        """Initializes remote worker"""
        self.server = server
        self.persistent = persistent
        self.host = host
        self.port = port
        self.secret = secret
        self.address = (host, port)
        self.id = host + ":" + str(port)
        self.server.logger.debug("Creating Rworker id=%s persistent=%s"
                % (self.id, persistent))
        self.connect(message)

    def __del__(self):
        """Closes connection with remote server"""
        self.close()

    def connect(self, message=None):
        """Connects to a remote server"""
        while True and not self.server._exiting:
            try:
                pptransport.SocketTransport.__init__(self)                
                self._connect(self.host, self.port)                
                if not self.authenticate(self.secret):
                    self.server.logger.error("Authentication failed for host=%s, port=%s"
                            % (self.host, self.port))
                    return False
                if message:
                    self.send(message)
                self.is_free = True
                return True
            except:
                if SHOW_EXPECTED_EXCEPTIONS:
                    self.server.logger.debug("Exception in connect method "
                            "(possibly expected)", exc_info=True)
                if not self.persistent:
                    self.server.logger.debug("Deleting from queue Rworker %s"
                            % (self.id, ))
                    return False
                self.server.logger.info("Failed to reconnect with " \
                        "(host=%s, port=%i), will try again in %i s"
                        % (self.host, self.port, RECONNECT_WAIT_TIME))
                time.sleep(RECONNECT_WAIT_TIME)


class _Statistics(object):
    """Class to hold execution statisitcs for a single node
    """

    def __init__(self, ncpus, rworker=None):
        """Initializes statistics for a node"""
        self.ncpus = ncpus
        self.time = 0.0
        self.njobs = 0
        self.rworker = rworker


class Template(object):
    """Template class
    """

    def __init__(self, job_server, func, depfuncs=(), modules=(),
            callback=None, callbackargs=(), group='default', globals=None):
        """Creates Template instance

           jobs_server - pp server for submitting jobs
           func - function to be executed
           depfuncs - tuple with functions which might be called from 'func'
           modules - tuple with module names to import
           callback - callback function which will be called with argument
                   list equal to callbackargs+(result,)
                   as soon as calculation is done
           callbackargs - additional arguments for callback function
           group - job group, is used when wait(group) is called to wait for
           jobs in a given group to finish
           globals - dictionary from which all modules, functions and classes
           will be imported, for instance: globals=globals()"""
        self.job_server = job_server
        self.func = func
        self.depfuncs = depfuncs
        self.modules = modules
        self.callback = callback
        self.callbackargs = callbackargs
        self.group = group
        self.globals = globals

    def submit(self, *args):
        """Submits function with *arg arguments to the execution queue
        """
        return self.job_server.submit(self.func, args, self.depfuncs,
                self.modules, self.callback, self.callbackargs,
                self.group, self.globals)

class RemoteNode(object):
    def __init__(self, hostid, ncpus):
        self._hostid = hostid
        self.ncpus = ncpus

class Server(object):
    """Parallel Python SMP execution server class
    """

    default_port = 60000
    default_secret = "epo20pdosl;dksldkmm"

    def __init__(self, ncpus="autodetect", ppservers=(), secret=None,
            restart=False, proto=2):
        """Creates Server instance

           ncpus - the number of worker processes to start on the local
                   computer, if parameter is omitted it will be set to
                   the number of processors in the system
           ppservers - list of active parallel python execution servers
                   to connect with
           secret - passphrase for network connections, if omitted a default
                   passphrase will be used. It's highly recommended to use a
                   custom passphrase for all network connections.
           restart - whether to restart worker process after each task completion
           proto - protocol number for pickle module

           With ncpus = 1 all tasks are executed consequently
           For the best performance either use the default "autodetect" value
           or set ncpus to the total number of processors in the system
        """

        if not isinstance(ppservers, tuple):
            raise TypeError("ppservers argument must be a tuple")

        self.logger = logging.getLogger('pp')
        self.logger.info("Creating server instance (pp-" + version+")")
        self.logger.info("Running on Python %s %s", sys.version.split(" ")[0],
                sys.platform)
        self.__tid = 0
        self.__active_tasks = 0
        self.__active_tasks_lock = threading.Lock()
        self.__queue = []
        self.__queue_lock = threading.Lock()
        self.__jobs = {}
        self.__jobs_lock = threading.Lock()
        self.__workers = []
        self.__dedicated_worker_pool = []
        self.__dedicated_worker_pool_lock = threading.Lock()
        self.__rworkers = []
        self.__rworkers_reserved = []
        self.__sourcesHM = {}
        self.__sfuncHM = {}
        self.__waittasks = []
        self.__waittasks_lock = threading.Lock()
        self._exiting = False
        self.__accurate_stats = True
        self.autopp_list = {}
        self.__active_rworkers_list_lock = threading.Lock()
        self.__restart_on_free = restart 
        self.__pickle_proto = proto
        
        self.__remote_nodes = {}
        self.__remote_nodes_lock = threading.Lock()
        
        self.load_average = 0.0
        self.__load_readings = collections.deque(maxlen=int(LOAD_AVERAGE_PERIOD / LOAD_AVERAGE_POLLING_INTERVAL))
        self.__load_readings.extend([0] * self.__load_readings.maxlen) #initially the load is 0
        self.__load_lock = threading.Lock()

        # add local directory and sys.path to PYTHONPATH
        pythondirs = [os.getcwd()] + sys.path

        if "PYTHONPATH" in os.environ and os.environ["PYTHONPATH"]:
            pythondirs += os.environ["PYTHONPATH"].split(os.pathsep)
        os.environ["PYTHONPATH"] = os.pathsep.join(set(pythondirs))

        atexit.register(self.destroy)
        self.__stats = {"local": _Statistics(0)}
        self.set_ncpus(ncpus)

        self.ppservers = []
        self.auto_ppservers = []

        for ppserver in ppservers:
            ppserver = ppserver.split(":")
            host = ppserver[0]
            if len(ppserver)>1:
                port = int(ppserver[1])
            else:
                port = Server.default_port
            if host.find("*") == -1:
                self.ppservers.append((host, port))
            else:
                if host == "*":
                    host = "*.*.*.*"
                interface = host.replace("*", "0")
                broadcast = host.replace("*", "255")
                self.auto_ppservers.append(((interface, port),
                        (broadcast, port)))
        self.__stats_lock = threading.Lock()
        
        ppcommon.start_thread("load", self._load_average_thread)
        
        if secret is not None:
            if not isinstance(secret, types.StringType):
                raise TypeError("secret must be of a string type")
            self.secret = str(secret)
        elif hasattr(user, "pp_secret"):
            secret = getattr(user, "pp_secret")
            if not isinstance(secret, types.StringType):
                raise TypeError("secret must be of a string type")
            self.secret = str(secret)
        else:
            self.secret = Server.default_secret
        self.__connect()
        self.__creation_time = time.time()
        print "pp local server started with %d workers, pid %d"% (self.__ncpus, os.getpid())
        self.logger.info("pp local server started with %d workers"
                % (self.__ncpus, ))

    def submit(self, func, args=(), depfuncs=(), modules=(),
            callback=None, callbackargs=(), group='default', globals=None, restrictions=[]):
        """Submits function to the execution queue

            func - function to be executed
            args - tuple with arguments of the 'func'
            depfuncs - tuple with functions which might be called from 'func'
            modules - tuple with module names to import
            callback - callback function which will be called with argument
                    list equal to callbackargs+(result,)
                    as soon as calculation is done
            callbackargs - additional arguments for callback function
            group - job group, is used when wait(group) is called to wait for
            jobs in a given group to finish
            globals - dictionary from which all modules, functions and classes
            will be imported, for instance: globals=globals()
        """

        # perform some checks for frequent mistakes
        if self._exiting:
            raise DestroyedServerError("Cannot submit jobs: server"\
                    " instance has been destroyed")

        if not isinstance(args, tuple):
            raise TypeError("args argument must be a tuple")

        if not isinstance(depfuncs, tuple):
            raise TypeError("depfuncs argument must be a tuple")

        if not isinstance(modules, tuple):
            raise TypeError("modules argument must be a tuple")

        if not isinstance(callbackargs, tuple):
            raise TypeError("callbackargs argument must be a tuple")

        if globals is not None and not isinstance(globals, dict):
            raise TypeError("globals argument must be a dictionary")

        for module in modules:
            if not isinstance(module, types.StringType):
                raise TypeError("modules argument must be a list of strings")

        tid = self.__gentid()

        if globals:
            modules += tuple(self.__find_modules("", globals))
            modules = tuple(set(modules))
            self.logger.debug("Task %i will autoimport next modules: %s" %
                    (tid, str(modules)))
            for object1 in globals.values():
                if isinstance(object1, types.FunctionType) \
                        or isinstance(object1, types.ClassType):
                    depfuncs += (object1, )

        task = _Task(self, tid, callback, callbackargs, group)

        self.__waittasks_lock.acquire()
        self.__waittasks.append(task)
        self.__waittasks_lock.release()

        # if the function is a method of a class add self to the arguments list
        if isinstance(func, types.MethodType) and func.im_self is not None:
            args = (func.im_self, ) + args

        # if there is an instance of a user deined class in the arguments add
        # whole class to dependancies
        for arg in args:
            # Checks for both classic or new class instances
            if isinstance(arg, types.InstanceType) \
                    or str(type(arg))[:6] == "<class":
                # do not include source for imported modules
                if ppcommon.is_not_imported(arg, modules):
                    depfuncs += tuple(ppcommon.get_class_hierarchy(arg.__class__))

        # if there is a function in the arguments add this
        # function to dependancies
        for arg in args:
            if isinstance(arg, types.FunctionType):
                depfuncs += (arg, )
                
                
        #Add task id
        args += (tid, )

        sfunc = self.__dumpsfunc((func, ) + depfuncs, modules)
        sargs = pickle.dumps(args, self.__pickle_proto)

        with self.__jobs_lock:
            if task.group not in self.__jobs:                                        
                job = Job(task.group, restrictions)
                job.worker = self.getFreeWorker()
                self.__jobs[task.group] = job
                self.__queue.append(job)
                
            self.__jobs[task.group].addTask((task, sfunc, sargs))
        
        #logging.getLogger(PARALLEL_LOGGER).debug("task %i submitted in group %s" , tid, group)
        logMessage("task %i submitted in group %s" % (tid, group), level = 5, logger=PARALLEL_LOGGER)
        self.__scheduler()
        return task

    def getFreeWorker(self):
        with self.__dedicated_worker_pool_lock:
            if len(self.__dedicated_worker_pool) == 0:
                worker = _Worker(self.__restart_on_free, self.__pickle_proto)
            else:
                worker = self.__dedicated_worker_pool.pop()
        return worker
    
    #TODO: this blocks if two users both wait for different groups...
    def wait(self, group=None):
        """Waits for all jobs in a given group to finish.
           If group is omitted waits for all jobs to finish
        """
        while True:
            self.__waittasks_lock.acquire()
            for task in self.__waittasks:
                if not group or task.group == group:
                    self.__waittasks_lock.release()
                    task.wait()
                    break
            else:
                self.__waittasks_lock.release()
                break

    def get_ncpus(self):
        """Returns the number of local worker processes (ppworkers)"""
        return self.__ncpus

    def set_ncpus(self, ncpus="autodetect"):
        """Sets the number of local worker processes (ppworkers)

        ncpus - the number of worker processes, if parammeter is omitted
                it will be set to the number of processors in the system"""
        if ncpus == "autodetect":
            ncpus = self.__detect_ncpus()
        if not isinstance(ncpus, int):
            raise TypeError("ncpus must have 'int' type")
        if ncpus < 0:
            raise ValueError("ncpus must be an integer > 0")
        if ncpus > len(self.__workers):
            self.__workers.extend([_Worker(self.__restart_on_free, 
                    self.__pickle_proto) for x in\
                    range(ncpus - len(self.__workers))])
        self.__stats["local"].ncpus = ncpus
        self.__ncpus = ncpus

    def get_active_nodes(self):
        """Returns active nodes as a dictionary
        [keys - nodes, values - ncpus]"""
        active_nodes = {}
        for node, stat in self.__stats.items():
            if node == "local" or node in self.autopp_list \
                    and self.autopp_list[node]:
                active_nodes[node] = stat.ncpus
        return active_nodes

    def get_stats(self):
        """Returns job execution statistics as a dictionary"""
        for node, stat in self.__stats.items():
            if stat.rworker:
                try:
                    stat.rworker.send("TIME")
                    stat.time = float(stat.rworker.receive())
                except:
                    self.__accurate_stats = False
                    stat.time = 0.0
        return self.__stats

    def print_stats(self):
        """Prints job execution statistics. Useful for benchmarking on
           clusters"""

        print "Job execution statistics:"
        walltime = time.time() - self.__creation_time
        statistics = self.get_stats().items()
        totaljobs = 0.0
        for ppserver, stat in statistics:
            totaljobs += stat.njobs
        print " job count | % of all jobs | job time sum | " \
                "time per job | job server"
        for ppserver, stat in statistics:
            if stat.njobs:
                print "    %6i |        %6.2f |     %8.4f |  %11.6f | %s" \
                        % (stat.njobs, 100.0*stat.njobs/totaljobs, stat.time,
                        stat.time/stat.njobs, ppserver, )
        print "Time elapsed since server creation", walltime

        if not self.__accurate_stats:
            print "WARNING: statistics provided above is not accurate" \
                  " due to job rescheduling"
        print

    # all methods below are for internal use only

    def insert(self, sfunc, sargs, job, task=None):
        """Inserts function into the execution queue. It's intended for
           internal use only (ppserver.py).
        """
        if not task:
            tid = self.__gentid()
            task = _Task(self, tid)
        with self.__jobs_lock:
            job.queue.append((task, sfunc, sargs))

        self.logger.debug("Task %i inserted" % (task.tid, ))
        self.__scheduler()
        return task

    def connect1(self, host, port, persistent=True):
        """Conects to a remote ppserver specified by host and port"""        
        try:
            rworker = _RWorker(host, port, self.secret, self, "STAT", persistent)
            ncpus = int(rworker.receive())
            hostid = host+":"+str(port)
            self.__stats[hostid] = _Statistics(ncpus, rworker)
            
            self.__remote_nodes_lock.acquire()
            self.__remote_nodes[hostid] = RemoteNode(hostid, ncpus)
            self.__remote_nodes_lock.release()

            for x in range(ncpus):
                rworker = _RWorker(host, port, self.secret, self, "EXEC", persistent)
                self.__update_active_rworkers(rworker.id, 1)
                # append is atomic - no need to lock self.__rworkers
                self.__rworkers.append(rworker)
            #creating reserved rworkers
            for x in range(ncpus):
                rworker = _RWorker(host, port, self.secret, self, "EXEC", persistent)
                self.__update_active_rworkers(rworker.id, 1)
                self.__rworkers_reserved.append(rworker)
            self.logger.debug("Connected to ppserver (host=%s, port=%i) \
                    with %i workers" % (host, port, ncpus))
            self.__scheduler()
        except:
            if SHOW_EXPECTED_EXCEPTIONS:
                self.logger.debug("Exception in connect1 method (possibly expected)", exc_info=True)
                
            #We can assume this connection is dead now
            self.__remote_nodes_lock.acquire()
            if hostid in self.__remote_nodes:
                del self.__remote_nodes[hostid]
            self.__remote_nodes_lock.release()
            
    def get_remote_node_list(self):
        remote_nodes = []
        self.__remote_nodes_lock.acquire()
        for remote_node in self.__remote_nodes:
            remote_nodes.append(remote_node)
        self.__remote_nodes_lock.release()
        return remote_nodes

    def __connect(self):
        """Connects to all remote ppservers"""
        for ppserver in self.ppservers:
            ppcommon.start_thread("connect1",  self.connect1, ppserver)

        self.discover = ppauto.Discover(self, True)
        for ppserver in self.auto_ppservers:
            ppcommon.start_thread("discover.run", self.discover.run, ppserver)

    def __detect_ncpus(self):
        """Detects the number of effective CPUs in the system"""
        #for Linux, Unix and MacOS
        if hasattr(os, "sysconf"):
            if "SC_NPROCESSORS_ONLN" in os.sysconf_names:
                #Linux and Unix
                ncpus = os.sysconf("SC_NPROCESSORS_ONLN")
                if isinstance(ncpus, int) and ncpus > 0:
                    return ncpus
            else:
                #MacOS X
                return int(os.popen2("sysctl -n hw.ncpu")[1].read())
        #for Windows
        if "NUMBER_OF_PROCESSORS" in os.environ:
            ncpus = int(os.environ["NUMBER_OF_PROCESSORS"])
            if ncpus > 0:
                return ncpus
        #return the default value
        return 1


    def __dumpsfunc(self, funcs, modules):
        """Serializes functions and modules"""
        hashs = hash(funcs + modules)
        if hashs not in self.__sfuncHM:
            sources = [self.__get_source(func) for func in funcs]
            self.__sfuncHM[hashs] = pickle.dumps(
                    (funcs[0].func_name, sources, modules),
                    self.__pickle_proto)
        return self.__sfuncHM[hashs]

    def __find_modules(self, prefix, dict):
        """recursively finds all the modules in dict"""
        modules = []
        for name, object in dict.items():
            if isinstance(object, types.ModuleType) \
                    and name not in ("__builtins__", "pp"):
                if object.__name__ == prefix+name or prefix == "":
                    modules.append(object.__name__)
                    modules.extend(self.__find_modules(
                            object.__name__+".", object.__dict__))
        return modules

    def __scheduler(self):
        """Schedules jobs for execution"""
        with self.__jobs_lock:    
            self.__schedule_dedicated_workers()  
            self.__remove_finished_jobs()     
            self.__schedule_local_workers()
            self.__schedule_remote_workers()
        
    def __remove_finished_jobs(self):
        for group, job in self.__jobs.items():
            if job.canBeRemoved():
                with self.__dedicated_worker_pool_lock:
                    self.__dedicated_worker_pool.append(job.worker)
                    job.worker = None
                del self.__jobs[group]
                
        
    def __schedule_dedicated_workers(self): 
        for job in self.__jobs.itervalues():
            if job.worker.is_free and len(job.queue) > 0:
                job.worker.is_free = False
                self.__stats["local"].njobs += 1
                self.__add_to_active_tasks(1)
                task = job.queue.pop()
                ppcommon.start_thread("run_local",  self._run_local, task+(job.worker, job)) 
    
    def __schedule_local_workers(self):        
        for worker in self.__workers:
            if worker.is_free:
                for job in self.__jobs.itervalues():
                    if not "local" in job.restrictions and len(job.queue) > 0:
                        task = job.queue.pop()
                        self.__send_local_task(task, worker, job)     
                        break       
    
    def __send_local_task(self, task, worker, job):
        worker.is_free = False
        self.__add_to_active_tasks(1)
        self.__stats["local"].njobs += 1
        ppcommon.start_thread("run_local",  self._run_local, task+(worker, job))        
     
    #Needs refactoring...   
    def __schedule_remote_workers(self):                    
        for rworker in self.__rworkers:
            if rworker.is_free:
                for job in self.__jobs.itervalues():
                    if not "remote" in job.restrictions and len(job.queue) > 0:
                        task = job.queue.pop()
                        self.__send_remote_task(task, rworker, job)
                        break
                
        if len(self.__queue) > self.__ncpus:
            for rworker in self.__rworkers_reserved:
                if rworker.is_free:
                    for job in self.__jobs.itervalues():
                        if not "remote" in job.restrictions and len(job.queue) > 0:
                            task = job.queue.pop()
                            self.__send_remote_task(task, rworker, job)
                            break
            
    def __send_remote_task(self, task, rworker, job):
        rworker.is_free = False
        self.__stats[rworker.id].njobs += 1
        self.__add_to_active_tasks(1)
        ppcommon.start_thread("run_remote",  self._run_remote, task+(rworker, job))  
    
    
    def _load_average_thread(self):
        while True:
            self.__record_load_average()
            time.sleep(LOAD_AVERAGE_POLLING_INTERVAL)
    
    def __record_load_average(self):
        # The number of active workers is not "thread safe", as per such, but as we are only reading the
        # values locking isn't really necessary
        number_of_active_workers = float(len(self.__jobs) + len(self.__workers) + len(self.__rworkers))
        # The same goes for the number of active tasks
        active_tasks = float(self.__active_tasks)
        #print "active workers: %d, active tasks: %d" % (number_of_active_workers, active_tasks)
        load = min([active_tasks/number_of_active_workers, 1.0]) #Limit max load to 100% (can be "more" due
                                                                        #to reserved workers
        # The average load is a simple average of the last n load readings. Anything more complicated
        # such as a weighted moving average (like the UNIX kernel load avg.) is not really required.
        # Using a deque automatically only keeps the last n readings, where n is the deque maxlen
        with self.__load_lock:
            self.__load_readings.append(load)
        
    def get_average_load(self):
        with self.__load_lock:
            oldest_load = self.__load_readings[0]
            current_load = self.__load_readings[-1]
            
        number_of_readings = self.__load_readings.maxlen
        self.load_average = self.load_average - (oldest_load / number_of_readings) + (current_load / number_of_readings)
        return self.load_average
                 
    def __get_source(self, func):
        """Fetches source of the function"""
        hashf = hash(func)
        if hashf not in self.__sourcesHM:
            #get lines of the source and adjust indent
            sourcelines = inspect.getsourcelines(func)[0]
            #remove indentation from the first line
            sourcelines[0] = sourcelines[0].lstrip()
            self.__sourcesHM[hashf] = "".join(sourcelines)
        return self.__sourcesHM[hashf]

    def _run_local(self, task, sfunc, sargs, worker, job):
        """Runs a job locally"""

        if self._exiting:
            return
        self.logger.info("Task %i started",  task.tid)

        start_time = time.time()

        
        sresult = None
        while sresult == None:
            try:
                worker.t.csend(sfunc)
                worker.t.send(sargs)
            except:
                if self._exiting:
                    return
                if SHOW_EXPECTED_EXCEPTIONS:
                    self.logger.debug("Exception sending task in _run_local (possibly expected)", exc_info=True)
                    
                #print "exception in run_local for group %s for worker %s when fetching result for tid %s: (thread is %s)" % (job.group, worker, task.tid, threading.current_thread())
                raise
            while sresult == None:
                try:
                    sresult = worker.t.receive(timeout=10)
                except pptransport.TimeoutException: #Can happen because of R crashing...
                    if worker.is_alive():
                        continue
                    else:
                        print "Worker appears to have crashed for task %d, reinserting task..."
                        
                        worker.stop()
                        job.worker = self.getFreeWorker()
                        self.insert(sfunc, sargs, job, task)
                        self.__scheduler()
                        return
                except:
                    if self._exiting:
                        return
                    if SHOW_EXPECTED_EXCEPTIONS:
                        self.logger.debug("Exception receiving result in _run_local (possibly expected)", exc_info=True)
                    raise

        task.finalize(sresult)

        # remove the job from the waiting list
        if self.__waittasks:
            with self.__waittasks_lock:
                self.__waittasks.remove(task)
        
        job.taskFinished()
        worker.free()
        
        self.__add_to_active_tasks(-1)
            
        if not self._exiting:
            self.__stat_add_time("local", time.time()-start_time)
        #self.logger.debug("Task %i ended",  task.tid)
        #logging.getLogger(PARALLEL_LOGGER).debug("Task %i ended", task.tid)
        logMessage("Task %i ended" % task.tid, level = 5, logger = PARALLEL_LOGGER)
        self.__scheduler()

    def _run_remote(self, task, sfunc, sargs, rworker, job):
        """Runs a task remotely"""
        self.logger.debug("Task (remote) %i started",  task.tid)

        try:
            rworker.csend(sfunc)
            rworker.send(sargs)
            sresult = rworker.receive()
            rworker.is_free = True
        except:
            self.logger.debug("Task %i failed due to broken network " \
                    "connection - rescheduling",  task.tid)
            self.insert(sfunc, sargs, job, task)
            self.__scheduler()
            self.__update_active_rworkers(rworker.id, -1)
            if rworker.connect("EXEC"):
                self.__update_active_rworkers(rworker.id, 1)
                self.__scheduler()
            return

        task.finalize(sresult)

        job.taskFinished()
        self.__add_to_active_tasks(-1)
        # remove the task from the waiting list
        if self.__waittasks:
            with self.__waittasks_lock:
                self.__waittasks.remove(task)

        self.logger.debug("Task (remote) %i ended",  task.tid)
        self.__scheduler()

    def __add_to_active_tasks(self, num):
        """Updates the number of active tasks"""
        self.__active_tasks_lock.acquire()
        self.__active_tasks += num
        self.__active_tasks_lock.release()

    def __stat_add_time(self, node, time_add):
        """Updates total runtime on the node"""
        self.__stats_lock.acquire()
        self.__stats[node].time += time_add
        self.__stats_lock.release()

    def __stat_add_job(self, node):
        """Increments job count on the node"""
        self.__stats_lock.acquire()
        self.__stats[node].njobs += 1
        self.__stats_lock.release()

    def __update_active_rworkers(self, id, count):
        """Updates list of active rworkers"""
        self.__active_rworkers_list_lock.acquire()

        if id not in self.autopp_list:
            self.autopp_list[id] = 0
        self.autopp_list[id] += count

        self.__active_rworkers_list_lock.release()

    def __gentid(self):
        """Generates a unique job ID number"""
        self.__tid += 1
        return self.__tid - 1

    def __del__(self):
        self._exiting = True

    def destroy(self):
        """Kills ppworkers and closes open files"""
        self._exiting = True
        self.__queue_lock.acquire()
        self.__queue = []
        self.__queue_lock.release()

        for worker in self.__workers:
            try:
                worker.t.send("E")
            except:
                pass
            
        time.sleep(0.2)
        for worker in self.__workers:
            try:
                worker.t.close()
                if sys.platform.startswith("win"):
                    os.popen('TASKKILL /PID '+str(worker.pid)+' /F')
                else:
                    os.kill(worker.pid, 9)
                    os.waitpid(worker.pid, 0)
            except:
                pass


class DestroyedServerError(RuntimeError):
    pass
    
class Job(object):
    def __init__(self, group, restrictions):
        assert(type(restrictions) is list)
        self.group = group
        self.queue = collections.deque()
        self.restrictions = restrictions
        self._tasksAdded = 0
        self._tasksCompleted = 0 
        self._lock = threading.Lock()
        self._lastActivity = time.time()
        self.worker = None
        
    def addTask(self, task):
        with self._lock:
            self.queue.append(task)
            self._tasksAdded += 1
            self._lastActivity = time.time()
        
    def taskFinished(self):
        with self._lock:
            self._tasksCompleted += 1
            self._lastActivity = time.time()
        
    def canBeRemoved(self):
        with self._lock:
            if time.time() > (JOB_MAX_IDLE_TIME + self._lastActivity):
                if self._tasksAdded == self._tasksCompleted:
                    return True
                
            return False
        
# Parallel Python Software: http://www.parallelpython.com
