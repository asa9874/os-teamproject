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

    @abstractmethod
    def schedule(self)-> None:
        """
        스케줄링 알고리즘을 실행하여 프로세스를 정해진 방식으로 처리
        """
        pass
    
    def hasNext(self)-> bool:
        """
        프로세스가 모두 종료되었는지 확인
        """
        return any(process.turnaround_time is None for process in self.processes)
    
    def log_state(self) -> None:
        """
        현재 시간과 프로세스 상태를 출력 (디버깅용)
        """
        running_processes = [p for p in self.processes if p.is_running()]
        waiting_processes = [p for p in self.processes if not p.is_completed() and not p.is_running()]
        
        print(f"\n[Time {self.current_time}]")
        print(f"Running: {[p.pid for p in running_processes]}")
        print(f"Waiting: {[p.pid for p in waiting_processes]}")
        
