from scheduler import BaseScheduler
from collections import deque

class HRRNScheduler(BaseScheduler):
    """
    응답 비율(Response Ratio)을 기준으로 정렬하여 프로세스를 할당하는 스케줄러(비선점)
    Response Ratio = (대기 시간 + 실행 시간) / 실행 시간
    """

    def assign_process(self) -> None:
        for processor in self.processors_info:
            if processor.is_process_empty(): 
                if len(self.ready_queue) > 1: # 길이 2 이상일 때 정렬
                    self.ready_queue = deque(sorted(self.ready_queue,key=lambda p: self.calculate_response_ratio(p),reverse=True))
                    
                if self.ready_queue: 
                    process = self.ready_queue.popleft()
                    processor.assign_process(process, self.current_time)

    def calculate_response_ratio(self, process):
        return (process.wait_time + process.burst) / process.burst