from core.process import Process
from core.processor import Processor
from algorithm import BaseScheduler  # BaseScheduler가 구현된 파일에서 import

class FCFSSceduler(BaseScheduler):
    def schedule(self):
        for processor in self.processors_info:
            if processor.is_available():
                for process in self.processes:
                    if process.start_time is None and process.arrival <= self.current_time:
                        processor.assign_process(process)
                        process.update_metrics(self.current_time)
                        print(f"Time {self.current_time}: Process {process.pid} assigned to Processor {processor.id}")
                        break
            else:
                processor.execute(self.current_time)
        self.current_time += 1  # 시간 증가
        super().log_state()
        
    def hasNext(self):
        return super().hasNext()
