from scheduler import BaseScheduler

class FCFSScheduler(BaseScheduler):
    def schedule(self):
        for processor in self.processors_info:
            if not processor.is_available():
                processor.execute()
        

    # FCFSScheduler는 단순하게 대기 큐의 가장앞에서 프로세스를 할당한다.
    def assign_process(self):
        for processor in self.processors_info:
            if processor.is_available():             #FCFS는 비선점이라 비어있지않으면 프로세스가 따로 할당되지 않는다.
                if self.ready_queue:
                    process = self.ready_queue.pop() #FIFO 방식으로 프로세스 할당
                    processor.assign_process(process,self.current_time)
                    break
                    

    # FCFSScheduler는 단순하게 도착한 프로세스를 대기 큐에 추가하기만 하면 된다.
    def ready_queue_update(self):
        self.enqueue_arrived_processes()
        