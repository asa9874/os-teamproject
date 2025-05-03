from core import Process

class Processor:
    def __init__(self, id: int, type: str, time_quantum: int = None):
        self.id = id                            # 프로세서 ID
        self.type = type                        # 'P' 또는 'E'
        self.current_process: Process = None    # 현재 실행 중인 프로세스
        self.used_power = 0.0                   # 사용한 전력량
        self.PowerOn = False                    # 프로세서가 켜져 있는지 여부
        self.process_queue = []                 # 프로세스 시간별큐(디버깅용)
        self.time_quantum_original = time_quantum  # 원래 시간 쿼텀 (RR 이외에는 매개변수 넣지마세요)
        self.time_quantum = time_quantum        # 프로세서의 시간 쿼텀 (RR 이외에는 매개변수 넣지마세요)
        
        if(self.type.upper() == 'P'):           # P코어일 경우
            self.start_power = 0.5              # 시동 전력 
            self.working_power = 3.0            # 작업 전력
            self.working_speed = 2.0            # 작업 속도
            
        else:                                   # E코어일 경우       
            self.start_power = 0.1              # 시동 전력
            self.working_power = 1.0            # 작업 전력
            self.working_speed = 1.0            # 작업 속도
        

    def is_time_quantum_expired(self, current_time: int) -> bool:
        """시간 쿼텀 만료 여부 확인 (RR용)"""
        return self.time_quantum is not None and self.time_quantum <= 0 # 시간 쿼텀이 만료된 경우
            
    def decrease_time_quantum(self) -> None:
        """시간 쿼텀 감소 (RR용)"""
        if self.time_quantum is not None:
            self.time_quantum -= 1
    
    def reset_time_quantum(self) -> None:
        """시간 쿼텀 초기화 (RR용)"""
        self.time_quantum = self.time_quantum_original



    def is_process_empty(self) -> bool:
        """프로세서에 할당된 프로세스가 없을 경우 True 반환"""
        return self.current_process is None
    
    def assign_process(self, process,current_time):
        """프로세서에 프로세스를 할당"""
        if self.PowerOn == False:                                       # 프로세서가 꺼져있을 경우
            self.PowerOn = True                                         # 프로세서 켜기
            self.used_power += self.start_power                         # 시동 전력 사용
        self.current_process = process                                  # 프로세스 할당
        self.reset_time_quantum()                                       # 시간 쿼텀 초기화 (RR용)
        self.current_process.start(current_time)                        # 프로세스 할당

    def execute(self, current_time: int) -> None:
        """현재 실행 중인 프로세스를 진행"""
        if self.current_process:
            self.process_queue.append(self.current_process.pid)         # 프로세스 ID를 큐에 추가 (디버깅용)
            if self.time_quantum is not None:                           # 시간 쿼텀이 설정된 경우(RR용)
                self.decrease_time_quantum()                            # 시간 쿼텀 감소(RR용)
            self.used_power += self.working_power                       # 작업 전력 사용
            self.current_process.run(self.working_speed)                # 프로세스의 남은 시간 감소
            if self.current_process.is_completed():                     # 프로세스가 종료된 경우
                self.current_process.stop(current_time)                             # 프로세스 종료 상태 설정
                self.current_process = None                             # 현재 프로세서를 None으로 설정하여 사용 가능 상태로 변경 
        elif current_time != 0: 
            self.process_queue.append(0)                                # 현재 프로세스가 없을 경우 '0' 추가 (디버깅용)
    
    
    def preempt_process(self):
        """현재 프로세스를 내려놓고 대기상태로"""
        if self.current_process:
            process = self.current_process
            self.current_process.wait() # 프로세스의 대기 상태 설정
            self.current_process = None

        return process
            

        
            
    