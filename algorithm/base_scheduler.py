from abc import ABC, abstractmethod
from core.process import Process
from typing import List, Any
from core.processor import Processor

# 추상 클래스
class BaseScheduler(ABC):
    def __init__(self, processes: List[Process], processors_info: List[Processor]) -> None:
        self.processes = processes
        self.processors_info = processors_info
        self.current_time = 0
        self.ready_queue = []  # 대기 큐
        self.current_power = 0  # 현재 프로세서의 전력 사용량

    @abstractmethod
    def schedule(self)-> None:
        """
        스케줄링 알고리즘을 실행하여 프로세스를 정해진 방식으로 처리(구현해야함)
        """
        pass
    
    @abstractmethod
    def assign_process(self, process: Process) -> None:
        """
        프로세서에 프로세스를 할당하는 메서드(구현해야함)
        """
        pass
    
    def process_waiting_time_update(self) -> None:
        """
        프로세스의 대기 시간을 업데이트
        """
        for process in self.processes:
            if process.arrival <= self.current_time and not process.is_running():
                process.wait_time+=1

    
    def hasNext(self)-> bool:
        """
        프로세스가 모두 종료되었는지 확인
        """
        return any(process.turnaround_time is None for process in self.processes)
    
    
    def get_current_power(self) -> float:
        """
        현재 프로세서의 전력 사용량을 계산하여 반환
        """
        power = 0.0
        for processor in self.processors_info:
            power += processor.used_power
        return power
    
    def processer_powerOff(self):
        """
        꺼야하는 프로세서의 전원을 끔
        """
        for processor in self.processors_info:
            if processor.is_available() and processor.PowerOn:
                processor.PowerOn = False
    
    def update_current_time(self) -> None:
        """
        현재 시간을 1초 증가시킴
        """
        self.current_time += 1
        
    def get_processs(self):
        """
        프로세스 리스트를 반환
        """
        return self.processes
    
    def get_processors(self):
        """
        프로세서 리스트를 반환
        """
        return self.processors_info
        
    def log_state(self) -> None:
        """
        현재 시간과 프로세스 상태를 출력 (디버깅용)
        """
        waiting_processes = [p for p in self.processes if not p.is_completed() and not p.is_running()]
        ended_processes = [p for p in self.processes if p.is_completed()]
        
        print("-----------")
        print(f"현재 시간: {self.current_time}")
        print(f"현재 전력 사용량: {self.get_current_power()}")
        print("실행 중인 프로세스")
        for processer in self.processors_info:
            if(processer.PowerOn == False): print(f"[꺼짐]", end="")
            else: print(f"[켜짐]", end="")
            print(f"프로세서 {processer.id} |", end="")
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
        
        
