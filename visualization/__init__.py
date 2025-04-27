import tkinter as tk
from tkinter import ttk  # Themed widgets for better appearance
from tkinter import messagebox
import time
import heapq
from enum import Enum, auto
from typing import List, Optional, Dict, Any
import math
import os # For console clearing during display updates (optional)

# --- 기존 시뮬레이터 로직 (Process, Enums, SchedulerSimulator) ---
# (이전 답변에서 제공된 Process, ProcessState, SchedulingAlgorithm, SchedulerSimulator 클래스 코드를 여기에 붙여넣으세요)
# --- 시작 ---
# 프로세스 상태 정의 (Enum 사용)
class ProcessState(Enum):
    PENDING = "Pending"
    READY = "Ready"
    RUNNING = "Running"
    COMPLETED = "Completed"

# 스케줄링 알고리즘 정의 (Enum 사용)
class SchedulingAlgorithm(Enum):
    FCFS = "FCFS"
    SJF = "SJF"  # Non-preemptive SJF
    PRIORITY = "Priority" # Non-preemptive Priority

# 프로세스 정보를 담는 클래스
class Process:
    def __init__(self, id: str, name: str, arrival_time: int, burst_time: int, priority: int):
        if burst_time <= 0:
            raise ValueError("Burst time must be positive.")
        if arrival_time < 0:
            raise ValueError("Arrival time cannot be negative.")

        self.id: str = id
        self.name: str = name
        self.arrival_time: int = arrival_time
        self.burst_time: int = burst_time
        self.priority: int = priority  # 숫자가 낮을수록 우선순위 높음
        self.remaining_time: int = burst_time
        self.state: ProcessState = ProcessState.PENDING
        self.start_time: Optional[int] = None
        self.completion_time: Optional[int] = None
        self.waiting_time: Optional[int] = None
        self.turnaround_time: Optional[int] = None

    def __repr__(self) -> str:
        # 객체를 쉽게 출력하기 위한 문자열 표현
        return (f"Process(id={self.id}, name='{self.name}', AT={self.arrival_time}, "
                f"BT={self.burst_time}, Prio={self.priority}, RT={self.remaining_time}, "
                f"State={self.state.value}, Start={self.start_time}, End={self.completion_time}, "
                f"WT={self.waiting_time}, TAT={self.turnaround_time})")

    def to_dict(self) -> Dict[str, Any]:
         # 테이블 출력을 위해 딕셔너리로 변환
        return {
            "ID": self.id,
            "Name": self.name,
            "AT": self.arrival_time,
            "BT": self.burst_time,
            "Prio": self.priority,
            "RT": self.remaining_time,
            "State": self.state.value,
            "Start": self.start_time if self.start_time is not None else '-',
            "End": self.completion_time if self.completion_time is not None else '-',
            "WT": self.waiting_time if self.waiting_time is not None else '-',
            "TAT": self.turnaround_time if self.turnaround_time is not None else '-',
        }

