class Process:
    def __init__(self, pid, arrival, burst):
        self.pid = pid # 프로세스 ID
        self.arrival = arrival # 도착 시간
        self.burst = burst # 실행 시간
        self.start_time = None # 시작 시간
        self.wait_time = 0 # 대기 시간
        self.turnaround_time = None # 반환 시간
        self.normalized_burst_time = None # 정규화된 실행 시간 (우선순위 계산에 사용)
        self.remaining_time = burst # 남은 실행 시간
        self.running = False # 실행 중인지 여부
        
        
    def is_completed(self) -> bool:
        return self.remaining_time == 0

    def is_running(self) -> bool:
        return self.running

    def assign(self, current_time: int):
        """프로세스의 시작 시간 업데이트 및 실행 상태 설정"""
        self.running = True
        if self.start_time is None:
            self.start_time = current_time
        
    def set_wait(self) -> None:
        """프로세스의 대기 상태설정"""
        self.running = False
        
    def set_end(self) -> None:
        """프로세스의 종료 상태 설정"""
        self.running = False
        self.turnaround_time = self.start_time + self.burst - self.arrival
        self.normalized_burst_time = self.turnaround_time / self.burst
        
    def log_state(self) -> None:
        """프로세스의 현재 상태 출력 (디버깅용)"""
        print(f"Process {self.pid}: Arrival {self.arrival}, BT {self.burst}, Remaining {self.remaining_time}, ST {self.start_time}, WT {self.wait_time}, TT {self.turnaround_time}, NTT {self.normalized_burst_time}")
    
    def __repr__(self):
        return f"Process(pid={self.pid}, arrival={self.arrival}, burst={self.burst})"