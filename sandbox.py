from core import Process
from core import Processor
from scheduler import CustomScheduler
from simulator import SchedulerApp
from scheduler import SchedulerType

# 스케쥴러 작동 테스트 하는 곳
def main():
    app = SchedulerApp(scheduler_type=SchedulerType.FCFS)
    processes = [
        Process(pid=1, arrival=0, burst=7),
        Process(pid=2, arrival=1, burst=6),
        Process(pid=3, arrival=3, burst=5),
        Process(pid=4, arrival=4, burst=10),
        Process(pid=5, arrival=6, burst=5),
        Process(pid=6, arrival=40, burst=5),    
        ]
    app.add_processes(processes)
    app.add_processor(id=1, type="E")
    app.run()
    



if __name__ == '__main__':
    main()