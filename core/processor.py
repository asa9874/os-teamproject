from core import Process

class Processor:
    def __init__(self, id: int, type: str, time_quantum: int = None):
        self.id = id                                # 프로세서 ID
        self.type = type                            # 'P' 또는 'E' 코어 구분
        self.current_process: Process = None        # 현재 실행 중인 프로세스
        self.used_power = 0.0                       # 누적 사용 전력량
        self.PowerOn = False                        # 프로세서 전원 상태
        self.process_queue = []                     # 디버깅용 프로세스 실행 로그
        self.time_quantum_original = time_quantum   # 초기 시간 쿼텀 (RR 스케줄링용)
        self.time_quantum = time_quantum            # 남은 시간 쿼텀 (RR 스케줄링용)
        
        
        # 프로세서의 전력 사용량 및 속도
        if self.type.upper() == 'P':                # P-코어
            self.start_power = 0.5                  
            self.working_power = 3.0                
            self.working_speed = 2.0                
        else:                                       # E-코어
            self.start_power = 0.1
            self.working_power = 1.0
            self.working_speed = 1.0



    def is_time_quantum_expired(self, current_time: int) -> bool:
        """시간 쿼텀 만료 여부 확인 (RR 전용)"""
        return self.time_quantum is not None and self.time_quantum <= 0

    def decrease_time_quantum(self) -> None:
        """시간 쿼텀 감소 (RR 전용)"""
        if self.time_quantum is not None:
            self.time_quantum -= 1

    def reset_time_quantum(self) -> None:
        """시간 쿼텀 초기화 (RR 전용)"""
        self.time_quantum = self.time_quantum_original


    def is_process_empty(self) -> bool:
        """할당된 프로세스가 없으면 True 반환"""
        return self.current_process is None

    def assign_process(self, process: Process, current_time: int) -> None:
        """
        프로세스를 현재 프로세서에 할당하고 실행 시작
        - 전원이 꺼져 있으면 시동 전력 추가
        - 시간 쿼텀 초기화(RR 전용)
        - 프로세스 상태 변경 
        """

        if not self.PowerOn:
            self.PowerOn = True
            self.used_power += self.start_power
        self.current_process = process
        self.reset_time_quantum()
        self.current_process.start(current_time)

    def preempt_process(self) -> Process:
        """
        현재 실행 중인 프로세스를 대기 상태로 전환
        - 현재 프로세스를 반환하고, 프로세서에서 제거
        """
        
        if self.current_process:
            process = self.current_process
            process.wait()
            self.current_process = None
            return process
        return None


    def execute(self, current_time: int) -> None:
        """
        프로세서를 한 사이클 실행한다.
        - 프로세스가 할당되어 있다면 실행 및 전력 증가
        - 시간 쿼텀 감소(RR 전용)
        - 소비 전력량 증가
        - 프로세스가 완료되면 종료 처리
        """

        if self.current_process:
            self.process_queue.append(self.current_process.pid) # 디버깅용 로그

            if self.time_quantum is not None:
                self.decrease_time_quantum()

            self.used_power += self.working_power
            self.current_process.run(self.working_speed)

            if self.current_process.is_completed():
                self.current_process.stop(current_time)
                self.current_process = None

        elif current_time != 0:
            self.process_queue.append(0) # 디버깅용 로그