from algorithm import BaseScheduler

class TestSceduler(BaseScheduler):
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
        self.current_time += 1
        
    def hasNext(self):
        return super().hasNext()

    def log_state(self):
        return super().log_state()