# 스케줄링 시뮬레이터 클래스
class SchedulerSimulator:
    def __init__(self):
        self.processes: List[Process] = []
        self.current_time: int = 0
        self.running_process: Optional[Process] = None
        self.selected_algorithm: SchedulingAlgorithm = SchedulingAlgorithm.FCFS
        self.simulation_log: List[str] = []
        self.next_process_id_counter: int = 1
        # GUI에서 시뮬레이션 상태를 제어하므로 _is_running 플래그 제거 또는 다르게 활용 가능

    def _add_to_log(self, message: str):
        # 시간 형식을 조금 더 명확하게
        log_entry = f"[T={self.current_time:03d}] {message}"
        self.simulation_log.insert(0, log_entry)
        if len(self.simulation_log) > 100: # 로그 최대 100개 유지 (GUI에선 더 많이 표시 가능)
            self.simulation_log.pop()
        # GUI 업데이트를 위한 콜백이나 플래그를 여기에 추가할 수 있지만,
        # GUI가 주기적으로 simulator 상태를 폴링하는 방식으로 구현

    def add_process(self, name: str, arrival_time: int, burst_time: int, priority: int) -> Optional[str]:
        """프로세스 추가, 성공 시 None, 실패 시 에러 메시지 반환"""
        try:
            # 입력값 유효성 검사 강화
            if arrival_time < 0:
                 raise ValueError("Arrival time cannot be negative.")
            if burst_time <= 0:
                 raise ValueError("Burst time must be positive.")
            if priority < 0:
                 raise ValueError("Priority cannot be negative.")

            process_id = f"P{self.next_process_id_counter}"
            process_name = name if name else f"Process {self.next_process_id_counter}"
            new_process = Process(process_id, process_name, arrival_time, burst_time, priority)

            self.processes.append(new_process)
            self.processes.sort(key=lambda p: p.arrival_time)
            self.next_process_id_counter += 1
            self._add_to_log(f"Process {new_process.name} added (AT={arrival_time}, BT={burst_time}, Prio={priority}).")
            print(f"Process {new_process.name} added successfully.") # 콘솔 로그 (선택적)
            return None # 성공
        except ValueError as e:
            print(f"Error adding process: {e}") # 콘솔 로그 (선택적)
            return str(e) # 실패 메시지 반환

    def set_algorithm(self, algorithm: SchedulingAlgorithm):
        if self.selected_algorithm != algorithm:
            self.selected_algorithm = algorithm
            print(f"Algorithm set to {algorithm.value}") # 콘솔 로그 (선택적)
            self._add_to_log(f"Scheduling algorithm changed to {algorithm.value}.")

    def reset(self):
        self.processes = []
        self.current_time = 0
        self.running_process = None
        self.simulation_log = ["Simulation reset."]
        self.next_process_id_counter = 1
        # GUI 쪽에서 is_simulating 플래그도 리셋해야 함
        print("Simulation reset.") # 콘솔 로그 (선택적)

    def _get_ready_queue(self) -> List[Process]:
        """현재 시간에 준비 상태인 프로세스 목록 반환 (선택된 알고리즘 기준으로 정렬)"""
        ready_processes = [p for p in self.processes if p.state == ProcessState.READY]

        if self.selected_algorithm == SchedulingAlgorithm.FCFS:
            ready_processes.sort(key=lambda p: p.arrival_time)
        elif self.selected_algorithm == SchedulingAlgorithm.SJF:
            ready_processes.sort(key=lambda p: (p.burst_time, p.arrival_time))
        elif self.selected_algorithm == SchedulingAlgorithm.PRIORITY:
            ready_processes.sort(key=lambda p: (p.priority, p.arrival_time))

        return ready_processes

    def tick(self) -> bool:
        """
        시뮬레이션의 한 단계를 진행.
        더 이상 진행할 프로세스가 없으면 False 반환.
        """
        # 모든 프로세스가 완료되었는지 확인 (시작 시 또는 중간 확인)
        non_completed_processes = [p for p in self.processes if p.state != ProcessState.COMPLETED]
        if not non_completed_processes and self.processes:
            # 더 이상 진행할 프로세스 없음
            # 마지막 로그는 GUI 또는 run 메소드에서 처리하는 것이 나을 수 있음
            return False

        # 현재 시간 먼저 증가 (React 코드 로직과 유사하게 시간 증가 후 처리)
        current_tick_time = self.current_time # 이번 틱 시작 시간
        self.current_time += 1 # 다음 틱을 위한 시간 증가

        # 1. 실행 중인 프로세스 처리
        process_completed_this_tick = False
        if self.running_process:
            self.running_process.remaining_time -= 1
            # self._add_to_log(f"Process {self.running_process.name} running. RT={self.running_process.remaining_time}") # 너무 많은 로그 생성 가능

            if self.running_process.remaining_time <= 0:
                # 프로세스 완료 처리
                completed_process = self.running_process
                completed_process.state = ProcessState.COMPLETED
                completed_process.completion_time = self.current_time # 현재 tick이 끝나는 시점
                completed_process.turnaround_time = completed_process.completion_time - completed_process.arrival_time
                # 대기시간 계산 시 주의: 시작시간이 None일 경우 처리 필요
                if completed_process.start_time is not None:
                    completed_process.waiting_time = completed_process.turnaround_time - completed_process.burst_time
                else:
                     # 도착하자마자 실행되어 완료된 극단적 경우 등
                     completed_process.waiting_time = 0 # 또는 에러처리

                self._add_to_log(f"Process {completed_process.name} completed at T={self.current_time}. "
                                 f"WT={completed_process.waiting_time}, TAT={completed_process.turnaround_time}")
                self.running_process = None # CPU 유휴 상태로 변경
                process_completed_this_tick = True

        # 2. 새로 도착한 프로세스를 Ready 상태로 변경
        # 도착 시간 <= 현재 시간 (이번 tick 시작 시간 기준)
        for p in self.processes:
            if p.state == ProcessState.PENDING and p.arrival_time <= current_tick_time:
                 # 주의: React 코드는 <= newCurrentTime (증가된 시간) 이었음.
                 # 도착하자마자 Ready 상태가 되도록 하려면 arrival_time <= self.current_time 사용 가능
                 # 여기서는 tick 시작 시간 기준으로 도착 처리 (더 일반적)
                p.state = ProcessState.READY
                self._add_to_log(f"Process {p.name} arrived at T={p.arrival_time} and became Ready at T={current_tick_time}.")

        # 3. CPU가 유휴 상태이고 Ready Queue에 프로세스가 있는 경우, 다음 프로세스 선택
        # (이번 tick에서 프로세스가 완료되었거나, 원래 유휴 상태였을 경우)
        if not self.running_process:
            ready_queue = self._get_ready_queue()
            if ready_queue:
                next_process = ready_queue[0] # 정렬된 목록의 첫 번째 프로세스
                self.running_process = next_process
                self.running_process.state = ProcessState.RUNNING
                if self.running_process.start_time is None: # 처음 실행되는 경우 시작 시간 기록
                    self.running_process.start_time = current_tick_time # 이번 tick 시작 시 실행됨
                self._add_to_log(f"Process {self.running_process.name} selected to run at T={current_tick_time} (Algorithm: {self.selected_algorithm.value}).")
                # 방금 선택된 프로세스가 이번 tick에 바로 1만큼 실행됨 (위의 실행 로직에서 처리됨)
            # else: # 실행할 프로세스가 없음 (CPU Idle)
            #     # 유휴 로그는 GUI에서 running_process가 None일 때 표시하는 것으로 대체 가능
            #     if any(p.state != ProcessState.COMPLETED for p in self.processes):
            #          self._add_to_log("CPU Idle. Waiting for processes or next arrival.")

        # 계속 진행해야 하는지 여부 반환 (완료되지 않은 프로세스가 하나라도 있는가?)
        return any(p.state != ProcessState.COMPLETED for p in self.processes)


    def calculate_metrics(self) -> Dict[str, float]:
        """완료된 프로세스들의 평균 대기 시간 및 평균 반환 시간 계산"""
        completed = [p for p in self.processes if p.state == ProcessState.COMPLETED and p.waiting_time is not None and p.turnaround_time is not None]
        if not completed:
            return {"avg_waiting_time": 0.0, "avg_turnaround_time": 0.0}

        total_waiting_time = sum(p.waiting_time for p in completed)
        total_turnaround_time = sum(p.turnaround_time for p in completed)
        count = len(completed)

        return {
            "avg_waiting_time": total_waiting_time / count if count > 0 else 0.0,
            "avg_turnaround_time": total_turnaround_time / count if count > 0 else 0.0,
        }
