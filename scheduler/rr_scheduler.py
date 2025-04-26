from scheduler import BaseScheduler

class RRScheduler(BaseScheduler):
    # RRScheduler는 FCFS와 비슷하게 처리된다.
    def schedule(self):
        for processor in self.processors_info:
            if not processor.is_available():
                processor.execute(self.current_time)
                
    # RRScheduler는 FCFS처럼 할당하지만 실행 중에 할당량 만료 시 회수가 이루어진다.
    def assign_process(self):
        for processor in self.processors_info:
            # 실행 중이면 할당량 만료시 회수
            if not processor.is_available() and processor.is_time_quantum_expired(self.current_time):
                self.ready_queue.appendleft(processor.current_process)
                processor.drop_process()
            
            # 비어있는 경우 할당
            if processor.is_available():
                if self.ready_queue:
                    process = self.ready_queue.pop() #FIFO 방식으로 프로세스 할당
                    processor.assign_process(process,self.current_time)
                    break
