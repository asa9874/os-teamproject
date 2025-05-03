from scheduler import BaseScheduler

class RRScheduler(BaseScheduler):
    """
    시간 할당량이 만료되면 프로세스를 회수하여 다시 큐에 넣는 방식의 스케줄러(선점)
    """
    def assign_process(self):
        for processor in self.processors_info:
            # 실행 중이면 할당량 만료시 회수
            if not processor.is_process_empty() and processor.is_time_quantum_expired(self.current_time):
                self.ready_queue.appendleft(processor.current_process)
                processor.preempt_process()
            
            # 비어있는 경우 할당
            if processor.is_process_empty():
                if self.ready_queue:
                    process = self.ready_queue.pop() 
                    processor.assign_process(process,self.current_time)
