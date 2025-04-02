from algorithm import BaseScheduler

class TestSceduler(BaseScheduler):
    def schedule(self):
        for processor in self.processors_info:
            if not processor.is_available():
                processor.execute(self.current_time)
        
    def assign_process(self):
        for processor in self.processors_info:
            if processor.is_available():
                for process in self.processes:
                    if process.start_time is None and process.arrival <= self.current_time:
                        processor.assign_process(process)
                        process.update_metrics(self.current_time)
                        break
 