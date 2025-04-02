from core import Process
from core import Processor
from algorithm.TestSceduler import TestSceduler

def main():
    processes = [
        Process(pid=1, arrival=0, burst=5),
        Process(pid=2, arrival=2, burst=8),
        Process(pid=3, arrival=4, burst=6)
    ]
    processors = [
        Processor(id=1, type="P"),
    ]

    myScheduler = TestSceduler(processes, processors)

    while myScheduler.hasNext():
        myScheduler.schedule()
        myScheduler.log_state()
    print("끝")
    

if __name__ == '__main__':
    main()