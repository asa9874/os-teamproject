class Process:
    def __init__(self, pid, arrival, burst):
        self.pid = pid # 프로세스 ID
        self.arrival = arrival # 도착 시간
        self.burst = burst # 실행 시간
        self.start_time = None # 시작 시간
        self.wait_time = None # 대기 시간
        self.turnaround_time = None # 반환 시간
        


    def __repr__(self):
        return f"Process(pid={self.pid}, arrival={self.arrival}, burst={self.burst})"