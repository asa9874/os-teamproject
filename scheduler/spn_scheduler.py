from scheduler import BaseScheduler

class SPNScheduler(BaseScheduler):
    def schedule(self): # SPN 스케줄링은 FCFS와 같은 방식으로 진행
        for processor in self.processors_info:
            if not processor.is_available():
                processor.execute(self.current_time)
        
    def assign_process(self):
        for processor in self.processors_info:
            if processor.is_available(): # 프로세서 비어있는 경우 프로세스 따로 할당x (비선점)
                if len(self.ready_queue) > 1: # ready_queue가 2개 이상일 때 실행
                    self.ready_queue = sorted(self.ready_queue, key = lambda p: (p.burst, p.arrival), reverse=True) # ready_queue를 실행시간, 도착시간(실행시간이 같을 경우) 순으로 정렬

                if self.ready_queue:
                    process = self.ready_queue.pop() #FIFO 방식으로 프로세스 할당
                    processor.assign_process(process,self.current_time)
                    break