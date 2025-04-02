from algorithm import BaseScheduler


class MyScheduler(BaseScheduler):
    def schedule(self):
        pass
    
    def hasNext(self):
        return super().hasNext()