# --- 시뮬레이터 로직 끝 ---


# --- Tkinter GUI Application ---
class SchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Process Scheduler Simulator")
        # self.root.geometry("1000x750") # 창 크기 조절

        # 스타일 설정
        self.style = ttk.Style()
        # 사용 가능한 테마 확인: print(self.style.theme_names())
        # ('clam', 'alt', 'default', 'classic') 등
        # 'clam' 이나 시스템 기본 테마 사용 추천
        try:
            # Windows: 'vista', 'xpnative' / Linux: 'clam' / MacOS: 'aqua'
             if os.name == 'nt':
                 self.style.theme_use('vista') # 또는 'xpnative'
             else:
                 self.style.theme_use('clam') # Linux/Mac 기본값 시도
        except tk.TclError:
            print("Default theme will be used.")
            self.style.theme_use('default') # Fallback

        # 시뮬레이터 인스턴스 생성
        self.simulator = SchedulerSimulator()

        # 시뮬레이션 상태 변수
        self.is_simulating = False
        self.simulation_speed_ms = 1000  # 1초 간격
        self.after_id = None # tk.after job ID

        # --- GUI 위젯 생성 ---
        self._create_widgets()
        self._setup_styles() # 스타일 적용 (Treeview 태그 등)

        # 초기 상태 표시
        self._update_display()

        # 예시 프로세스 추가 (CLI 버전과 동일)
        self.simulator.add_process(name="P1", arrival_time=0, burst_time=5, priority=2)
        self.simulator.add_process(name="P2", arrival_time=1, burst_time=3, priority=1)
        self.simulator.add_process(name="P3", arrival_time=2, burst_time=8, priority=3)
        self.simulator.add_process(name="P4", arrival_time=3, burst_time=6, priority=0)
        self._update_process_table() # 추가된 프로세스를 테이블에 표시
        self._update_log_display()   # 추가 로그 표시


    def _create_widgets(self):
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- 1. 입력 및 제어 프레임 ---
        input_controls_frame = ttk.LabelFrame(main_frame, text="Controls & Process Input", padding="10")
        input_controls_frame.pack(fill=tk.X, pady=(0, 10))
        input_controls_frame.columnconfigure(4, weight=1) # 버튼 영역 오른쪽 정렬 위해

        # 프로세스 입력 필드
        ttk.Label(input_controls_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.name_entry = ttk.Entry(input_controls_frame, width=10)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_controls_frame, text="Arrival Time:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.arrival_entry = ttk.Entry(input_controls_frame, width=5)
        self.arrival_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(input_controls_frame, text="Burst Time:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.burst_entry = ttk.Entry(input_controls_frame, width=5)
        self.burst_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(input_controls_frame, text="Priority:").grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        self.priority_entry = ttk.Entry(input_controls_frame, width=5)
        self.priority_entry.grid(row=1, column=3, padx=5, pady=5)
        self.priority_entry.insert(0, "0") # 기본값

        self.add_button = ttk.Button(input_controls_frame, text="Add Process", command=self._add_process_gui)
        self.add_button.grid(row=0, column=4, rowspan=2, padx=10, pady=5, sticky=tk.E + tk.W + tk.N + tk.S)

        # 구분선
        ttk.Separator(input_controls_frame, orient=tk.HORIZONTAL).grid(row=2, column=0, columnspan=5, sticky=tk.EW, pady=10)

        # 알고리즘 선택 및 제어 버튼
        ttk.Label(input_controls_frame, text="Algorithm:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.algorithm_var = tk.StringVar(value=SchedulingAlgorithm.FCFS.value)
        self.algorithm_combo = ttk.Combobox(input_controls_frame, textvariable=self.algorithm_var,
                                            values=[algo.value for algo in SchedulingAlgorithm], state='readonly', width=15)
        self.algorithm_combo.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W)
        self.algorithm_combo.bind("<<ComboboxSelected>>", self._on_algorithm_select)

        # 제어 버튼 프레임 (오른쪽 정렬용)
        button_frame = ttk.Frame(input_controls_frame)
        button_frame.grid(row=3, column=3, columnspan=2, padx=5, pady=5, sticky=tk.E)

        self.start_button = ttk.Button(button_frame, text="Start", command=self._start_simulation, width=8)
        self.start_button.pack(side=tk.LEFT, padx=2)

        self.pause_button = ttk.Button(button_frame, text="Pause", command=self._pause_simulation, state=tk.DISABLED, width=8)
        self.pause_button.pack(side=tk.LEFT, padx=2)

        self.reset_button = ttk.Button(button_frame, text="Reset", command=self._reset_simulation, width=8)
        self.reset_button.pack(side=tk.LEFT, padx=2)

        # --- 2. 상태 표시 프레임 ---
        status_frame = ttk.LabelFrame(main_frame, text="Simulation Status", padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        status_frame.columnconfigure(0, weight=1)
        status_frame.columnconfigure(1, weight=2)
        status_frame.columnconfigure(2, weight=2)

        # 현재 시간
        ttk.Label(status_frame, text="Current Time:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.time_var = tk.StringVar(value="0")
        ttk.Label(status_frame, textvariable=self.time_var, font=('Segoe UI', 16, 'bold')).grid(row=1, column=0, sticky=tk.W, padx=5, pady=(0,5))

        # 실행 중인 프로세스
        ttk.Label(status_frame, text="Running Process:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=1, sticky=tk.W, padx=5)
        self.running_process_var = tk.StringVar(value="CPU Idle")
        self.running_process_label = ttk.Label(status_frame, textvariable=self.running_process_var, wraplength=200) # wraplength 추가
        self.running_process_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=(0,5))

        # 준비 큐
        ttk.Label(status_frame, text="Ready Queue:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=2, sticky=tk.W, padx=5)
        self.ready_queue_listbox = tk.Listbox(status_frame, height=3, width=40, borderwidth=1, relief=tk.SUNKEN)
        self.ready_queue_listbox.grid(row=1, column=2, sticky=tk.NSEW, padx=5, pady=(0,5))
        ready_scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.ready_queue_listbox.yview)
        ready_scrollbar.grid(row=1, column=3, sticky=tk.NS, pady=(0,5))
        self.ready_queue_listbox.config(yscrollcommand=ready_scrollbar.set)

        # --- 3. 전체 프로세스 테이블 ---
        table_frame = ttk.LabelFrame(main_frame, text="All Processes", padding="10")
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        columns = ("ID", "Name", "AT", "BT", "Prio", "RT", "State", "Start", "End", "WT", "TAT")
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)

        # 컬럼 설정
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=60 if col not in ["Name", "State", "ID"] else (100 if col == "Name" else (80 if col == "State" else 40)) , anchor=tk.CENTER if col not in ["Name", "State"] else tk.W) # 너비와 정렬 조정

        # 스크롤바
        tree_scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        tree_scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=tree_scrollbar_y.set, xscrollcommand=tree_scrollbar_x.set)

        tree_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # --- 4. 메트릭 및 로그 프레임 ---
        metrics_log_frame = ttk.Frame(main_frame)
        metrics_log_frame.pack(fill=tk.X)
        metrics_log_frame.columnconfigure(0, weight=1)
        metrics_log_frame.columnconfigure(1, weight=1)

        # 메트릭
        metrics_frame = ttk.LabelFrame(metrics_log_frame, text="Performance Metrics", padding="10")
        metrics_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 5))
        metrics_frame.columnconfigure(1, weight=1)

        ttk.Label(metrics_frame, text="Avg. Waiting Time:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.avg_wt_var = tk.StringVar(value="0.00")
        ttk.Label(metrics_frame, textvariable=self.avg_wt_var, font=('Segoe UI', 12, 'bold')).grid(row=0, column=1, sticky=tk.W, padx=5)

        ttk.Label(metrics_frame, text="Avg. Turnaround Time:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.avg_tat_var = tk.StringVar(value="0.00")
        ttk.Label(metrics_frame, textvariable=self.avg_tat_var, font=('Segoe UI', 12, 'bold')).grid(row=1, column=1, sticky=tk.W, padx=5)

        # 시뮬레이션 로그
        log_frame = ttk.LabelFrame(metrics_log_frame, text="Simulation Log", padding="10")
        log_frame.grid(row=0, column=1, sticky=tk.NSEW, padx=(5, 0))
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)

        self.log_text = tk.Text(log_frame, height=6, width=60, wrap=tk.WORD, state=tk.DISABLED, borderwidth=1, relief=tk.SUNKEN)
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.config(yscrollcommand=log_scrollbar.set)

        self.log_text.grid(row=0, column=0, sticky=tk.NSEW)
        log_scrollbar.grid(row=0, column=1, sticky=tk.NS)

    def _setup_styles(self):
        """Treeview 행 색상 등 스타일 설정"""
        self.style.map("Treeview", background=[('selected', '#0078D7')], foreground=[('selected', 'white')])

        # 상태별 색상 태그 정의 (React 코드의 색상과 유사하게)
        # Treeview는 배경색 변경이 테마에 따라 잘 안될 수 있음. foreground 시도.
        # 색상 코드는 예시이며, 더 적절한 색으로 변경 가능
        self.tree.tag_configure(ProcessState.PENDING.value, foreground='grey')
        self.tree.tag_configure(ProcessState.READY.value, foreground='orange')
        self.tree.tag_configure(ProcessState.RUNNING.value, foreground='green', font=('Segoe UI', 9, 'bold'))
        self.tree.tag_configure(ProcessState.COMPLETED.value, foreground='blue') # 또는 연한 회색: 'dark slate gray'

    # --- GUI 액션 핸들러 ---
    def _add_process_gui(self):
        try:
            name = self.name_entry.get()
            # 입력값 검증 강화
            at_str = self.arrival_entry.get()
            bt_str = self.burst_entry.get()
            prio_str = self.priority_entry.get()

            if not at_str or not bt_str or not prio_str:
                raise ValueError("Arrival, Burst, and Priority times cannot be empty.")

            at = int(at_str)
            bt = int(bt_str)
            prio = int(prio_str)

            error_message = self.simulator.add_process(name, at, bt, prio)

            if error_message:
                 messagebox.showerror("Input Error", error_message)
            else:
                # 성공 시 입력 필드 초기화
                self.name_entry.delete(0, tk.END)
                self.arrival_entry.delete(0, tk.END)
                self.burst_entry.delete(0, tk.END)
                self.priority_entry.delete(0, tk.END)
                self.priority_entry.insert(0, "0") # 우선순위 기본값 복원
                self._update_process_table()
                self._update_log_display()
                self._update_button_states() # 프로세스 추가 후 시작 버튼 활성화
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {e}\nPlease enter valid non-negative integers for times/priority (Burst > 0).")
        except Exception as e:
             messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def _on_algorithm_select(self, event=None):
        selected_algo_str = self.algorithm_var.get()
        try:
            algorithm = SchedulingAlgorithm(selected_algo_str) # 값으로 Enum 멤버 찾기
            self.simulator.set_algorithm(algorithm)
            self._update_ready_queue_display() # 알고리즘 변경 시 준비 큐 정렬 순서 변경 반영
            self._update_log_display()
        except ValueError:
             print(f"Error: Unknown algorithm selected: {selected_algo_str}") # Debug

    def _start_simulation(self):
        if not self.simulator.processes:
            messagebox.showinfo("No Processes", "Please add processes before starting.")
            return
        if all(p.state == ProcessState.COMPLETED for p in self.simulator.processes):
             messagebox.showinfo("Simulation Finished", "All processes are already completed. Reset to run again.")
             return

        self.is_simulating = True
        self._update_button_states()
        self._simulation_step() # 첫 스텝 시작

    def _pause_simulation(self):
        self.is_simulating = False
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self._update_button_states()
        self.simulator._add_to_log("Simulation paused.")
        self._update_log_display()

    def _reset_simulation(self):
        self.is_simulating = False
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        self.simulator.reset()
        self._update_display() # 모든 표시 초기화
        self._update_button_states()

        # 선택: 리셋 시 예시 프로세스 다시 로드?
        # self.simulator.add_process(...)
        # self._update_process_table()
        # self._update_log_display()

    # --- 시뮬레이션 진행 및 GUI 업데이트 ---
    def _simulation_step(self):
        if not self.is_simulating:
            return # 중지됨

        should_continue = self.simulator.tick()
        self._update_display()

        if should_continue:
            # 다음 스텝 예약
            self.after_id = self.root.after(self.simulation_speed_ms, self._simulation_step)
        else:
            # 시뮬레이션 종료 처리
            self.is_simulating = False
            if self.simulator.processes: # 프로세스가 있었을 경우에만 완료 메시지
                 self.simulator._add_to_log("All processes completed. Simulation finished.")
                 self._update_log_display() # 마지막 로그 표시
                 messagebox.showinfo("Simulation Finished", "All processes have completed.")
            self._update_button_states() # 종료 후 버튼 상태 업데이트

    def _update_display(self):
        """GUI의 모든 동적 요소 업데이트"""
        # 시간 업데이트
        self.time_var.set(str(self.simulator.current_time))

        # 실행 중 프로세스 업데이트
        if self.simulator.running_process:
            rp = self.simulator.running_process
            self.running_process_var.set(f"{rp.name} (ID: {rp.id}), RT: {rp.remaining_time}")
            # 실행 중 상태 강조 (예: 라벨 배경색 변경 - 테마에 따라 작동 안 할 수 있음)
            self.running_process_label.config(foreground="green", font=('Segoe UI', 9, 'bold'))
        else:
            self.running_process_var.set("CPU Idle")
            self.running_process_label.config(foreground="grey", font=('Segoe UI', 9, 'normal'))

        # 준비 큐 업데이트
        self._update_ready_queue_display()

        # 프로세스 테이블 업데이트
        self._update_process_table()

        # 메트릭 업데이트
        metrics = self.simulator.calculate_metrics()
        self.avg_wt_var.set(f"{metrics['avg_waiting_time']:.2f}")
        self.avg_tat_var.set(f"{metrics['avg_turnaround_time']:.2f}")

        # 로그 업데이트
        self._update_log_display()


    def _update_ready_queue_display(self):
        self.ready_queue_listbox.delete(0, tk.END)
        ready_queue = self.simulator._get_ready_queue()
        for p in ready_queue:
            self.ready_queue_listbox.insert(tk.END, f"{p.name} (AT:{p.arrival_time}, BT:{p.burst_time}, Prio:{p.priority})")

    def _update_process_table(self):
        # 기존 항목 삭제
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 새 데이터 삽입 및 태그 적용
        for p in self.simulator.processes:
            p_dict = p.to_dict()
            # Treeview 컬럼 순서에 맞게 값 리스트 생성
            values = [p_dict[col] for col in self.tree['columns']]
            # 상태에 따라 태그 적용
            self.tree.insert('', tk.END, iid=p.id, values=values, tags=(p.state.value,))

    def _update_log_display(self):
        self.log_text.config(state=tk.NORMAL) # 편집 가능 상태로 변경
        self.log_text.delete('1.0', tk.END) # 기존 내용 삭제
        # 로그가 너무 많으면 성능 저하 가능 -> 최근 N개만 표시 고려
        log_limit = 100 # 표시할 최대 로그 수
        start_index = max(0, len(self.simulator.simulation_log) - log_limit)
        for entry in self.simulator.simulation_log[start_index:]: # 최신 로그가 위로 오므로 역순 불필요
            self.log_text.insert('1.0', entry + "\n") # 새 로그를 맨 위에 삽입
        self.log_text.config(state=tk.DISABLED) # 다시 읽기 전용으로
        # self.log_text.see(tk.END) # 스크롤을 맨 아래로 (맨 위에 삽입했으므로 불필요)


    def _update_button_states(self):
        """시뮬레이션 상태에 따라 버튼 활성화/비활성화"""
        has_processes = bool(self.simulator.processes)
        all_completed = all(p.state == ProcessState.COMPLETED for p in self.simulator.processes) if has_processes else True

        if self.is_simulating:
            self.start_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)
            self.reset_button.config(state=tk.DISABLED)
            self.add_button.config(state=tk.DISABLED) # 시뮬레이션 중 추가 금지
            self.algorithm_combo.config(state=tk.DISABLED) # 시뮬레이션 중 변경 금지
        else:
            # 시작 가능 조건: 프로세스가 있고, 아직 완료되지 않은 프로세스가 있는 경우
            can_start = has_processes and not all_completed
            self.start_button.config(state=tk.NORMAL if can_start else tk.DISABLED)
            self.pause_button.config(state=tk.DISABLED)
            self.reset_button.config(state=tk.NORMAL)
            self.add_button.config(state=tk.NORMAL)
            self.algorithm_combo.config(state='readonly') # 선택 가능

# --- 애플리케이션 실행 ---
if __name__ == "__main__":
    root = tk.Tk()
    app = SchedulerApp(root)
    root.mainloop()