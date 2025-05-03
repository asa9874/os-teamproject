import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import random

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from core.process import Process
from core.processor import Processor
from simulator import SchedulerApp, SchedulerType
from scheduler.base_scheduler import BaseScheduler

# 상수 정의
MAX_PROCESSES = 15
MAX_PROCESSORS = 4
"""
이전버전 GUI임 최종제출때는 제외할것
"""
class SchedulerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("프로세스 스케줄링 시뮬레이터")
        self.geometry("1250x650")

        # 데이터 저장용 변수
        self.app = SchedulerApp()
        self.process_data = []
        self.processor_data = []
        self.process_colors = {}

        # 시뮬레이션 상태 변수
        self.simulation_running = False
        self.simulation_paused = False
        self.current_after_id = None
        self.simulation_speed_ms = 100

        # GUI 스타일
        style = ttk.Style(self)
        style.theme_use('vista')

        # 간트 차트 관련 파라미터
        self.gantt_label_width = 70
        self.gantt_padding = 10
        self.gantt_header_height = 25
        self.gantt_row_height = 30
        self.gantt_time_scale = 25

        # 제어 프레임 (상단)
        self.control_frame = ttk.Frame(self, padding="5")
        self.control_frame.pack(side=tk.TOP, fill=tk.X)

        # 좌우 분할용
        self.main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.main_pane.pack(fill=tk.BOTH, expand=True)

        # 입력 프레임 (좌측) 1/4
        self.input_frame = ttk.Frame(self.main_pane, padding=5)
        self.main_pane.add(self.input_frame, weight=1) # 가중치 1

        # 출력 프레임 (우측) 3/4
        self.output_container_frame = ttk.Frame(self.main_pane, padding=5)
        self.main_pane.add(self.output_container_frame, weight=3) # 가중치 3

        # 위젯 생성
        self.setup_control_widgets()
        self.setup_input_widgets()
        self.setup_output_widgets()

        # 프로세스, 프로세서 목록 라벨 초기화
        self.update_list_counts()   


    # 제어 위젯
    def setup_control_widgets(self):
        # 알고리즘 선택
        ttk.Label(self.control_frame, text="Algorithm:").pack(side=tk.LEFT, padx=(0,2))
        scheduler_names = [s.name for s in SchedulerType]
        self.scheduler_var = tk.StringVar(value=scheduler_names[0])
        self.scheduler_combo = ttk.Combobox(self.control_frame, textvariable=self.scheduler_var, values=scheduler_names, state="readonly", width=8, height=10)
        self.scheduler_combo.pack(side=tk.LEFT, padx=(0,10))
        self.scheduler_combo.bind("<<ComboboxSelected>>", self.update_rr_quantum_visibility) # 콤보박스가 RR이면 퀀텀 활성화

        # RR용 타임 퀀텀
        self.rr_quantum_label = ttk.Label(self.control_frame, text="Time Quantum:")
        self.rr_quantum_entry = ttk.Entry(self.control_frame, width=4)

        # 시뮬레이션 제어용
        self.start_button = ttk.Button(self.control_frame, text="Start", command=self.start_simulation, width=7)
        self.start_button.pack(side=tk.LEFT, padx=(10, 2))
        self.pause_resume_button = ttk.Button(self.control_frame, text="Pause", state=tk.DISABLED, command=self.toggle_pause_simulation, width=7)
        self.pause_resume_button.pack(side=tk.LEFT, padx=2)
        self.step_button = ttk.Button(self.control_frame, text="Step", state=tk.DISABLED, command=self.step_simulation, width=5)
        self.step_button.pack(side=tk.LEFT, padx=2)
        self.reset_button = ttk.Button(self.control_frame, text="Reset", command=self.reset_all, width=6)
        self.reset_button.pack(side=tk.LEFT, padx=(10, 2))

        # 속도 조절
        self.speed_label_var = tk.StringVar(value=f"{self.simulation_speed_ms} ms")
        ttk.Label(self.control_frame, textvariable=self.speed_label_var, width=7).pack(side=tk.RIGHT, padx=(0,5))
        self.speed_scale = ttk.Scale(self.control_frame, from_=50, to=500, orient=tk.HORIZONTAL,
                                     command=self.update_speed, length=120)
        self.speed_scale.set(self.simulation_speed_ms)
        self.speed_scale.pack(side=tk.RIGHT, padx=2)
        ttk.Label(self.control_frame, text="Speed:").pack(side=tk.RIGHT, padx=0)

        # RR이면 퀀텀 활성화
        self.update_rr_quantum_visibility()

    # 입력 위젯
    def setup_input_widgets(self):
        input_content_frame = ttk.Frame(self.input_frame)
        input_content_frame.pack(fill=tk.BOTH, expand=True)

        # 프로세스 입력
        process_section_frame = ttk.Frame(input_content_frame, padding=(0,0,0,10))
        process_section_frame.pack(side=tk.TOP, fill=tk.X, expand=False)

        process_input_frame = ttk.LabelFrame(process_section_frame, text="Add Process")
        process_input_frame.pack(pady=5, fill=tk.X)
        ttk.Label(process_input_frame, text="Arrival:").grid(row=0, column=0, padx=5, pady=(5,2), sticky=tk.W)
        self.arrival_entry = ttk.Entry(process_input_frame, width=5)
        self.arrival_entry.grid(row=0, column=1, padx=5, pady=(5,2), sticky="ew")
        ttk.Label(process_input_frame, text="Burst:").grid(row=1, column=0, padx=5, pady=(2,5), sticky=tk.W)
        self.burst_entry = ttk.Entry(process_input_frame, width=5)
        self.burst_entry.grid(row=1, column=1, padx=5, pady=(2,5), sticky="ew")
        self.add_process_button = ttk.Button(process_input_frame, text="Add", width=6, command=self.add_process)
        self.add_process_button.grid(row=0, column=2, rowspan=2, padx=10, pady=5, sticky="ns")
        process_input_frame.columnconfigure(1, weight=1)

        # 프로세스 목록 (LabelFrame + Treeview)
        # LabelFrame 객체를 인스턴스 변수로 저장하여 나중에 텍스트 변경
        self.process_list_labelframe = ttk.LabelFrame(process_section_frame, text="Processes") # 초기 텍스트
        self.process_list_labelframe.pack(pady=5, fill=tk.X)
        self.process_tree = ttk.Treeview(self.process_list_labelframe, columns=("pid", "arrival", "burst"), show="headings", height=6)
        self.process_tree.heading("pid", text="PID")
        self.process_tree.column("pid", width=40, minwidth=30, anchor=tk.CENTER)
        self.process_tree.heading("arrival", text="Arrival")
        self.process_tree.column("arrival", width=50, minwidth=40, anchor=tk.CENTER)
        self.process_tree.heading("burst", text="Burst")
        self.process_tree.column("burst", width=50, minwidth=40, anchor=tk.CENTER)
        process_scrollbar = ttk.Scrollbar(self.process_list_labelframe, orient=tk.VERTICAL, command=self.process_tree.yview)
        self.process_tree.configure(yscrollcommand=process_scrollbar.set)
        process_scrollbar.pack(side=tk.RIGHT, fill=tk.Y) # 스크롤바 먼저 배치
        self.process_tree.pack(side=tk.LEFT, fill=tk.X, expand=True) # Treeview가 남은 공간 채움
        self.remove_process_button = ttk.Button(process_section_frame, text="Remove Selected Process", command=self.remove_process)
        self.remove_process_button.pack(pady=(0,5)) # 버튼 아래 여백

        # 프로세서 입력
        processor_section_frame = ttk.Frame(input_content_frame)
        processor_section_frame.pack(side=tk.TOP, fill=tk.X, expand=False) # 세로 확장 안 함

        processor_input_frame = ttk.LabelFrame(processor_section_frame, text="Add Processor")
        processor_input_frame.pack(pady=5, fill=tk.X)
        ttk.Label(processor_input_frame, text="Type:").grid(row=0, column=0, padx=5, pady=(5,2), sticky=tk.W)
        self.proc_type_var = tk.StringVar(value='P') # P-Core 기본 선택
        proc_type_p = ttk.Radiobutton(processor_input_frame, text="P-Core", variable=self.proc_type_var, value='P')
        proc_type_e = ttk.Radiobutton(processor_input_frame, text="E-Core", variable=self.proc_type_var, value='E')
        proc_type_p.grid(row=0, column=1, padx=5, pady=(5,2), sticky=tk.W)
        proc_type_e.grid(row=1, column=1, padx=5, pady=(2,5), sticky=tk.W)
        self.add_processor_button = ttk.Button(processor_input_frame, text="Add", width=6, command=self.add_processor)
        self.add_processor_button.grid(row=0, column=2, rowspan=2, padx=10, pady=5, sticky="ns")
        processor_input_frame.columnconfigure(1, weight=1) # 라디오 버튼 공간 확보

        # 프로세서 목록 (LabelFrame + Treeview)
        # LabelFrame 객체를 인스턴스 변수로 저장
        self.processor_list_labelframe = ttk.LabelFrame(processor_section_frame, text="Processors") # 초기 텍스트
        self.processor_list_labelframe.pack(pady=5, fill=tk.X)
        self.processor_tree = ttk.Treeview(self.processor_list_labelframe, columns=("id", "type"), show="headings", height=4) # Quantum 컬럼 없음
        self.processor_tree.heading("id", text="ID")
        self.processor_tree.column("id", width=50, minwidth=40, anchor=tk.CENTER)
        self.processor_tree.heading("type", text="Type")
        self.processor_tree.column("type", width=70, minwidth=50, anchor=tk.CENTER)
        processor_scrollbar = ttk.Scrollbar(self.processor_list_labelframe, orient=tk.VERTICAL, command=self.processor_tree.yview)
        self.processor_tree.configure(yscrollcommand=processor_scrollbar.set)
        processor_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.processor_tree.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.remove_processor_button = ttk.Button(processor_section_frame, text="Remove Selected Processor", command=self.remove_processor)
        self.remove_processor_button.pack(pady=(0,5))

    # 출력 위젯
    def setup_output_widgets(self):
        # 간트 차트
        gantt_frame = ttk.LabelFrame(self.output_container_frame, text="Gantt Chart", padding=5)
        gantt_frame.pack(side=tk.TOP, fill=tk.X, expand=False, pady=(0,5)) # 세로 확장 X
        self.gantt_canvas = tk.Canvas(gantt_frame, bg='white', height=100, highlightthickness=0) # 초기 높이, 동적 조절됨
        gantt_hbar = ttk.Scrollbar(gantt_frame, orient=tk.HORIZONTAL, command=self.gantt_canvas.xview)
        gantt_hbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.gantt_canvas.configure(xscrollcommand=gantt_hbar.set) # 세로 스크롤 제거됨
        self.gantt_canvas.pack(fill=tk.X, expand=True) # 프레임 내에서 가로 확장
        self.draw_initial_gantt_layout() # 초기 레이아웃 그리기

        # 결과 테이블
        results_frame = ttk.LabelFrame(self.output_container_frame, text="Results Table", padding=5)
        results_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(0,5)) # 세로/가로 확장 O
        self.results_tree = ttk.Treeview(results_frame, columns=("pid", "arrival", "burst","remain", "start", "wait", "turnaround", "ntt"), show="headings", height=5)
        self.results_tree.heading("pid", text="PID")
        self.results_tree.column("pid", width=50, minwidth=40, anchor=tk.CENTER)
        self.results_tree.heading("arrival", text="Arr")
        self.results_tree.column("arrival", width=50, minwidth=40, anchor=tk.CENTER)
        self.results_tree.heading("burst", text="Burst")
        self.results_tree.column("burst", width=50, minwidth=40, anchor=tk.CENTER)
        self.results_tree.heading("remain", text="Rem")
        self.results_tree.column("remain", width=50, minwidth=40, anchor=tk.CENTER)
        self.results_tree.heading("start", text="Start")
        self.results_tree.column("start", width=50, minwidth=40, anchor=tk.CENTER)
        self.results_tree.heading("wait", text="Wait")
        self.results_tree.column("wait", width=50, minwidth=40, anchor=tk.CENTER)
        self.results_tree.heading("turnaround", text="TT")
        self.results_tree.column("turnaround", width=50, minwidth=40, anchor=tk.CENTER)
        self.results_tree.heading("ntt", text="NTT")
        self.results_tree.column("ntt", width=60, minwidth=50, anchor=tk.CENTER)
        results_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=results_scrollbar.set)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.results_tree_items = {} # Treeview 아이템 저장용 딕셔너리

        # 요약 정보 영역 (하단)
        summary_frame = ttk.Frame(self.output_container_frame, padding=(5, 2))
        summary_frame.pack(side=tk.BOTTOM, fill=tk.X, expand=False, pady=(0, 0)) # 세로 확장 X
        self.summary_label_vars = {} # StringVar 저장용 딕셔너리

        # 경과 시간 표시 라벨
        ttk.Label(summary_frame, text="Elapsed Time:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(5,2))
        time_var = tk.StringVar(value="0") # 초기값 0
        self.summary_label_vars["Current Time"] = time_var
        ttk.Label(summary_frame, textvariable=time_var, font=('Arial', 10), width=5).pack(side=tk.LEFT, padx=(0,10))

        # 총 전력 사용량 표시 라벨
        ttk.Label(summary_frame, text="Total Power Used:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(5,2))
        power_var = tk.StringVar(value="N/A") # 초기값 N/A
        self.summary_label_vars["Total Power Used"] = power_var
        ttk.Label(summary_frame, textvariable=power_var, font=('Arial', 10)).pack(side=tk.LEFT, padx=(0,5))


    def get_unique_pid(self):
        existing_pids = {int(self.process_tree.item(item, 'values')[0]) for item in self.process_tree.get_children()}
        return max(existing_pids, default=0) + 1

    def get_unique_processor_id(self):
        existing_ids = {int(self.processor_tree.item(item, 'values')[0]) for item in self.processor_tree.get_children()}
        return max(existing_ids, default=0) + 1
    
    # 프로세스 ID에 기반하여 랜덤 색상 생성 (ID가 같으면 항상 같은 색)
    def generate_color(self, pid):
        if pid == 0: return "#E0E0E0" # 유휴 상태는 회색
        if pid not in self.process_colors:
            random.seed(pid) # PID 기반 시드 설정으로 색상 일관성 유지
            r, g, b = [random.randint(100, 230) for _ in range(3)]
            # 너무 밝은 색 피하기 (선택 사항)
            if r > 200 and g > 200 and b > 200: b = random.randint(100,180)
            self.process_colors[pid] = f'#{r:02x}{g:02x}{b:02x}'
        return self.process_colors[pid]

    def update_list_counts(self):
        if hasattr(self, 'process_list_labelframe') and self.process_list_labelframe.winfo_exists():
            process_count = len(self.process_data)
            self.process_list_labelframe.config(text=f"Processes ({process_count}/{MAX_PROCESSES})")
        if hasattr(self, 'processor_list_labelframe') and self.processor_list_labelframe.winfo_exists():
            processor_count = len(self.processor_data)
            self.processor_list_labelframe.config(text=f"Processors ({processor_count}/{MAX_PROCESSORS})")

    # 프로세스 추가
    def add_process(self):
        if self.simulation_running:
            messagebox.showwarning("실행 중", "시뮬레이션 중에는 프로세스를 추가할 수 없습니다.")
            return
        if len(self.process_data) >= MAX_PROCESSES:
            messagebox.showwarning("개수 초과", f"최대 {MAX_PROCESSES}개의 프로세스만 추가할 수 있습니다.")
            return
        try: # 입력값 검증 및 추가
            pid = self.get_unique_pid() # 자동 PID 생성
            arrival = int(self.arrival_entry.get())
            burst = int(self.burst_entry.get())
            if arrival < 0 or burst <= 0: raise ValueError("Arrival은 0 이상, Burst는 0 보다 커야 합니다.")
            # Treeview 및 내부 데이터 리스트에 추가
            self.process_tree.insert("", tk.END, values=(pid, arrival, burst))
            self.process_data.append({'pid': pid, 'arrival': arrival, 'burst': burst})
            # 입력 필드 초기화 및 포커스 이동
            self.arrival_entry.delete(0, tk.END)
            self.burst_entry.delete(0, tk.END)
            self.arrival_entry.focus()
            self.update_list_counts() # 목록 개수 업데이트
        except ValueError as e: # 정수가 아니거나 조건 미충족 시
            messagebox.showerror("입력 오류", f"잘못된 프로세스 정보입니다: {e}")

    # 프로세스 제거
    def remove_process(self):
        if self.simulation_running:
            messagebox.showwarning("실행 중", "시뮬레이션 중에는 프로세스를 제거할 수 없습니다.")
            return
        selected_items = self.process_tree.selection() # 선택된 아이템들 가져오기
        if not selected_items: return # 선택된 것 없으면 무시
        if messagebox.askyesno("삭제 확인", "선택된 프로세스를 삭제하시겠습니까?"):
            pids_to_remove = [int(self.process_tree.item(item, 'values')[0]) for item in selected_items]
            # 내부 데이터 리스트에서 제거
            self.process_data = [p for p in self.process_data if p['pid'] not in pids_to_remove]
            # Treeview에서 제거
            for item in selected_items: self.process_tree.delete(item)
            self.update_list_counts() # 목록 개수 업데이트

    # 프로세서 추가
    def add_processor(self):
        if self.simulation_running:
            messagebox.showwarning("실행 중", "시뮬레이션 중에는 프로세서를 추가할 수 없습니다.")
            return
        if len(self.processor_data) >= MAX_PROCESSORS:
            messagebox.showwarning("개수 초과", f"최대 {MAX_PROCESSORS}개의 프로세서만 추가할 수 있습니다.")
            return
        proc_id = self.get_unique_processor_id() # 자동 ID 생성
        proc_type = self.proc_type_var.get().upper() # 대문자 P 또는 E
        if proc_type not in ['P', 'E']: raise ValueError("프로세서 타입은 'P' 또는 'E' 여야 합니다.")
        # Treeview 및 내부 데이터 리스트에 추가 (Quantum 표시는 안 함)
        self.processor_tree.insert("", tk.END, values=(proc_id, proc_type))
        self.processor_data.append({'id': proc_id, 'type': proc_type, 'quantum': None}) # 내부에선 quantum 저장 공간 유지
        self.draw_initial_gantt_layout() # 간트 차트 레이아웃 업데이트 (높이 조절 등)
        self.update_list_counts() # 목록 개수 업데이트

    # 프로세서 제거
    def remove_processor(self):
        if self.simulation_running:
            messagebox.showwarning("실행 중", "시뮬레이션 중에는 프로세서를 제거할 수 없습니다.")
            return
        selected_items = self.processor_tree.selection()
        if not selected_items: return
        if messagebox.askyesno("삭제 확인", "선택된 프로세서를 삭제하시겠습니까?"):
            ids_to_remove = [int(self.processor_tree.item(item, 'values')[0]) for item in selected_items]
            # 내부 데이터 리스트에서 제거
            self.processor_data = [p for p in self.processor_data if p['id'] not in ids_to_remove]
            # Treeview에서 제거
            for item in selected_items: self.processor_tree.delete(item)
            self.draw_initial_gantt_layout() # 간트 차트 레이아웃 업데이트
            self.update_list_counts() # 목록 개수 업데이트

    # RR이면 퀀텀 활성화
    def update_rr_quantum_visibility(self, event=None):
        selected_scheduler = self.scheduler_var.get()
        is_rr = selected_scheduler == SchedulerType.RR.name
        # 위젯이 실제로 화면에 그려졌는지 확인 후 pack/forget 호출 (오류 방지)
        is_label_mapped = self.rr_quantum_label.winfo_ismapped()
        is_entry_mapped = self.rr_quantum_entry.winfo_ismapped()

        if is_rr:
            if not is_label_mapped: # 아직 안 보이면
                self.rr_quantum_entry.pack(side=tk.LEFT, padx=(0, 10), before=self.start_button)
                self.rr_quantum_label.pack(side=tk.LEFT, padx=(0, 2), before=self.rr_quantum_entry)
            if not self.rr_quantum_entry.get(): self.rr_quantum_entry.insert(0, "4") # 기본값 4
        else: # RR 아니면 숨김
            if is_label_mapped: self.rr_quantum_label.pack_forget()
            if is_entry_mapped: self.rr_quantum_entry.pack_forget()

    # 속도값 변경 시 호출
    def update_speed(self, value):
        new_speed = int(float(value)) # 슬라이더 값은 float일 수 있으므로 int 변환
        speed_changed = new_speed != self.simulation_speed_ms
        self.simulation_speed_ms = new_speed
        # 라벨 텍스트 업데이트
        self.speed_label_var.set(f"{self.simulation_speed_ms} ms")

        # 시뮬레이션이 실행 중이고, 일시정지 상태가 아니며, 속도가 실제로 변경되었을 때만 재예약
        if speed_changed and self.simulation_running and not self.simulation_paused:
            print(f"속도 변경됨: {self.simulation_speed_ms}ms. 다음 스텝 재예약...")
            # 기존 예약된 after 이벤트 취소
            if self.current_after_id:
                self.after_cancel(self.current_after_id)
            # 새로운 속도로 즉시 다음 스텝 예약 (Tkinter 메인 루프에서 실행되도록 보장)
            self.current_after_id = self.after(self.simulation_speed_ms, self.simulation_step)

    # 초기화
    def reset_all(self):
        # 진행 중인 시뮬레이션 정지
        if self.current_after_id:
            self.after_cancel(self.current_after_id)
            self.current_after_id = None
        self.simulation_running = False
        self.simulation_paused = False

        # GUI 목록 및 내부 데이터 초기화
        self.process_tree.delete(*self.process_tree.get_children())
        self.processor_tree.delete(*self.processor_tree.get_children())
        self.process_data.clear()
        self.processor_data.clear()

        # 입력 필드 초기화
        self.arrival_entry.delete(0, tk.END)
        self.burst_entry.delete(0, tk.END)
        self.proc_type_var.set('P')
        self.rr_quantum_entry.delete(0, tk.END)
        self.scheduler_combo.current(0)
        self.update_rr_quantum_visibility() # 스케줄러 기본값 및 RR 필드 업데이트
        self.speed_scale.set(300)
        self.update_speed(300) # 속도 기본값

        self.update_list_counts()
        self.clear_outputs()
        self.start_button.config(text="Start", state=tk.NORMAL)
        self.pause_resume_button.config(text="Pause", state=tk.DISABLED)
        self.step_button.config(state=tk.DISABLED)
        self.enable_inputs()

        self.app = SchedulerApp()
        self.process_colors.clear()

    # 출력 영역 초기화
    def clear_outputs(self):
        self.gantt_canvas.delete("all")
        self.draw_initial_gantt_layout() # 빈 간트 차트 레이아웃 다시 그리기
        self.results_tree.delete(*self.results_tree.get_children())
        self.results_tree_items.clear()
        self.summary_label_vars["Total Power Used"].set("N/A")
        self.summary_label_vars["Current Time"].set("0")

    # 입력 비활성화 (시뮬레이션 시작)
    def disable_inputs(self):
        # input_frame과 control_frame 내의 특정 위젯들 비활성화 (재귀적으로 탐색)
        for frame in [self.input_frame, self.control_frame]:
            widgets_to_check = list(frame.winfo_children())
            while widgets_to_check:
                widget = widgets_to_check.pop(0)
                # 주요 제어 버튼(Start, Pause 등)은 제외하고 비활성화
                is_control_button = (widget == self.start_button or
                                     widget == self.pause_resume_button or
                                     widget == self.step_button or
                                     widget == self.reset_button)
                # 버튼, 입력필드, 콤보박스, 라디오버튼, 스케일, 체크박스 등 대상
                if not is_control_button and isinstance(widget, (ttk.Button, ttk.Entry, ttk.Combobox, ttk.Radiobutton, ttk.Scale, ttk.Checkbutton)):
                    widget.config(state=tk.DISABLED)
                # 프레임이나 레이블프레임이면 내부 위젯도 검사 대상에 추가
                if isinstance(widget, (ttk.Frame, ttk.LabelFrame, tk.Frame)):
                    widgets_to_check.extend(widget.winfo_children())

    # 입력 활성화 (시뮬레이션 이후)
    def enable_inputs(self):
        # 입력 프레임과 출력 프레임 내의 특정 위젯들 활성화 (재귀적으로 탐색)
        for frame in [self.input_frame, self.control_frame]:
            widgets_to_check = list(frame.winfo_children())
            while widgets_to_check:
                widget = widgets_to_check.pop(0)
                # 주요 제어 버튼(Start, Pause 등)은 제외하고 활성화
                is_control_button = (widget == self.start_button or
                                     widget == self.pause_resume_button or
                                     widget == self.step_button or
                                     widget == self.reset_button)

                if not is_control_button and isinstance(widget, (ttk.Button, ttk.Entry, ttk.Radiobutton, ttk.Scale, ttk.Checkbutton)):
                    widget.config(state=tk.NORMAL)
                # 콤보박스는 'readonly' 상태로 설정
                elif not is_control_button and isinstance(widget, ttk.Combobox):
                    widget.config(state="readonly")
                # RR Quantum 입력 필드는 스케줄러 선택 상태에 따라 활성/비활성
                elif widget == self.rr_quantum_entry:
                    is_rr = self.scheduler_var.get() == SchedulerType.RR.name
                    widget.config(state=tk.NORMAL if is_rr else tk.DISABLED)

                # 프레임이면 내부 위젯도 검사
                if isinstance(widget, (ttk.Frame, ttk.LabelFrame, tk.Frame)):
                    widgets_to_check.extend(widget.winfo_children())

    # 시뮬레이션 시작
    def start_simulation(self):
        if self.simulation_running: return # 이미 실행 중이면 무시
        self.clear_outputs() # 출력 영역 초기화
        self.app = SchedulerApp() # 새 시뮬레이션 앱 인스턴스 생성
        selected_scheduler_name = self.scheduler_var.get()
        try: # 스케줄러 타입 설정
            self.app.scheduler_type = SchedulerType[selected_scheduler_name]
        except KeyError: # 잘못된 스케줄러 이름이면 오류 처리
            messagebox.showerror("오류", f"알 수 없는 스케줄러 타입: {selected_scheduler_name}")
            return

        # RR이면 퀀텀 확인
        time_quantum = None
        if self.app.scheduler_type == SchedulerType.RR:
            try: # Quantum 값 읽기 및 검증
                quantum_str = self.rr_quantum_entry.get()
                if not quantum_str:
                    messagebox.showerror("입력 필요", "RR은 Time Quantum 값이 필요합니다.")
                    return
                time_quantum = int(quantum_str)
                if time_quantum <= 0:
                    raise ValueError("Time Quantum은 양수여야 합니다.")
            except ValueError as e: # 잘못된 값이면 오류 처리
                messagebox.showerror("입력 오류", f"잘못된 Time Quantum 값: {e}")
                return

        # 프로세스/프로세서 데이터 확인 및 시뮬레이터 앱에 추가
        if not self.process_data:
            messagebox.showwarning("입력 필요", "적어도 하나 이상의 프로세스를 추가해야 합니다.")
            return
        for p_data in self.process_data: self.app.add_process(**p_data) # 딕셔너리 언패킹으로 전달
        if not self.processor_data: 
            messagebox.showwarning("입력 필요", "적어도 하나 이상의 프로세서를 추가해야 합니다.")
            return
        for i, proc_data in enumerate(self.processor_data):
            q_for_processor = time_quantum if self.app.scheduler_type == SchedulerType.RR else None
            self.app.add_processor(id=proc_data['id'], type=proc_data['type'], time_quantum=q_for_processor)
            if self.app.scheduler_type == SchedulerType.RR: self.processor_data[i]['quantum'] = q_for_processor # 내부 데이터에 실제 사용된 quantum 저장

        # 스케줄러 선택 및 초기화, GUI 준비
        try: # 스케줄러 초기화
            self.app.select_scheduler()
            self.prepare_results_table(self.app.scheduler.processes) # 결과 테이블 초기화
            self.draw_initial_gantt_layout() # 간트 차트 초기 레이아웃 그리기 (프로세서 추가 후 높이 재조정)
        except Exception as e: # 초기화 실패 시
             messagebox.showerror("초기화 오류", f"스케줄러 초기화 실패: {e}")
             self.reset_all()
             return

        # 시뮬레이션 시작 상태 설정 및 GUI 업데이트
        self.simulation_running = True
        self.simulation_paused = False
        self.disable_inputs()
        self.start_button.config(state=tk.DISABLED)
        self.pause_resume_button.config(text="Pause", state=tk.NORMAL)
        self.step_button.config(state=tk.NORMAL) # 버튼 상태 변경
        self.simulation_step() # 첫 스텝 실행 (반복 시작)

    # 시뮬레이션 일시정지 및 재개
    def toggle_pause_simulation(self):
        if not self.simulation_running: return # 실행 중이 아니면 무시

        self.simulation_paused = not self.simulation_paused # 상태 반전

        if self.simulation_paused: # 일시정지 상태로 변경됨
            self.pause_resume_button.config(text="Resume") # 버튼 텍스트 변경
            if self.current_after_id: # 예약된 다음 스텝 실행 취소
                self.after_cancel(self.current_after_id)
                self.current_after_id = None
        else: # 재개 상태로 변경됨
            self.pause_resume_button.config(text="Pause") # 버튼 텍스트 변경
            self.step_button.config(state=tk.NORMAL) # Step 버튼 활성화 (다시 Pause 가능하게)
            # 즉시 다음 스텝을 예약하여 애니메이션 재개
            self.current_after_id = self.after(self.simulation_speed_ms, self.simulation_step)
    
    # 한 단계만 실행
    def step_simulation(self):
        if not self.simulation_running: return # 실행 중 아니면 무시

        # 만약 자동으로 실행 중이었다면 일단 정지 상태로 변경
        if not self.simulation_paused:
            self.simulation_paused = True
            self.pause_resume_button.config(text="Resume")
            if self.current_after_id: self.after_cancel(self.current_after_id)
            self.current_after_id = None
        # 한 단계 실행
        self._execute_one_step()


    # 한 단계 실행 후 GUI를 업데이트
    def _execute_one_step(self):
        scheduler = self.app.scheduler # 현재 스케줄러 객체 가져오기

        if scheduler.has_next(): # 실행할 프로세스가 남았는지 확인
            current_time = scheduler.current_time # 현재 시간 기록 (업데이트 전)

            # 루틴 수행
            scheduler.update_ready_queue()
            scheduler.schedule()
            scheduler.assign_process()
            scheduler.power_off_idle_processors()
            scheduler.process_waiting_time_update()

            # 현재 상태 가져오기 (로직 실행 후)
            current_processes = scheduler.get_process()
            current_processors = scheduler.get_processors()
            current_power = scheduler.calculate_total_power()

            # GUI 업데이트
            self.update_gantt_chart_live(current_processors, current_time)
            self.update_results_table_live(current_processes)
            self.update_summary_live(current_time, current_power)

            scheduler.update_current_time()
            return True
        else:
            self.simulation_finished()
            return False
        
    # 시뮬레이션 루프
    def simulation_step(self):
        # 실행 중이 아니거나 일시정지 상태면 즉시 반환 (루프 중단)
        if not self.simulation_running or self.simulation_paused:
            self.current_after_id = None # 명시적으로 ID 클리어
            return

        # 한 단계 실행 시도
        executed = self._execute_one_step()

        # 실행 성공했고, 여전히 실행 중 & 일시정지 상태 아니면 다음 스텝 예약
        if executed and self.simulation_running and not self.simulation_paused:
            self.current_after_id = self.after(self.simulation_speed_ms, self.simulation_step)
        else: # 실행 실패(종료)했거나 상태 변경(일시정지 등) 시 예약 안 함
            self.current_after_id = None

    # 시뮬레이션 종료
    def simulation_finished(self):
        self.simulation_running = False
        self.simulation_paused = False
        final_time = "N/A"
        total_power = 0.0

        # 앱과 스케줄러 객체가 유효한지 확인 (Reset 등으로 인해 없어졌을 수 있음)
        if self.app and self.app.scheduler:
            # 최종 데이터 가져오기 (hasNext가 False가 된 직후이므로 시간은 마지막 완료 스텝 + 1)
            final_processes = self.app.scheduler.get_process()
            final_processors = self.app.scheduler.get_processors()
            final_time = self.app.scheduler.current_time # 최종 시간
            total_power = self.app.scheduler.calculate_total_power() # 최종 전력
            self.update_results_table_live(final_processes) # 마지막 상태 결과 테이블 반영
            self.calculate_and_display_summary(total_power, final_time) # 최종 요약 정보 표시
        else: # 앱/스케줄러 없으면 N/A 표시
            self.calculate_and_display_summary(0.0, 0)

        # 제어 버튼 상태 복구
        self.start_button.config(text="Start", state=tk.NORMAL)
        self.pause_resume_button.config(text="Pause", state=tk.DISABLED)
        self.step_button.config(state=tk.DISABLED)
        self.enable_inputs() # 입력 필드 활성화

        # 예약된 이벤트 확실히 취소
        if self.current_after_id:
            self.after_cancel(self.current_after_id)
            self.current_after_id = None

        # 완료 메시지 표시
        ftime_display = final_time if final_time != "N/A" else 0
        messagebox.showinfo("시뮬레이션 완료", f"시뮬레이션이 시간 {ftime_display}에 종료되었습니다.")


    # 간트 차트 초기 설정
    def draw_initial_gantt_layout(self):
        self.gantt_canvas.delete("all")
        self.process_colors.clear()
        num_processors = len(self.processor_data)

        # 필요한 캔버스 높이 계산
        # 헤더 높이 + (프로세서 개수 * (행 높이 + 행 간격)) + 하단 여백
        canvas_height = self.gantt_header_height + (num_processors * (self.gantt_row_height + self.gantt_padding)) + self.gantt_padding
        if num_processors == 0: canvas_height = self.gantt_header_height + 30 # 프로세서 없어도 최소 높이
        self.gantt_canvas.config(height=canvas_height)

        # 스크롤 영역
        initial_drawing_width = 800 # 시간 축 초기 표시 너비
        # 스크롤 가능한 전체 너비 = 라벨 너비 + 시간 축 너비 + 우측 여백
        scroll_width = self.gantt_label_width + initial_drawing_width + self.gantt_padding
        self.gantt_canvas.configure(scrollregion=(0, 0, scroll_width, canvas_height)) # 스크롤 영역 설정

        # 시간 축 그리기
        # 그릴 수 있는 최대 시간 계산
        drawing_width_available = initial_drawing_width
        max_initial_time = int(drawing_width_available / self.gantt_time_scale)
        max_initial_time = max(0, max_initial_time)

        # 시간 눈금 및 라벨 그리기 (라벨 너비만큼 오른쪽으로 오프셋)
        time_axis_y = self.gantt_padding + self.gantt_header_height / 2 # 시간 라벨 Y 위치
        grid_line_top = self.gantt_padding # 격자선 시작 Y
        grid_line_bottom = canvas_height - self.gantt_padding # 격자선 끝 Y
        for t in range(max_initial_time + 1):
            x = self.gantt_label_width + (t * self.gantt_time_scale) # X 위치 오프셋 적용
            # 격자선
            self.gantt_canvas.create_line(x, grid_line_top, x, grid_line_bottom, fill="lightgrey", dash=(2, 2), tags="time_grid")
            # 시간 라벨 (5 단위 또는 짧을 때 전부)
            if t % 5 == 0 or max_initial_time <= 20:
                self.gantt_canvas.create_text(x, time_axis_y, text=str(t), anchor=tk.CENTER, tags="time_label")

        # 프로세서 라벨 그리기
        label_x_pos = self.gantt_label_width - 5 # 라벨 우측 정렬 X 위치 (여백 5px)
        for i, processor_info in enumerate(self.processor_data):
            # 각 프로세서 행의 Y 위치 계산
            y_top = self.gantt_padding + self.gantt_header_height + i * (self.gantt_row_height + self.gantt_padding)
            label_y_center = y_top + self.gantt_row_height / 2 # 라벨 중앙 Y

            self.gantt_canvas.create_text(label_x_pos, label_y_center - 6, text=f"CPU {processor_info['id']}", anchor=tk.E, tags="proc_label", font=('Arial', 9))
            self.gantt_canvas.create_text(label_x_pos, label_y_center + 6, text=f"({processor_info['type']}-Core)", anchor=tk.E, tags="proc_label", font=('Arial', 8))

    # 간트 차트 업데이트
    def update_gantt_chart_live(self, processors: list[Processor], current_time: int):
        if current_time == 0: return
        time_step = current_time - 1 # 이전 시간 간격 [t-1, t]에 대한 블록을 그림

        # 캔버스 높이 조절
        num_processors = len(self.processor_data)
        required_canvas_height = self.gantt_header_height + (num_processors * (self.gantt_row_height + self.gantt_padding)) + self.gantt_padding
        if num_processors == 0:
            required_canvas_height = self.gantt_header_height + 30

        # 현재 캔버스 높이와 필요한 높이가 다르면 캔버스 높이 업데이트
        # winfo_reqheight() 사용: Tk가 계산한 필요한 높이
        if abs(self.gantt_canvas.winfo_reqheight() - required_canvas_height) > 1:
             self.gantt_canvas.config(height=required_canvas_height)

        # 스크롤 영역 너비 조절
        # 필요한 전체 너비 = 라벨 너비 + (현재 시간 * 스케일) + 우측 여백
        required_total_width = self.gantt_label_width + (current_time * self.gantt_time_scale) + self.gantt_padding
        current_scroll_region = self.gantt_canvas.cget('scrollregion')
        if current_scroll_region: # 현재 스크롤 영역 정보 읽기
            try: # 간혹 빈 문자열 등이 반환될 수 있으므로 try/except
                 _, _, current_scroll_width, current_scroll_height = map(int, current_scroll_region.split())
            except ValueError: # 파싱 실패 시 기본값 사용
                 current_scroll_width = self.gantt_label_width + 800
                 current_scroll_height = required_canvas_height
        else: # 스크롤 영역 정보 없으면 기본값
            current_scroll_width = self.gantt_label_width + 800
            current_scroll_height = required_canvas_height

        # 스크롤 영역 업데이트 시 사용할 캔버스 높이 (위에서 계산된 값)
        current_canvas_height = required_canvas_height

        width_changed = False
        if required_total_width > current_scroll_width: # 필요한 너비가 현재 스크롤 너비보다 크면 확장
            new_scroll_width = required_total_width + 200 # 버퍼 추가
            # 스크롤 영역 업데이트 (너비, 높이 모두 최신 값으로)
            self.gantt_canvas.configure(scrollregion=(0, 0, new_scroll_width, current_canvas_height))
            # 확장된 영역에 시간 축/격자 추가
            start_t = int((current_scroll_width - self.gantt_label_width) / self.gantt_time_scale) # 이전 끝 시간부터
            end_t = int((new_scroll_width - self.gantt_label_width) / self.gantt_time_scale) + 1 # 새 끝 시간까지
            time_axis_y = self.gantt_padding + self.gantt_header_height / 2
            grid_line_top = self.gantt_padding
            grid_line_bottom = current_canvas_height - self.gantt_padding
            for t in range(start_t , end_t):
                x = self.gantt_label_width + (t * self.gantt_time_scale) # 라벨 오프셋 적용
                self.gantt_canvas.create_line(x, grid_line_top, x, grid_line_bottom, fill="lightgrey", dash=(2, 2), tags="time_grid")
                if t % 5 == 0: self.gantt_canvas.create_text(x, time_axis_y, text=str(t), anchor=tk.CENTER, tags="time_label")
            current_scroll_width = new_scroll_width
            width_changed = True # 상태 업데이트

        height_changed = False
        # 스크롤 영역 높이가 실제 필요한 높이와 다르면 업데이트 (프로세서 제거 등)
        if abs(current_scroll_height - current_canvas_height) > 1:
            self.gantt_canvas.configure(scrollregion=(0, 0, current_scroll_width, current_canvas_height))
            height_changed = True # 상태 업데이트

        # 자동 스크롤 (가로)
        # 현재 보이는 캔버스 위젯의 너비
        visible_width = self.gantt_canvas.winfo_width()
        # 스크롤이 필요한 조건: 너비/높이 변경되었거나, 현재 시간 블록 끝이 보이는 영역 밖에 있을 때
        # 스크롤 타겟 X 위치 = 라벨 너비 + 현재 시간 블록 끝 위치
        target_x_pos = self.gantt_label_width + (current_time * self.gantt_time_scale)
        if (width_changed or height_changed or (target_x_pos > visible_width + self.gantt_canvas.xview()[0] * current_scroll_width)) and current_scroll_width > 0:
            # 스크롤할 위치 계산 (비율)
            scroll_fraction = (target_x_pos - visible_width + 50) / current_scroll_width # 50px 정도 여유
            self.gantt_canvas.xview_moveto(min(max(0, scroll_fraction), 1.0)) # 0~1 사이 값으로 제한

        # 현재 시간 단계의 블록 그리기
        for i, processor in enumerate(processors):
            try: # processor_data에서 현재 processor 객체의 인덱스 찾기 (ID 기준)
                gui_proc_index = next(idx for idx, data in enumerate(self.processor_data) if data['id'] == processor.id)
            except StopIteration: continue # GUI 목록에 없는 프로세서면 건너뜀 (이론상 발생 안 함)

            # 블록 그릴 Y 좌표 계산
            y_top = self.gantt_padding + self.gantt_header_height + gui_proc_index * (self.gantt_row_height + self.gantt_padding)
            y_bottom = y_top + self.gantt_row_height

            # 해당 시간 단계(time_step)에 실행된 프로세스 ID 가져오기 (processor.process_queue 사용)
            pid_at_step = 0 # 기본값: 유휴(idle)
            if time_step < len(processor.process_queue): # 해당 시간 기록이 있는지 확인
                pid_at_step = processor.process_queue[time_step] if processor.process_queue[time_step] is not None else 0

            pid = pid_at_step # 사용할 PID
            # 블록 그릴 X 좌표 계산 (라벨 너비 오프셋 적용)
            x_start = self.gantt_label_width + time_step * self.gantt_time_scale
            x_end = x_start + self.gantt_time_scale

            color = self.generate_color(pid) # PID 기반 색상 가져오기
            tag_name = f"t{time_step}_p{processor.id}" # 고유 태그 생성 (나중에 삭제/수정 등에 사용 가능)

            if pid != 0: # 유휴 상태(0)는 그리지 않거나 다른 스타일 적용 가능
                # 사각형 블록 그리기
                self.gantt_canvas.create_rectangle(x_start, y_top + 1, x_end, y_bottom - 1, fill=color, outline="black", width=1, tags=(tag_name, "block"))
                # 블록 너비가 충분하면 내부에 PID 텍스트 표시
                if self.gantt_time_scale > 18:
                    # 배경색 밝기에 따라 텍스트 색상 결정 (가독성 향상)
                    text_color = "white" if sum(int(color[i:i+2], 16) for i in (1, 3, 5)) < 384 else "black"
                    self.gantt_canvas.create_text(x_start + self.gantt_time_scale / 2, y_top + self.gantt_row_height / 2, text=str(pid), fill=text_color, font=('Arial', 8, 'bold'), tags=(tag_name, "block_text"))

    # 결과 테이블 초기 설정
    def prepare_results_table(self, initial_processes: list[Process]):
        self.results_tree.delete(*self.results_tree.get_children())
        self.results_tree_items.clear()
        initial_processes.sort(key=lambda p: p.pid)
        # 각 프로세스 정보를 테이블 행으로 추가
        for p in initial_processes:
             item_id = self.results_tree.insert("", tk.END, values=(p.pid, p.arrival, p.burst, p.remaining_time, "-", "-", "-", "-"))
             self.results_tree_items[p.pid] = item_id # PID를 key로 Treeview 아이템 ID 저장

    # 결과 테이블 업데이트
    def update_results_table_live(self, current_processes: list[Process]):
        for p in current_processes:
            if p.pid in self.results_tree_items:
                item_id = self.results_tree_items[p.pid] # 저장된 Treeview 아이템 ID 가져오기
                # 표시할 값들
                st = p.start_time if p.start_time is not None else "-"
                wt = p.wait_time
                tt = p.turnaround_time if p.turnaround_time is not None else "-"
                ntt = f"{p.normalized_turnaround_time:.3f}" if p.normalized_turnaround_time is not None else "-"
                remain = p.remaining_time
                # 업데이트
                self.results_tree.item(item_id, values=(p.pid, p.arrival, p.burst, remain, st, wt, tt, ntt))

    # 요약 업데이트
    def update_summary_live(self, current_time: int, current_power: float):
        self.summary_label_vars["Current Time"].set(str(current_time))
        self.summary_label_vars["Total Power Used"].set(f"{current_power:.2f}")

    # 최종 요약 정보
    def calculate_and_display_summary(self, total_power: float, final_time: int):
        self.summary_label_vars["Current Time"].set(str(final_time))
        self.summary_label_vars["Total Power Used"].set(f"{total_power:.2f}")

if __name__ == "__main__":
    app_gui = SchedulerGUI()
    app_gui.mainloop() # Tkinter 이벤트 루프 시작
