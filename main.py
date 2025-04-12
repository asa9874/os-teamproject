from core import Process
from core import Processor
from algorithm import FCFSSceduler


# 시간기준은 시작을 기준임 
# 현재 시간: 0초 -> 0초에 프로세스 할당끝난시점,시동전력 포함
# 현재 시간: 1초 -> 1초에 프로세스 끝,프로세스 할당끝난시점, 0초 단계 사용전략 포함
def main():
    processes = [
        Process(pid=1, arrival=0, burst=3),
        Process(pid=2, arrival=1, burst=7),
        Process(pid=3, arrival=3, burst=2),
        Process(pid=4, arrival=5, burst=5),
        Process(pid=5, arrival=6, burst=3),
    ]
    processors = [
        Processor(id=1, type="E"), #P or E
    ]

    # 테스트 할때 클래스명만 바꿔주면 됨
    myScheduler = FCFSSceduler(processes, processors)
    myScheduler.simulate() # 시뮬레이션 실행
    print("끝")
    myScheduler.log_process_queue()
    

if __name__ == '__main__':
    main()