class Process:
    def __init__(self, pid, arrival, burst):
        self.pid = pid                              # 프로세스 ID
        self.arrival = arrival                      # 도착 시간
        self.burst = burst                          # 실행 시간
        self.start_time = None                      # 시작 시간
        self.wait_time = 0                          # 대기 시간
        self.turnaround_time = None                 # 반환 시간
        self.normalized_turnaround_time = None      # 정규화된 실행 시간
        self.remaining_time = burst                 # 남은 실행 시간
        self.running = False                        # 실행 중인지 여부
        
        
    def is_completed(self) -> bool:
        return self.remaining_time == 0

    def is_running(self) -> bool:
        return self.running

    def start(self, current_time: int):
        """프로세스의 시작 시간 업데이트 및 실행 상태 설정"""
        self.running = True
        if self.start_time is None:
            self.start_time = current_time

    def run(self,working_speed: int) -> None:
        """프로세스 실행"""
        self.remaining_time -= working_speed
        if self.remaining_time < 0:
            self.remaining_time = 0
        
    def wait(self) -> None:
        """프로세스의 대기 상태설정(ready queue에 들어갈때)"""
        self.running = False
        
    def stop(self, current_time: int) -> None:
        """프로세스의 종료 상태 설정"""
        self.running = False
        self.remaining_time = 0
        self.turnaround_time = current_time - self.arrival
        self.normalized_turnaround_time = self.turnaround_time / self.burst
        
    def log_state(self) -> None:
        """프로세스의 현재 상태 출력 (디버깅용)"""
        print(f"Process {self.pid}: Arrival {self.arrival}, BT {self.burst}, Remaining {self.remaining_time}, ST {self.start_time}, WT {self.wait_time}, TT {self.turnaround_time}, NTT {self.normalized_turnaround_time}")
    