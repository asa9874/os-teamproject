class Process:
    def __init__(self, pid, arrival, burst):
        self.pid = pid # 프로세스 ID
        self.arrival = arrival # 도착 시간
        self.burst = burst # 실행 시간
        self.start_time = None # 시작 시간
        self.wait_time = None # 대기 시간
        self.turnaround_time = None # 반환 시간
        
    def is_completed(self) -> bool:
        return self.remaining_time == 0

    def is_running(self) -> bool:
        return self.start_time is not None and self.remaining_time > 0

    def update_metrics(self, current_time: int):
        """프로세스의 시작 시간, 대기 시간, 반환 시간 업데이트"""
        if self.start_time is None:
            self.start_time = current_time
        self.wait_time = self.start_time - self.arrival
        self.turnaround_time = current_time - self.arrival + 1

    def __repr__(self):
        return f"Process(pid={self.pid}, arrival={self.arrival}, burst={self.burst})"