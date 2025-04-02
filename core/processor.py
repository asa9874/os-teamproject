class Processor:
    def __init__(self, id: int, type: str):
        self.id = id                 # 프로세서 ID
        self.type = type             # 'P' 또는 'E'
        self.current_process = None  # 현재 실행 중인 프로세스
        self.remaining_time = 0      # 현재 프로세스의 남은 실행 시간

    def is_available(self) -> bool:
        """프로세서가 현재 사용 가능한지 확인"""
        return self.current_process is None

    def is_p_core(self) -> bool:
        """P코어인지 확인"""
        return self.type.upper() == 'P'

    def assign_process(self, process):
        """프로세스를 프로세서에 할당"""
        if self.is_available():
            self.current_process = process
            self.remaining_time = process.remaining_time
        else:
            raise ValueError(f"Processor {self.id} is already running a process!")

    def execute(self):
        """현재 실행 중인 프로세스를 진행"""
        if self.current_process:
            self.current_process.remaining_time -= 1
            self.remaining_time -= 1

            # 실행이 끝나면 프로세서에서 해제
            if self.remaining_time == 0:
                self.current_process = None

    def __repr__(self):
        return f"Processor(id={self.id}, type={self.type}, current_process={self.current_process})"