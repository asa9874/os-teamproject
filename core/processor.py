class Processor:
    def __init__(self,id,type):
        self.id = id
        self.type = type
        


    def __repr__(self):
        return f"Process(pid={self.pid}, arrival={self.arrival}, burst={self.burst})"