from scheduler import BaseScheduler
from collections import deque

class HRRNScheduler(BaseScheduler):
    def assign_process(self):
        for processor in self.processors_info:
            if processor.is_available():
                if len(self.ready_queue) > 1:
                    self.ready_queue = deque(sorted(self.ready_queue,key=lambda p: self.calculate_response_ratio(p),reverse=True))
                    #아래에 선언된 함수에서 계산한 response ratio를 기준으로 정렬
                if self.ready_queue:
                    process = self.ready_queue.popleft()
                    processor.assign_process(process, self.current_time)

    def calculate_response_ratio(self, process):
        #Response Ratio = (WT + BT) / BT
        return (process.wait_time + process.burst) / process.burst