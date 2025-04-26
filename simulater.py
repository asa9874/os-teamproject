from core.process import Process
from core.processor import Processor
from scheduler import FCFSSceduler

class SchedulerApp:
    def __init__(self):
        self.processes = []
        self.processors = []
        self.scheduler = None

    def setup_processes(self) -> None:
        self.processes = [
            Process(pid=1, arrival=0, burst=3),
            Process(pid=2, arrival=1, burst=7),
            Process(pid=3, arrival=3, burst=2),
            Process(pid=4, arrival=5, burst=5),
            Process(pid=5, arrival=6, burst=3),
        ]

    def setup_processors(self) -> None:
        self.processors = [
            Processor(id=1, type="E"),  # P 또는 E
        ]

    def run_scheduler(self) -> None:
        # 여기에 테스트할 스케줄러 클래스명을 바꾸기만 하면 됨
        self.scheduler = FCFSScheduler(self.processes, self.processors)
        self.scheduler.simulate()

    def print_results(self) -> None:
        print("끝")
        self.scheduler.log_process_queue()

    def run(self) -> None:
        self.setup_processes()
        self.setup_processors()
        self.run_scheduler()
        self.print_results()


if __name__ == '__main__':
    app = SchedulerApp()
    app.run()
