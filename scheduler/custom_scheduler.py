from collections import deque

"""
CustomAlgorithm => LRTN(Long Remaining Time Next)
동기: 가장 비효율적인 최악의 스케줄링을 구현해보자

아이디어: SRTN을 반대로 생각해서 convoy 효과, starvation 효과를 극대화하자
즉 평균 NTT값을 높여보자

"""

"""
만약 context switching에 자원이 든다면
rr방식(1초마다) + finishDelay(프로세스 1초 남았을 때 대기상태로 돌릴 예정
"""

from scheduler import BaseScheduler

class CustomScheduler(BaseScheduler):
    def schedule(self):
        for processor in self.processors_info:
            if not processor.is_available():
                processor.execute(self.current_time)
        
    def assign_process(self):
        def detect_arrivals(current_time) -> bool: # 현재시간, 프로세스들의 도착 시간을 비교함 -> 둘이 같을 경우 프로세스 도착 확인(True)
            arrivals = [i.arrival for i in self.ready_queue]

            return current_time in arrivals

        for processor in self.processors_info:
            # 사용중일 경우
            if not processor.is_available():
                # 현재 프로세스 RT <= 1 경우 맨 뒤로 보냄
                if processor.current_process.remaining_time <= 1 and self.ready_queue:
                    print("delay")
                    self.ready_queue.appendleft(processor.current_process)
                    processor.drop_process()
            
                # 신규 도착 -> 더 긴 작업이 있을 경우 선점
                elif detect_arrivals(self.current_time) and len(self.ready_queue)+1 > 1: # 프로세스 도착 & 프로세스수 2개 이상
                    self.ready_queue = deque(sorted(self.ready_queue, key = lambda p: (p.remaining_time, p.arrival))) # 남은 시간 순으로 오름차순
                    Longest_RT_P = self.ready_queue[-1]
                    #print(Longest_RT_P.remaining_time, processor.current_process.remaining_time)

                    if Longest_RT_P.remaining_time > processor.current_process.remaining_time: # 현재 프로세스의 RT값 보다 큰 RT가 ReadyQueue에 있을 경우 선점
                        print("RT")
                        self.ready_queue.appendleft(processor.current_process)
                        processor.drop_process()

            # 비어있는 경우 할당
            if processor.is_available():
                if self.ready_queue:
                    process = self.ready_queue.pop() #FIFO 방식으로 프로세스 할당
                    processor.assign_process(process,self.current_time)
                    break

    

    
    
    
