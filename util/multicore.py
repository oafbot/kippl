import multiprocessing as mp

class Multicore:
    def __init__(self, cores=mp.cpu_count()):
        """multi-core processing."""
        self.queue = mp.Queue()
        self.cores = cores - 2 if cores > 4 else cores
        self.procs = {} # processes
        self.prods = {} # product returned from porcesses
    
    def run(self, tasks=None, func=None, args=[]):
        for n in range(0, self.cores):
            """Split tasks according to number of cores available."""
            start = n * (len(tasks)//self.cores)
            end   = ((n+1) * (len(tasks)//self.cores)) - 1
            """Pass queue object, process id and divided task as keyword args."""
            kwarg = dict(queue=self.queue, pid=n, tasks=tasks[start:end])
            """Spawn processes."""
            self.procs[n] = mp.Process(target=func, args=args, kwargs=kwarg)
            self.procs[n].start()
            
            if n == self.cores-1 and len(tasks)%self.cores != 0:
                """If there are remaining tasks, spawn an additional job."""
                start = end+1
                end   = len(tasks)-1
                """Pass queue object, process id and divided task as keyword args."""
                kwarg = dict(queue=self.queue, pid=n, tasks=tasks[start:])
                self.procs[n+1] = mp.Process(target=func, args=args, kwargs=kwarg)
                self.procs[n+1].start()
        """retrieve processes."""
        for n in self.procs: self.prods[n] = self.queue.get()
        """Reconstruct and return the completed process."""
        repackage = []
        for n in self.prods: repackage += self.prods[n]
        return repackage
    
