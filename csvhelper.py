class CsvHelper:
    def __init__(self, path="./data.csv", columns=""):
        import os
        import codecs
        self.path = path 
        if not os.path.isfile(path):
            self.data = ','.join(columns)+"\n"
        else:
            self.data=''
        self.file = codecs.open(path, "ab+", 'utf-8')
    
    def LineIn(self, values):
        self.data += ','.join(values)+"\n"
        #return self.data

    def LineOut(self):
        self.file.write(self.data.encode('utf-8'))
        self.data = ''
    
    def Close(self):
        self.file.close()
    
    def Scrub(self,target):
        import re
        target=target.replace(",", "")
        target=re.sub("\n", " ", target)
        target=re.sub("\r", " ", target)
        return target