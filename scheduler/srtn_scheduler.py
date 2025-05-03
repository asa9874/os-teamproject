from scheduler import BaseScheduler
from collections import deque
"""

"""
class SRTNScheduler(BaseScheduler):
    def assign_process(self):
        """
        선점
        Remain Time을 기준으로 정렬하여 프로세스를 할당하는 스케줄러
        실행중인 프로세스 남은시간 > 대기큐에서 남은시간이 가장 짧은 프로세스의 남은시간 => 선점
        """
        for processor in self.processors_info:
            if not processor.is_process_empty() and self.ready_queue: #선점
                shortest = min(self.ready_queue, key=lambda p: (p.remaining_time, p.arrival)) #RT를 기준으로 보조키 AT를 기준으로 정렬

                if shortest.remaining_time < processor.current_process.remaining_time: # 선점 조건
                    self.ready_queue.remove(shortest)                                  # 큐에서 실행할 프로세스를 제거
                    self.ready_queue.appendleft(processor.current_process)             # 큐에 실행중인 프로세스를 삽입
                    processor.preempt_process()                                        # 프로세서 비움     
                    processor.assign_process(shortest, self.current_time)              # 새로운 프로세스 할당
            
            if processor.is_process_empty(): #프로세서에 비어있을 떄
                if self.ready_queue:
                    self.ready_queue = deque(sorted(self.ready_queue, key=lambda p: (p.remaining_time, p.arrival), reverse=True)) #RT를 기준으로 보조키 AT를 보조키로 정렬
                    next_process = self.ready_queue.pop() #정렬된 큐에서 가장 RT가 짧은 프로세서를 next_process로 지정
                    processor.assign_process(next_process, self.current_time) #실행