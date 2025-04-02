from core import Process

class Processor:
    def __init__(self, id: int, type: str):
        self.id = id                            # 프로세서 ID
        self.type = type                        # 'P' 또는 'E'
        self.current_process: Process = None    # 현재 실행 중인 프로세스
        self.used_power = 0.0                   # 사용한 전력량
        self.PowerOn = False                    # 프로세서가 켜져 있는지 여부
        
        if(self.type.upper() == 'P'):   # P코어일 경우
            self.start_power = 0.5      # 시동 전력
            self.working_power = 3.0    # 작업 전력
            
        else:                           # E코어일 경우       
            self.start_power = 0.1      # 시동 전력
            self.working_power = 1.0    # 작업 전력
        

    def is_available(self) -> bool:
        """프로세서가 현재 사용 가능한지 확인"""
        return self.current_process is None

    def is_p_core(self) -> bool:
        """P코어인지 확인"""
        return self.type.upper() == 'P'

    def assign_process(self, process,current_time):
        if self.PowerOn == False:                # 프로세서가 꺼져있을 경우
            self.PowerOn = True                  # 프로세서 켜기
            self.used_power += self.start_power  # 시동 전력 사용
        self.current_process = process
        self.current_process.assign(current_time)  # 프로세스의 시작 시간 업데이트

    def execute(self, current_time: int):
        """현재 실행 중인 프로세스를 진행"""
        if self.current_process:
            self.used_power += self.working_power                   # 작업 전력 사용
            self.current_process.remaining_time -= 1                # 프로세스의 남은 시간 감소
            if self.current_process.remaining_time <= 0:            # 프로세스가 종료된 경우
                self.current_process.set_end()                     # 프로세스 종료 상태 설정
                self.current_process = None                         # 현재 프로세서를 None으로 설정하여 사용 가능 상태로 변경 
    
    
    def drop_process(self):
        """현재 프로세스를 종료"""
        if self.current_process:
            self.current_process.set_wait() # 프로세스의 대기 상태 설정
            self.current_process = None
            
    
    def __repr__(self):
        return f"Processor(id={self.id}, type={self.type}, current_process={self.current_process})"