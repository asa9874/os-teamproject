from typing import List
from core.process import Process
from core.processor import Processor
from scheduler import (
    BaseScheduler,
    FCFSScheduler,
    RRScheduler,
    SPNScheduler,
    HRRNScheduler,
    SRTNScheduler,
    CustomScheduler,
    SchedulerType,
)

class SchedulerApp:
    def __init__(self, scheduler_type: SchedulerType = SchedulerType.FCFS) -> None:
        self.processes: List[Process] = []
        self.processors: List[Processor] = []
        self.scheduler_type: SchedulerType = scheduler_type
        self.scheduler: BaseScheduler = None
        
        self.scheduler_map = {
            SchedulerType.FCFS: FCFSScheduler,
            SchedulerType.RR: RRScheduler,
            SchedulerType.SPN: SPNScheduler,
            SchedulerType.HRRN: HRRNScheduler,
            SchedulerType.SRTN: SRTNScheduler,
            SchedulerType.CUSTOM: CustomScheduler,
        }

    # 프로세스 관련 메서드
    def add_process(self, pid: int, arrival: int, burst: int) -> None:
        self.processes.append(Process(pid=pid, arrival=arrival, burst=burst))

    def add_processes(self, process_list: List[Process]) -> None:
        self.processes.extend(process_list)

    def remove_process(self, pid: int) -> None:
        self.processes = [p for p in self.processes if p.pid != pid]

    def reset_processes(self) -> None:
        self.processes.clear()

    # 프로세서 관련 메서드
    def add_processor(self, id: int, type: str, time_quantum: int = None) -> None: #time_quantum은 RR용으로만 사용됨
        self.processors.append(Processor(id=id, type=type, time_quantum=time_quantum))
    
    def add_processors(self, processor_list: List[Processor]) -> None:
        self.processors.extend(processor_list)

    def remove_processor(self, id: int) -> None:
        self.processors = [p for p in self.processors if p.id != id]

    def reset_processors(self) -> None:
        self.processors.clear()

    # 스케줄러 관련 메서드
    def select_scheduler(self) -> None:
        scheduler_class = self.scheduler_map.get(self.scheduler_type)
        if scheduler_class is None:
            raise ValueError(f"지원하지 않는 스케줄러 유형입니다: {self.scheduler_type}")
        self.scheduler = scheduler_class(self.processes, self.processors)

    # 시뮬레이션 관련 메서드
    def run_scheduler(self) -> None:
        self.scheduler.simulate()

    def print_results(self) -> None:
        print("끝")
        if self.scheduler:
            self.scheduler.log_process_queue()

    def run(self) -> None:
        self.select_scheduler()
        self.run_scheduler()
        self.print_results()
