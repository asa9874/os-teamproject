from scheduler import BaseScheduler

class FCFSScheduler(BaseScheduler):
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
        self.enqueue_arrived_processes()
        