from scheduler import BaseScheduler
from collections import deque

class SPNScheduler(BaseScheduler):
    """
    비선점
    실행시간을 기준으로 정렬하여 프로세스를 할당하는 스케줄러
    """
    def assign_process(self):
        for processor in self.processors_info:
            if processor.is_process_empty(): # 프로세서 비어있는 경우 프로세스 따로 할당x (비선점)
                if len(self.ready_queue) > 1: # ready_queue가 2개 이상일 때 실행
                    self.ready_queue = deque(sorted(self.ready_queue, key = lambda p: (p.burst, p.arrival), reverse=True)) # ready_queue를 실행시간, 도착시간(실행시간이 같을 경우) 순으로 정렬

                if self.ready_queue: # ready_queue가 비어있지 않은 경우
                    process = self.ready_queue.pop() 
                    processor.assign_process(process,self.current_time) 