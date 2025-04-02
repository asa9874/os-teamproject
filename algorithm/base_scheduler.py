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
    
    