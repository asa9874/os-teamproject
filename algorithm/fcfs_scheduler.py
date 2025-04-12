from algorithm import BaseScheduler

class FCFSSceduler(BaseScheduler):
    def schedule(self):
        for processor in self.processors_info:
            if not processor.is_available():
                processor.execute()
        
    def assign_process(self):
        for processor in self.processors_info:
            if processor.is_available():
                if self.ready_queue:
                    process = self.ready_queue.pop() #FIFO 방식으로 프로세스 할당
                    processor.assign_process(process,self.current_time)
                    break
                    
    def ready_queue_update(self):
        for process in self.processes:
            if process.arrival <= self.current_time and not process.is_running() and process not in self.ready_queue and process.remaining_time > 0:
                # 프로세스가 도착했지만 실행 중이지 않은 경우
                self.ready_queue.appendleft(process)
 