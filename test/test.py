from core.process import Process
from core.processor import Processor
from algorithm.custom_scheduler import MyScheduler

def main():
    processes = [
        Process(pid=1, arrival=0, burst=5),
        Process(pid=2, arrival=2, burst=8),
        Process(pid=3, arrival=4, burst=6)
    ]
    processors=[
        Processor(id=1,type="P"),
    ]
    
    myScheduler = MyScheduler(processes, processors)

    while myScheduler.has_next():
        myScheduler.schedule()
    

if __name__ == '__main__':
    main()