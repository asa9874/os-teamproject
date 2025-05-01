from scheduler import BaseScheduler
from collections import deque

class SRTNScheduler(BaseScheduler):
    def schedule(self): #SRTN스케줄링 선점방식으로 프로세서가 도착시 RT가 작은 프로세서를 실행 / 똑같을 시 AT기준으로 실행행
        for processor in self.processors_info:
            if not processor.is_available():
                processor.execute(self.current_time)

    def assign_process(self):
        for processor in self.processors_info:
            if not processor.is_available() and self.ready_queue:
                shortest = min(self.ready_queue, key=lambda p: (p.remaining_time, p.arrival)) #RT를 기준으로 보조키 AT를 기준으로 정렬
                if shortest.remaining_time < processor.current_process.remaining_time:
                    self.ready_queue.remove(shortest)
                    self.ready_queue.appendleft(processor.current_process)
                    processor.drop_process()
                    processor.assign_process(shortest, self.current_time)
            if processor.is_available(): #프로세서에 비어있을 떄
                if self.ready_queue: #RT를 기준으로 보조키 AT를 보조키로 정렬
                    self.ready_queue = deque(sorted(self.ready_queue, key=lambda p: (p.remaining_time, p.arrival), reverse=True))
                    next_proc = self.ready_queue.pop()
                    processor.assign_process(next_proc, self.current_time)
                    break