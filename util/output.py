class Output:

    def __init__(self, trace=True):
        self.count = 0.0
        self.trace = trace
        
    def lineout(self, output):
        """Dynamic single line output."""
        length = len(str(output))
        delete = "\b" * (length+2)
        print "{0}{1:{2}}".format(delete, output, length),
    
    def on_status(self, label="Processed"):
        """Progress bar rendering."""
        import sys
        if self.trace:
            numerator = self.count + 1.0
            if numerator >= self.denominator:
                self.status_end(label)
            elif sys.stdout.isatty():
                perc = numerator/self.denominator if self.denominator != 0 else 0
                bar  = ": |" + "==|" * int(perc*10) + int(10-(perc*10)+1)*"---" + " "
                self.lineout(label + bar + str(int(perc*100))+"%")
            self.count += 1.0
    
    def statusbar(self, task, label="Processed", title=None, trace=None):    
        self.count = 0.0
        self.label = label
        self.trace = trace if trace else self.trace
        self.denominator = task
        if self.trace:
            if title: print title
            self.lineout(label+": |" + "---" * 10 + " 0%")
    
    def status_end(self, label="Processed"):
        self.count = 0.0
        if self.trace:
            self.lineout(label+": |" + "==|" * 10 + " 100%\n\n")
    
    def exec_time(self, start):
        import datetime
        elapsed = datetime.datetime.now() - start
        hours, rem = divmod(elapsed.seconds, 3600)
        mins, secs = divmod(rem, 60)
        hh = str(hours) if hours > 9 else "0" + str(hours)
        mm = str(mins)  if mins  > 9 else "0" + str(mins)
        ss = str(secs)  if secs  > 9 else "0" + str(secs)        
        
        print "\nexecution: ", elapsed.days, "days, ", hh+":"+mm+":"+ss
    