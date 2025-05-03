from collections import deque
from scheduler import BaseScheduler

class CustomScheduler(BaseScheduler):
    """
    CustomAlgorithm => RR + FinishDelay(RemainingTime이 1초 남았을 때 대기상태)
    동기: 가장 비효율적인 최악의 스케줄링을 구현해보자

    아이디어: RR(qt=1) => 과도한 contextSwitching -> overhead 극대화
            FinishDelay => starvation, avg_NTT 극대화

    평가지표: 모든 p의 평균 NTT값

    제약: 프로세서가 쉬면 안됨
    """
    def assign_process(self) -> None:
        def avg_RT(): # readyQueue의 평균 RT값
            return sum([i.remaining_time for i in self.ready_queue]) / (len(self.ready_queue)) if self.ready_queue else 0

        for processor in self.processors_info:
            # 프로세서 사용 불가 경우
            if not processor.is_process_empty():
                if processor.is_time_quantum_expired(self.current_time):
                    self.ready_queue.appendleft(processor.current_process)  # 대기 큐의 맨 앞에 추가
                    processor.preempt_process()  # 프로세서를 비움
            
            # 프로세서 사용 가능 경우
            if processor.is_process_empty():
                if self.ready_queue: # 대기 큐에 프로세스가 존재하는 경우
                    if avg_RT() > 1: # readyQueue에 RT값이 1이상인 프로세스가 존재하는 경우
                        while self.ready_queue[-1].remaining_time <= 1: # ready_queue[-1]의 RT값이 1이상이 나올때 까지 appendleft
                            last_process = self.ready_queue.pop()
                            self.ready_queue.appendleft(last_process)
                            
                    else:
                        self.ready_queue = deque(sorted(self.ready_queue, key = lambda p: (p.burst, p.arrival))) # 평균 NTT 상승을 위한 프로세스 BT순으로 정렬
                        
                    # FIFO 방식으로 대기 큐에서 프로세스를 할당
                    process = self.ready_queue.pop()
                    processor.assign_process(process, self.current_time)
