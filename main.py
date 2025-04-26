from core import Process
from core import Processor
from scheduler import FCFSScheduler
from simulator import SchedulerApp
from scheduler import SchedulerType

# 시간기준은 시작을 기준임 
# 현재 시간: 0초 -> 0초에 프로세스 할당끝난시점,시동전력 포함
# 현재 시간: 1초 -> 1초에 프로세스 끝,프로세스 할당끝난시점, 0초 단계 사용전략 포함
def main():
    app = SchedulerApp(scheduler_type=SchedulerType.FCFS)
    processes = [
        Process(pid=1, arrival=0, burst=3),
        Process(pid=2, arrival=1, burst=7),
        Process(pid=3, arrival=3, burst=2),
        Process(pid=4, arrival=5, burst=5),
        Process(pid=5, arrival=6, burst=3),
    ]
    app.add_processes(processes)
    app.add_processor(id=1, type="E")
    app.run()
    



if __name__ == '__main__':
    main()