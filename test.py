from core import Process
from core import Processor
from algorithm.TestSceduler import TestSceduler


# 시간기준은 시작을 기준임 
# 현재 시간: 0초 -> 0초에 프로세스 할당끝난시점,시동전력 포함
# 현재 시간: 1초 -> 1초에 프로세스 끝,프로세스 할당끝난시점, 0초 단계 사용전략 포함
def main():
    processes = [
        Process(pid=1, arrival=0, burst=3),
        Process(pid=2, arrival=1, burst=7),
    ]
    processors = [
        Processor(id=1, type="P"),
    ]

    # 테스트 할때 클래스명만 바꿔주면 됨
    myScheduler = TestSceduler(processes, processors)
    while myScheduler.hasNext():
        myScheduler.schedule()
        myScheduler.assign_process()
        myScheduler.processer_powerOff()
        myScheduler.process_waiting_time_update()
        myScheduler.log_state()
        myScheduler.update_current_time()
    print("끝")
    

if __name__ == '__main__':
    main()