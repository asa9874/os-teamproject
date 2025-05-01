from scheduler import BaseScheduler
from collections import deque

class SRTNScheduler(BaseScheduler):
    def schedule(self): #SRTN스케줄링 선점방식으로 프로세서가 도착시 RT가 작은 프로세서를 실행 / 똑같을 시 AT기준으로 실행
        for processor in self.processors_info:
            if not processor.is_available():
                processor.execute(self.current_time)

    def assign_process(self):
        for processor in self.processors_info:
            if not processor.is_available() and self.ready_queue:
                shortest = min(self.ready_queue, key=lambda p: (p.remaining_time, p.arrival)) #RT를 기준으로 보조키 AT를 기준으로 정렬
                if shortest.remaining_time < processor.current_process.remaining_time: #실행중인것과 큐에서 짧은 프로세스를 비교(false시 그대로 실행)
                    self.ready_queue.remove(shortest) #큐에서 실행할 프로세서를 제거
                    self.ready_queue.appendleft(processor.current_process) #큐에 실행중인 프로세서를 삽입
                    processor.drop_process()
                    processor.assign_process(shortest, self.current_time) #실행
            if processor.is_available(): #프로세서에 비어있을 떄
                if self.ready_queue:
                    self.ready_queue = deque(sorted(self.ready_queue, key=lambda p: (p.remaining_time, p.arrival), reverse=True)) #RT를 기준으로 보조키 AT를 보조키로 정렬
                    next_process = self.ready_queue.pop() #정렬된 큐에서 가장 RT가 짧은 프로세서를 next_process로 지정
                    processor.assign_process(next_process, self.current_time) #실행
                    break