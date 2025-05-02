from abc import ABC, abstractmethod
from core.process import Process
from typing import List, Any
from core.processor import Processor
from collections import deque
import heapq

# 추상 클래스
class BaseScheduler(ABC):
    def __init__(self, processes: List[Process], processors_info: List[Processor]) -> None:
        self.processes = processes                  # 프로세스 리스트
        # P 코어 우선할당
        self.processors_info = sorted(processors_info, key=lambda p: 0 if p.type.upper() == 'P' else 1)
        self.current_time = 0                       # 현재 시간
        self.ready_queue = deque()                  # 대기 큐
        self.current_power = 0                      # 현재 프로세서의 전력 사용량

    def simulate(self) -> None:
        """
        시뮬레이션을 실행하는 메서드
        """
        while self.hasNext():
            self.ready_queue_update()           # 대기 큐 업데이트
            self.schedule()                     # 스케줄링 알고리즘 실행
            self.assign_process()               # 프로세서에 프로세스 할당
            self.processor_power_off()           # 프로세서 전원 끄기
            self.process_waiting_time_update()  # 대기 중인 프로세스의 대기 시간 업데이트
            self.log_state()                    # 현재 상태 출력 (디버깅용)
            self.update_current_time()          # 현재 시간 업데이트

    
    
    @abstractmethod
    def assign_process(self) -> None:
        """
        프로세서에 레디큐의 프로세스를 할당하는 메서드(구현해야함)
        
        """
        pass
    
    
    def schedule(self)-> None:
        """
        프로세서들을 일시키는 메서드(프로세스 할당여부는 execute에서 확인함)
        """
        for processor in self.processors_info:
            processor.execute(self.current_time)
    
    def ready_queue_update(self) -> None:
        """
        대기 큐를 업데이트하는 메서드
        충돌시 PID가 큰게 우선으로 할당됩니다.
        """
        process_priority_queue = []
        for process in self.processes:
            # 프로세스가 도착했지만 대기 큐에 없고 실행 중이지 않으며 남은 시간이 있는 경우
            if process.arrival <= self.current_time and not process.is_running() and process not in self.ready_queue and process.remaining_time > 0:
                heapq.heappush(process_priority_queue, (-process.pid, process))
        while process_priority_queue:
            process = heapq.heappop(process_priority_queue)[1]
            self.ready_queue.appendleft(process)


    def process_waiting_time_update(self) -> None:
        """
        대기 중인 프로세스의 대기 시간을 업데이트하는 메서드
        """
        for process in self.processes:
            # 프로세스가 도착했지만 실행 중이지 않으며 남은 시간이 있는 경우
            if process.arrival <= self.current_time and not process.is_running() and process.remaining_time > 0:
                process.wait_time+=1

    
    def hasNext(self)-> bool:
        """
        시뮬레이션이 계속 진행될 수 있는지 확인하는 메서드
        """
        return any(process.turnaround_time is None for process in self.processes)
    
    
    def get_current_power(self) -> float:
        """
        전체 프로세서의 전력 사용량 합 계산하는 메서드
        """
        power = 0.0
        for processor in self.processors_info:
            power += processor.used_power
        return power
    
    def processor_power_off(self):
        """
        프로세서의 전원을 끄는 메서드
        (할당된 프로세스가 없고 대기 중인 프로세스가 없고 전원이 켜져 있는 경우)
        """
        for processor in self.processors_info:
            if processor.is_available() and processor.PowerOn:
                processor.PowerOn = False
    
    def update_current_time(self) -> None:
        self.current_time += 1
        
    def get_process(self):
        return self.processes
    
    def get_processors(self):
        return self.processors_info

    # 디버깅용 출력 메서드들

    def log_state(self) -> None:
        """
        현재 시간과 프로세스 상태를 출력 (디버깅용)
        """
        waiting_processes = [p for p in self.processes if not p.is_completed() and not p.is_running()]
        ended_processes = [p for p in self.processes if p.is_completed()]
        
        print("-----------")
        print(f"현재 시간: {self.current_time}")
        print(f"현재 전력 사용량: {self.get_current_power()}")
        print(f"현재 대기 큐:", end="")
        for process in self.ready_queue:
            print(f" {process.pid}", end="")
        print()
        print("실행 중인 프로세스")
        for processer in self.processors_info:
            if(processer.PowerOn == False): print(f"[꺼짐]", end="")
            else: print(f"[켜짐]", end="")
            print(f"프로세서 {processer.id} |", end="")
            if(processer.time_quantum is not None): print(f"시간 쿼텀: {processer.time_quantum}", end="")
            if(processer.current_process):
                processer.current_process.log_state()
            else:
                print("없음")
            
        print("쉬는 프로세스")
        for process in waiting_processes:
            process.log_state()
        
        print("종료된 프로세스")
        for process in ended_processes:
            process.log_state()
        print("-----------")
        print()
        print()
    
    def log_process_queue(self) -> None:
        """
        프로세스 큐를 출력 (디버깅용)
        """
        cell_width = 5
        header = "프로세서 시간|"
        for t in range(1, self.current_time):
            header += f"{str(t).rjust(cell_width)}"
        print(header)
        for processor in self.processors_info:
            row = f"프로세서 {processor.id}".ljust(9) + "|"
            for pid in processor.process_queue:
                cell = str(pid) if pid is not None else "-"
                row += f"{cell.rjust(cell_width)}"
            print(row)

        # 평균 NTT 값 (성능평가용)
        ended_processes = [p for p in self.processes if p.is_completed()]
        sum_ntt = 0
        for process in ended_processes:
            sum_ntt += process.normalized_turnaround_time
        avg_ntt = sum_ntt / len(ended_processes)
        print("평균 NTT : ", avg_ntt)

        
