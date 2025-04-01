from abc import ABC, abstractmethod

# 추상 클래스
class BaseScheduler(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def run(self, processes, processors_info):
        pass