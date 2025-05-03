from scheduler import BaseScheduler

class FCFSScheduler(BaseScheduler):
    """
    대기 큐에서 먼저 도착한 순서대로 프로세스를 할당하는 스케줄러 (비선점)
    """
    def assign_process(self) -> None:
        for processor in self.processors_info:
            if processor.is_process_empty():  # 비어 있는 경우에만 할당
                if self.ready_queue:
                    process = self.ready_queue.pop()  # FIFO 방식 할당
                    processor.assign_process(process, self.current_time)
