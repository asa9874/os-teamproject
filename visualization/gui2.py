import customtkinter as ctk
from tkinter import messagebox
import tkinter.ttk as ttk
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
pip install customtkinter 한후에 실행가능
"""
class SchedulerGUI2(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("프로세스 스케줄링 시뮬레이터")
        self.geometry("1250x700")

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

        # 간트 차트 관련 파라미터
        self.gantt_label_width = 70
        self.gantt_padding = 10
        self.gantt_header_height = 25
        self.gantt_row_height = 30
        self.gantt_time_scale = 25

        # 제어 프레임 (상단)
        self.control_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.control_frame.pack(side="top", fill="x", padx=5, pady=5)

        # 좌우 분할용 (customtkinter에는 PanedWindow가 없으므로 ttk.PanedWindow 사용)
        self.main_pane = ttk.PanedWindow(self, orient="horizontal")
        self.main_pane.pack(fill="both", expand=True)

        # 입력 프레임 (좌측) 1/4
        self.input_frame = ctk.CTkFrame(self.main_pane, corner_radius=8)
        self.main_pane.add(self.input_frame, weight=0)

        # 출력 프레임 (우측) 3/4
        self.output_container_frame = ctk.CTkFrame(self.main_pane, corner_radius=8)
        self.main_pane.add(self.output_container_frame, weight=3)

        # 위젯 생성
        self.setup_control_widgets()
        self.setup_input_widgets()
        self.setup_output_widgets()

        # 프로세스, 프로세서 목록 라벨 초기화
        self.update_list_counts()

    # 제어 위젯
    def setup_control_widgets(self):
        # 알고리즘 선택
        ctk.CTkLabel(self.control_frame, text="Algorithm:").pack(side="left", padx=(0,2))
        scheduler_names = [s.name for s in SchedulerType]
        self.scheduler_var = ctk.StringVar(value=scheduler_names[0])
        self.scheduler_combo = ctk.CTkComboBox(
            self.control_frame,
            values=scheduler_names,
            variable=self.scheduler_var,
            width=100,
            command=self.update_rr_quantum_visibility
        )
        self.scheduler_combo.pack(side="left", padx=(0,10))

        # RR용 타임 퀀텀
        self.rr_quantum_label = ctk.CTkLabel(self.control_frame, text="Time Quantum:")
        self.rr_quantum_entry = ctk.CTkEntry(self.control_frame, width=50)

        # 시뮬레이션 제어용 버튼들
        self.start_button = ctk.CTkButton(self.control_frame, text="Start", command=self.start_simulation, width=70)
        self.start_button.pack(side="left", padx=(10,2))
        self.pause_resume_button = ctk.CTkButton(self.control_frame, text="Pause", command=self.toggle_pause_simulation, width=70, state="disabled")
        self.pause_resume_button.pack(side="left", padx=2)
        self.step_button = ctk.CTkButton(self.control_frame, text="Step", command=self.step_simulation, width=50, state="disabled")
        self.step_button.pack(side="left", padx=2)
        self.reset_button = ctk.CTkButton(self.control_frame, text="Reset", command=self.reset_all, width=60)
        self.reset_button.pack(side="left", padx=(10,2))

        # 속도 조절
        self.speed_label_var = ctk.StringVar(value=f"{self.simulation_speed_ms} ms")
        ctk.CTkLabel(self.control_frame, textvariable=self.speed_label_var, width=70).pack(side="right", padx=(0,5))
        self.speed_scale = ctk.CTkSlider(self.control_frame, from_=50, to=500, command=self.update_speed, width=120)
        self.speed_scale.set(self.simulation_speed_ms)
        self.speed_scale.pack(side="right", padx=2)
        ctk.CTkLabel(self.control_frame, text="Speed:").pack(side="right", padx=0)

        # RR이면 퀀텀 위젯 표시
        self.update_rr_quantum_visibility()

    # 입력 위젯
    def setup_input_widgets(self):
        input_content_frame = ctk.CTkFrame(self.input_frame)
        input_content_frame.pack(fill="both", expand=True)

        # 프로세스 입력
        process_section_frame = ctk.CTkFrame(input_content_frame)
        process_section_frame.pack(side="top", fill="x", pady=(0,10))

        # 'Add Process' 제목 레이블과 프레임
        process_input_header = ctk.CTkLabel(process_section_frame, text="Add Process", font=("Arial", 12, "bold"))
        process_input_header.pack(pady=(5,0), anchor="w", padx=5)
        process_input_frame = ctk.CTkFrame(process_section_frame, corner_radius=8)
        process_input_frame.pack(pady=5, fill="x", padx=5)

        ctk.CTkLabel(process_input_frame, text="Arrival:").grid(row=0, column=0, padx=5, pady=(5,2), sticky="w")
        self.arrival_entry = ctk.CTkEntry(process_input_frame, width=50)
        self.arrival_entry.grid(row=0, column=1, padx=5, pady=(5,2), sticky="ew")
        ctk.CTkLabel(process_input_frame, text="Burst:").grid(row=1, column=0, padx=5, pady=(2,5), sticky="w")
        self.burst_entry = ctk.CTkEntry(process_input_frame, width=50)
        self.burst_entry.grid(row=1, column=1, padx=5, pady=(2,5), sticky="ew")
        self.add_process_button = ctk.CTkButton(process_input_frame, text="Add", command=self.add_process, width=60)
        self.add_process_button.grid(row=0, column=2, rowspan=2, padx=10, pady=5, sticky="ns")
        process_input_frame.grid_columnconfigure(1, weight=1)

        # 프로세스 목록 (ttk.Treeview 사용)
        process_list_header = ctk.CTkLabel(process_section_frame, text="Processes", font=("Arial", 12, "bold"))
        process_list_header.pack(pady=(5,0), anchor="w", padx=5)
        self.process_list_labelframe = ctk.CTkFrame(process_section_frame)
        self.process_list_labelframe.pack(pady=5, fill="x", padx=5)
        self.process_tree = ttk.Treeview(self.process_list_labelframe, columns=("pid", "arrival", "burst"), show="headings", height=6)
        self.process_tree.heading("pid", text="PID")
        self.process_tree.column("pid", width=40, minwidth=30, anchor="center")
        self.process_tree.heading("arrival", text="Arrival")
        self.process_tree.column("arrival", width=50, minwidth=40, anchor="center")
        self.process_tree.heading("burst", text="Burst")
        self.process_tree.column("burst", width=50, minwidth=40, anchor="center")
        process_scrollbar = ttk.Scrollbar(self.process_list_labelframe, orient="vertical", command=self.process_tree.yview)
        self.process_tree.configure(yscrollcommand=process_scrollbar.set)
        process_scrollbar.pack(side="right", fill="y")
        self.process_tree.pack(side="left", fill="x", expand=True)
        self.remove_process_button = ctk.CTkButton(process_section_frame, text="Remove Selected Process", command=self.remove_process)
        self.remove_process_button.pack(pady=(0,5), padx=5)

        # 프로세서 입력
        processor_section_frame = ctk.CTkFrame(input_content_frame)
        processor_section_frame.pack(side="top", fill="x", padx=5)
        processor_input_header = ctk.CTkLabel(processor_section_frame, text="Add Processor", font=("Arial", 12, "bold"))
        processor_input_header.pack(pady=(5,0), anchor="w")
        processor_input_frame = ctk.CTkFrame(processor_section_frame, corner_radius=8, width=400, height=80)
        processor_input_frame.pack(pady=5, fill="x")
        processor_input_frame.pack_propagate(False)  # 지정한 width, height 유지

        ctk.CTkLabel(processor_input_frame, text="Type:").grid(row=0, column=0, padx=5, pady=(10,2), sticky="w")
        self.proc_type_var = ctk.StringVar(value="P")
        proc_type_p = ctk.CTkRadioButton(processor_input_frame, text="P-Core", variable=self.proc_type_var, value="P")
        proc_type_e = ctk.CTkRadioButton(processor_input_frame, text="E-Core", variable=self.proc_type_var, value="E")
        proc_type_p.grid(row=0, column=1, padx=5, pady=(10,2), sticky="w")
        proc_type_e.grid(row=1, column=1, padx=5, pady=(2,10), sticky="w")
        self.add_processor_button = ctk.CTkButton(processor_input_frame, text="Add", command=self.add_processor, width=60)
        self.add_processor_button.grid(row=0, column=2, rowspan=2, padx=10, pady=5, sticky="ns")
        processor_input_frame.grid_columnconfigure(1, weight=1)

        processor_list_header = ctk.CTkLabel(processor_section_frame, text="Processors", font=("Arial", 12, "bold"))
        processor_list_header.pack(pady=(5,0), anchor="w")
        self.processor_list_labelframe = ctk.CTkFrame(processor_section_frame)
        self.processor_list_labelframe.pack(pady=5, fill="x")
        self.processor_tree = ttk.Treeview(self.processor_list_labelframe, columns=("id", "type"), show="headings", height=4)
        self.processor_tree.heading("id", text="ID")
        self.processor_tree.column("id", width=50, minwidth=40, anchor="center")
        self.processor_tree.heading("type", text="Type")
        self.processor_tree.column("type", width=70, minwidth=50, anchor="center")
        processor_scrollbar = ttk.Scrollbar(self.processor_list_labelframe, orient="vertical", command=self.processor_tree.yview)
        self.processor_tree.configure(yscrollcommand=processor_scrollbar.set)
        processor_scrollbar.pack(side="right", fill="y")
        self.processor_tree.pack(side="left", fill="x", expand=True)
        self.remove_processor_button = ctk.CTkButton(processor_section_frame, text="Remove Selected Processor", command=self.remove_processor)
        self.remove_processor_button.pack(pady=(0,5))

    # 출력 위젯
    def setup_output_widgets(self):
        # 간트 차트 영역
        gantt_header = ctk.CTkLabel(self.output_container_frame, text="Gantt Chart", font=("Arial", 12, "bold"))
        gantt_header.pack(pady=(5,0), anchor="w", padx=5)
        gantt_frame = ctk.CTkFrame(self.output_container_frame)  # padx, pady 제거
        gantt_frame.pack(side="top", fill="x", padx=5, pady=5)  # pack()에서 패딩 지정
        self.gantt_canvas = ctk.CTkCanvas(gantt_frame, bg="white", height=100, highlightthickness=0)
        gantt_hbar = ttk.Scrollbar(gantt_frame, orient="horizontal", command=self.gantt_canvas.xview)
        gantt_hbar.pack(side="bottom", fill="x")
        self.gantt_canvas.configure(xscrollcommand=gantt_hbar.set)
        self.gantt_canvas.pack(fill="x", expand=True)
        self.draw_initial_gantt_layout()

        # 결과 테이블 영역
        results_header = ctk.CTkLabel(self.output_container_frame, text="Results Table", font=("Arial", 12, "bold"))
        results_header.pack(pady=(5,0), anchor="w", padx=5)
        results_frame = ctk.CTkFrame(self.output_container_frame)  # padx, pady 제거
        results_frame.pack(side="top", fill="both", expand=True, padx=5, pady=(0,5))  # pack()에서 패딩 지정
        columns = ("pid", "arrival", "burst", "remain", "start", "wait", "turnaround", "ntt")
        self.results_tree = ttk.Treeview(
            results_frame,
            columns=columns,
            show="headings",
            height=5
        )
        self.results_tree.heading("pid", text="PID")
        self.results_tree.heading("arrival", text="arrival")
        self.results_tree.heading("burst", text="burst")
        self.results_tree.heading("remain", text="remain")
        self.results_tree.heading("start", text="start")
        self.results_tree.heading("wait", text="wait")
        self.results_tree.heading("turnaround", text="turnaround")
        self.results_tree.heading("ntt", text="NTT")
        for col in columns:
            self.results_tree.column(col, width=120, stretch=False)
            self.results_tree.heading(col, text=col.capitalize())
        
        # ... (Treeview 설정 코드)
        results_scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=results_scrollbar.set)
        results_scrollbar.pack(side="right", fill="y")
        self.results_tree.pack(side="left", fill="both", expand=True)
        self.results_tree_items = {}

        # 요약 정보 영역
        summary_frame = ctk.CTkFrame(self.output_container_frame)  # padx, pady 제거
        summary_frame.pack(side="bottom", fill="x", padx=5, pady=2)  # pack()에서 패딩 지정
        self.summary_label_vars = {}
        ctk.CTkLabel(summary_frame, text="Elapsed Time:", font=("Arial", 10, "bold")).pack(side="left", padx=(5,2))
        time_var = ctk.StringVar(value="0")
        self.summary_label_vars["Current Time"] = time_var
        ctk.CTkLabel(summary_frame, textvariable=time_var, font=("Arial", 10), width=50).pack(side="left", padx=(0,10))
        ctk.CTkLabel(summary_frame, text="Total Power Used:", font=("Arial", 10, "bold")).pack(side="left", padx=(5,2))
        power_var = ctk.StringVar(value="N/A")
        self.summary_label_vars["Total Power Used"] = power_var
        ctk.CTkLabel(summary_frame, textvariable=power_var, font=("Arial", 10)).pack(side="left", padx=(0,5))

    def get_unique_pid(self):
        existing_pids = {int(self.process_tree.item(item, 'values')[0]) for item in self.process_tree.get_children()}
        return max(existing_pids, default=0) + 1

    def get_unique_processor_id(self):
        existing_ids = {int(self.processor_tree.item(item, 'values')[0]) for item in self.processor_tree.get_children()}
        return max(existing_ids, default=0) + 1

    def generate_color(self, pid):
        if pid == 0:
            return "#E0E0E0"
        if pid not in self.process_colors:
            random.seed(pid)
            r, g, b = [random.randint(100, 230) for _ in range(3)]
            if r > 200 and g > 200 and b > 200:
                b = random.randint(100,180)
            self.process_colors[pid] = f'#{r:02x}{g:02x}{b:02x}'
        return self.process_colors[pid]

    def update_list_counts(self):
        if hasattr(self, 'process_list_labelframe') and self.process_list_labelframe.winfo_exists():
            process_count = len(self.process_data)
            # 제목 레이블 업데이트
            new_text = f"Processes ({process_count}/{MAX_PROCESSES})"
            for child in self.process_list_labelframe.winfo_children():
                if isinstance(child, ctk.CTkLabel):
                    child.configure(text=new_text)
        if hasattr(self, 'processor_list_labelframe') and self.processor_list_labelframe.winfo_exists():
            processor_count = len(self.processor_data)
            new_text = f"Processors ({processor_count}/{MAX_PROCESSORS})"
            for child in self.processor_list_labelframe.winfo_children():
                if isinstance(child, ctk.CTkLabel):
                    child.configure(text=new_text)

    def add_process(self):
        if self.simulation_running:
            messagebox.showwarning("실행 중", "시뮬레이션 중에는 프로세스를 추가할 수 없습니다.")
            return
        if len(self.process_data) >= MAX_PROCESSES:
            messagebox.showwarning("개수 초과", f"최대 {MAX_PROCESSES}개의 프로세스만 추가할 수 있습니다.")
            return
        try:
            pid = self.get_unique_pid()
            arrival = int(self.arrival_entry.get())
            burst = int(self.burst_entry.get())
            if arrival < 0 or burst <= 0:
                raise ValueError("Arrival은 0 이상, Burst는 0 보다 커야 합니다.")
            self.process_tree.insert("", "end", values=(pid, arrival, burst))
            self.process_data.append({'pid': pid, 'arrival': arrival, 'burst': burst})
            self.arrival_entry.delete(0, "end")
            self.burst_entry.delete(0, "end")
            self.arrival_entry.focus()
            self.update_list_counts()
        except ValueError as e:
            messagebox.showerror("입력 오류", f"잘못된 프로세스 정보입니다: {e}")

    def remove_process(self):
        if self.simulation_running:
            messagebox.showwarning("실행 중", "시뮬레이션 중에는 프로세스를 제거할 수 없습니다.")
            return
        selected_items = self.process_tree.selection()
        if not selected_items:
            return
        if messagebox.askyesno("삭제 확인", "선택된 프로세스를 삭제하시겠습니까?"):
            pids_to_remove = [int(self.process_tree.item(item, 'values')[0]) for item in selected_items]
            self.process_data = [p for p in self.process_data if p['pid'] not in pids_to_remove]
            for item in selected_items:
                self.process_tree.delete(item)
            self.update_list_counts()

    def add_processor(self):
        if self.simulation_running:
            messagebox.showwarning("실행 중", "시뮬레이션 중에는 프로세서를 추가할 수 없습니다.")
            return
        if len(self.processor_data) >= MAX_PROCESSORS:
            messagebox.showwarning("개수 초과", f"최대 {MAX_PROCESSORS}개의 프로세서만 추가할 수 있습니다.")
            return
        proc_id = self.get_unique_processor_id()
        proc_type = self.proc_type_var.get().upper()
        if proc_type not in ['P', 'E']:
            raise ValueError("프로세서 타입은 'P' 또는 'E' 여야 합니다.")
        self.processor_tree.insert("", "end", values=(proc_id, proc_type))
        self.processor_data.append({'id': proc_id, 'type': proc_type, 'quantum': None})
        self.draw_initial_gantt_layout()
        self.update_list_counts()

    def remove_processor(self):
        if self.simulation_running:
            messagebox.showwarning("실행 중", "시뮬레이션 중에는 프로세서를 제거할 수 없습니다.")
            return
        selected_items = self.processor_tree.selection()
        if not selected_items:
            return
        if messagebox.askyesno("삭제 확인", "선택된 프로세서를 삭제하시겠습니까?"):
            ids_to_remove = [int(self.processor_tree.item(item, 'values')[0]) for item in selected_items]
            self.processor_data = [p for p in self.processor_data if p['id'] not in ids_to_remove]
            for item in selected_items:
                self.processor_tree.delete(item)
            self.draw_initial_gantt_layout()
            self.update_list_counts()

    def update_rr_quantum_visibility(self, event=None):
        selected_scheduler = self.scheduler_var.get()
        is_rr = selected_scheduler == SchedulerType.RR.name
        print(f"Selected Scheduler: {selected_scheduler}, Is RR: {is_rr}")

        if is_rr:
            if not self.rr_quantum_label.winfo_ismapped():
                self.rr_quantum_entry.pack(side="left", padx=(0, 10), before=self.start_button)
                self.rr_quantum_label.pack(side="left", padx=(0, 2), before=self.rr_quantum_entry)
            if not self.rr_quantum_entry.get():
                self.rr_quantum_entry.insert(0, "4")
        else:
            if self.rr_quantum_label.winfo_ismapped():
                self.rr_quantum_label.pack_forget()
            if self.rr_quantum_entry.winfo_ismapped():
                self.rr_quantum_entry.pack_forget()

    def update_speed(self, value):
        new_speed = int(float(value))
        speed_changed = new_speed != self.simulation_speed_ms
        self.simulation_speed_ms = new_speed
        self.speed_label_var.set(f"{self.simulation_speed_ms} ms")
        if speed_changed and self.simulation_running and not self.simulation_paused:
            if self.current_after_id:
                self.after_cancel(self.current_after_id)
            self.current_after_id = self.after(self.simulation_speed_ms, self.simulation_step)

    def reset_all(self):
        if self.current_after_id:
            self.after_cancel(self.current_after_id)
            self.current_after_id = None
        self.simulation_running = False
        self.simulation_paused = False
        self.process_tree.delete(*self.process_tree.get_children())
        self.processor_tree.delete(*self.processor_tree.get_children())
        self.process_data.clear()
        self.processor_data.clear()
        self.arrival_entry.delete(0, "end")
        self.burst_entry.delete(0, "end")
        self.proc_type_var.set("P")
        self.rr_quantum_entry.delete(0, "end")
        self.scheduler_combo.set(self.scheduler_combo.cget("values")[0])
        self.update_rr_quantum_visibility()
        self.speed_scale.set(300)
        self.update_speed(300)
        self.update_list_counts()
        self.clear_outputs()
        self.start_button.configure(text="Start", state="normal")
        self.pause_resume_button.configure(text="Pause", state="disabled")
        self.step_button.configure(state="disabled")
        self.enable_inputs()
        self.app = SchedulerApp()
        self.process_colors.clear()

    def clear_outputs(self):
        self.gantt_canvas.delete("all")
        self.draw_initial_gantt_layout()
        self.results_tree.delete(*self.results_tree.get_children())
        self.results_tree_items.clear()
        self.summary_label_vars["Total Power Used"].set("N/A")
        self.summary_label_vars["Current Time"].set("0")

    def disable_inputs(self):
        for frame in [self.input_frame, self.control_frame]:
            for widget in frame.winfo_children():
                if widget not in [self.start_button, self.pause_resume_button, self.step_button, self.reset_button]:
                    try:
                        widget.configure(state="disabled")
                    except:
                        pass
                if isinstance(widget, (ctk.CTkFrame)):
                    for child in widget.winfo_children():
                        try:
                            child.configure(state="disabled")
                        except:
                            pass

    def enable_inputs(self):
        for frame in [self.input_frame, self.control_frame]:
            for widget in frame.winfo_children():
                if widget not in [self.start_button, self.pause_resume_button, self.step_button, self.reset_button]:
                    try:
                        widget.configure(state="normal")
                    except:
                        pass
                if isinstance(widget, (ctk.CTkFrame)):
                    for child in widget.winfo_children():
                        try:
                            if isinstance(child, ctk.CTkComboBox):
                                child.configure(state="readonly")
                            else:
                                child.configure(state="normal")
                        except:
                            pass
                if widget == self.rr_quantum_entry:
                    is_rr = self.scheduler_var.get() == SchedulerType.RR.name
                    widget.configure(state="normal" if is_rr else "disabled")

    def start_simulation(self):
        if self.simulation_running:
            return
        self.clear_outputs()
        self.app = SchedulerApp()
        selected_scheduler_name = self.scheduler_var.get()
        try:
            self.app.scheduler_type = SchedulerType[selected_scheduler_name]
        except KeyError:
            messagebox.showerror("오류", f"알 수 없는 스케줄러 타입: {selected_scheduler_name}")
            return
        time_quantum = None
        if self.app.scheduler_type == SchedulerType.RR:
            try:
                quantum_str = self.rr_quantum_entry.get()
                if not quantum_str:
                    messagebox.showerror("입력 필요", "RR은 Time Quantum 값이 필요합니다.")
                    return
                time_quantum = int(quantum_str)
                if time_quantum <= 0:
                    raise ValueError("Time Quantum은 양수여야 합니다.")
            except ValueError as e:
                messagebox.showerror("입력 오류", f"잘못된 Time Quantum 값: {e}")
                return
        if not self.process_data:
            messagebox.showwarning("입력 필요", "적어도 하나 이상의 프로세스를 추가해야 합니다.")
            return
        for p_data in self.process_data:
            self.app.add_process(**p_data)
        if not self.processor_data:
            messagebox.showwarning("입력 필요", "적어도 하나 이상의 프로세서를 추가해야 합니다.")
            return
        for i, proc_data in enumerate(self.processor_data):
            q_for_processor = time_quantum if self.app.scheduler_type == SchedulerType.RR else None
            self.app.add_processor(id=proc_data['id'], type=proc_data['type'], time_quantum=q_for_processor)
            if self.app.scheduler_type == SchedulerType.RR:
                self.processor_data[i]['quantum'] = q_for_processor
        try:
            self.app.select_scheduler()
            self.prepare_results_table(self.app.scheduler.processes)
            self.draw_initial_gantt_layout()
        except Exception as e:
            messagebox.showerror("초기화 오류", f"스케줄러 초기화 실패: {e}")
            self.reset_all()
            return
        self.simulation_running = True
        self.simulation_paused = False
        self.disable_inputs()
        self.start_button.configure(state="disabled")
        self.pause_resume_button.configure(text="Pause", state="normal")
        self.step_button.configure(state="normal")
        self.simulation_step()

    def toggle_pause_simulation(self):
        if not self.simulation_running:
            return
        self.simulation_paused = not self.simulation_paused
        if self.simulation_paused:
            self.pause_resume_button.configure(text="Resume")
            if self.current_after_id:
                self.after_cancel(self.current_after_id)
                self.current_after_id = None
        else:
            self.pause_resume_button.configure(text="Pause")
            self.step_button.configure(state="normal")
            self.current_after_id = self.after(self.simulation_speed_ms, self.simulation_step)

    def step_simulation(self):
        if not self.simulation_running:
            return
        if not self.simulation_paused:
            self.simulation_paused = True
            self.pause_resume_button.configure(text="Resume")
            if self.current_after_id:
                self.after_cancel(self.current_after_id)
            self.current_after_id = None
        self._execute_one_step()

    def _execute_one_step(self):
        scheduler = self.app.scheduler
        if scheduler.has_next():
            current_time = scheduler.current_time
            scheduler.update_ready_queue()
            scheduler.schedule()
            scheduler.assign_process()
            scheduler.power_off_idle_processors()
            scheduler.process_waiting_time_update()
            current_processes = scheduler.get_process()
            current_processors = scheduler.get_processors()
            current_power = scheduler.calculate_total_power()
            self.update_gantt_chart_live(current_processors, current_time)
            self.update_results_table_live(current_processes)
            self.update_summary_live(current_time, current_power)
            scheduler.update_current_time()
            return True
        else:
            self.simulation_finished()
            return False

    def simulation_step(self):
        if not self.simulation_running or self.simulation_paused:
            self.current_after_id = None
            return
        executed = self._execute_one_step()
        if executed and self.simulation_running and not self.simulation_paused:
            self.current_after_id = self.after(self.simulation_speed_ms, self.simulation_step)
        else:
            self.current_after_id = None

    def simulation_finished(self):
        self.simulation_running = False
        self.simulation_paused = False
        final_time = "N/A"
        total_power = 0.0
        if self.app and self.app.scheduler:
            final_processes = self.app.scheduler.get_process()
            final_processors = self.app.scheduler.get_processors()
            final_time = self.app.scheduler.current_time
            total_power = self.app.scheduler.calculate_total_power()
            self.update_results_table_live(final_processes)
            self.calculate_and_display_summary(total_power, final_time)
        else:
            self.calculate_and_display_summary(0.0, 0)
        self.start_button.configure(text="Start", state="normal")
        self.pause_resume_button.configure(text="Pause", state="disabled")
        self.step_button.configure(state="disabled")
        self.enable_inputs()
        if self.current_after_id:
            self.after_cancel(self.current_after_id)
            self.current_after_id = None
        ftime_display = final_time if final_time != "N/A" else 0
        messagebox.showinfo("시뮬레이션 완료", f"시뮬레이션이 시간 {ftime_display}에 종료되었습니다.")

    def draw_initial_gantt_layout(self):
        self.gantt_canvas.delete("all")
        self.process_colors.clear()
        num_processors = len(self.processor_data)
        canvas_height = self.gantt_header_height + (num_processors * (self.gantt_row_height + self.gantt_padding)) + self.gantt_padding
        if num_processors == 0:
            canvas_height = self.gantt_header_height + 30
        self.gantt_canvas.config(height=canvas_height)
        initial_drawing_width = 800
        scroll_width = self.gantt_label_width + initial_drawing_width + self.gantt_padding
        self.gantt_canvas.configure(scrollregion=(0, 0, scroll_width, canvas_height))
        drawing_width_available = initial_drawing_width
        max_initial_time = int(drawing_width_available / self.gantt_time_scale)
        max_initial_time = max(0, max_initial_time)
        time_axis_y = self.gantt_padding + self.gantt_header_height / 2
        grid_line_top = self.gantt_padding
        grid_line_bottom = canvas_height - self.gantt_padding
        for t in range(max_initial_time + 1):
            x = self.gantt_label_width + (t * self.gantt_time_scale)
            self.gantt_canvas.create_line(x, grid_line_top, x, grid_line_bottom, fill="lightgrey", dash=(2,2), tags="time_grid")
            if t % 5 == 0 or max_initial_time <= 20:
                self.gantt_canvas.create_text(x, time_axis_y, text=str(t), anchor="center", tags="time_label")
        label_x_pos = self.gantt_label_width - 5
        for i, processor_info in enumerate(self.processor_data):
            y_top = self.gantt_padding + self.gantt_header_height + i * (self.gantt_row_height + self.gantt_padding)
            label_y_center = y_top + self.gantt_row_height / 2
            self.gantt_canvas.create_text(label_x_pos, label_y_center - 6, text=f"CPU {processor_info['id']}", anchor="e", tags="proc_label", font=('Arial', 9))
            self.gantt_canvas.create_text(label_x_pos, label_y_center + 6, text=f"({processor_info['type']}-Core)", anchor="e", tags="proc_label", font=('Arial', 8))

    def update_gantt_chart_live(self, processors: list, current_time: int):
        if current_time == 0:
            return
        time_step = current_time - 1
        num_processors = len(self.processor_data)
        required_canvas_height = self.gantt_header_height + (num_processors * (self.gantt_row_height + self.gantt_padding)) + self.gantt_padding
        if num_processors == 0:
            required_canvas_height = self.gantt_header_height + 30
        if abs(self.gantt_canvas.winfo_reqheight() - required_canvas_height) > 1:
            self.gantt_canvas.config(height=required_canvas_height)
        required_total_width = self.gantt_label_width + (current_time * self.gantt_time_scale) + self.gantt_padding
        current_scroll_region = self.gantt_canvas.cget("scrollregion")
        if current_scroll_region:
            try:
                _, _, current_scroll_width, current_scroll_height = map(int, current_scroll_region.split())
            except ValueError:
                current_scroll_width = self.gantt_label_width + 800
                current_scroll_height = required_canvas_height
        else:
            current_scroll_width = self.gantt_label_width + 800
            current_scroll_height = required_canvas_height
        current_canvas_height = required_canvas_height
        width_changed = False
        if required_total_width > current_scroll_width:
            new_scroll_width = required_total_width + 200
            self.gantt_canvas.configure(scrollregion=(0, 0, new_scroll_width, current_canvas_height))
            start_t = int((current_scroll_width - self.gantt_label_width) / self.gantt_time_scale)
            end_t = int((new_scroll_width - self.gantt_label_width) / self.gantt_time_scale) + 1
            time_axis_y = self.gantt_padding + self.gantt_header_height / 2
            grid_line_top = self.gantt_padding
            grid_line_bottom = current_canvas_height - self.gantt_padding
            for t in range(start_t, end_t):
                x = self.gantt_label_width + (t * self.gantt_time_scale)
                self.gantt_canvas.create_line(x, grid_line_top, x, grid_line_bottom, fill="lightgrey", dash=(2,2), tags="time_grid")
                if t % 5 == 0:
                    self.gantt_canvas.create_text(x, time_axis_y, text=str(t), anchor="center", tags="time_label")
            current_scroll_width = new_scroll_width
            width_changed = True
        height_changed = False
        if abs(current_scroll_height - current_canvas_height) > 1:
            self.gantt_canvas.configure(scrollregion=(0, 0, current_scroll_width, current_canvas_height))
            height_changed = True
        visible_width = self.gantt_canvas.winfo_width()
        target_x_pos = self.gantt_label_width + (current_time * self.gantt_time_scale)
        if (width_changed or height_changed or (target_x_pos > visible_width + self.gantt_canvas.xview()[0] * current_scroll_width)) and current_scroll_width > 0:
            scroll_fraction = (target_x_pos - visible_width + 50) / current_scroll_width
            self.gantt_canvas.xview_moveto(min(max(0, scroll_fraction), 1.0))
        for i, processor in enumerate(processors):
            try:
                gui_proc_index = next(idx for idx, data in enumerate(self.processor_data) if data['id'] == processor.id)
            except StopIteration:
                continue
            y_top = self.gantt_padding + self.gantt_header_height + gui_proc_index * (self.gantt_row_height + self.gantt_padding)
            y_bottom = y_top + self.gantt_row_height
            pid_at_step = 0
            if time_step < len(processor.process_queue):
                pid_at_step = processor.process_queue[time_step] if processor.process_queue[time_step] is not None else 0
            pid = pid_at_step
            x_start = self.gantt_label_width + time_step * self.gantt_time_scale
            x_end = x_start + self.gantt_time_scale
            color = self.generate_color(pid)
            tag_name = f"t{time_step}_p{processor.id}"
            if pid != 0:
                self.gantt_canvas.create_rectangle(x_start, y_top + 1, x_end, y_bottom - 1, fill=color, outline="black", width=1, tags=(tag_name, "block"))
                if self.gantt_time_scale > 18:
                    text_color = "white" if sum(int(color[i:i+2], 16) for i in (1,3,5)) < 384 else "black"
                    self.gantt_canvas.create_text(x_start + self.gantt_time_scale / 2, y_top + self.gantt_row_height / 2, text=str(pid), fill=text_color, font=('Arial', 8, 'bold'), tags=(tag_name, "block_text"))

    def prepare_results_table(self, initial_processes: list):
        self.results_tree.delete(*self.results_tree.get_children())
        self.results_tree_items.clear()
        initial_processes.sort(key=lambda p: p.pid)
        for p in initial_processes:
            item_id = self.results_tree.insert("", "end", values=(p.pid, p.arrival, p.burst, p.remaining_time, "-", "-", "-", "-"))
            self.results_tree_items[p.pid] = item_id

    def update_results_table_live(self, current_processes: list):
        for p in current_processes:
            if p.pid in self.results_tree_items:
                item_id = self.results_tree_items[p.pid]
                st = p.start_time if p.start_time is not None else "-"
                wt = p.wait_time
                tt = p.turnaround_time if p.turnaround_time is not None else "-"
                ntt = f"{p.normalized_turnaround_time:.3f}" if p.normalized_turnaround_time is not None else "-"
                remain = p.remaining_time
                self.results_tree.item(item_id, values=(p.pid, p.arrival, p.burst, remain, st, wt, tt, ntt))

    def update_summary_live(self, current_time: int, current_power: float):
        self.summary_label_vars["Current Time"].set(str(current_time))
        self.summary_label_vars["Total Power Used"].set(f"{current_power:.2f}")

    def calculate_and_display_summary(self, total_power: float, final_time: int):
        self.summary_label_vars["Current Time"].set(str(final_time))
        self.summary_label_vars["Total Power Used"].set(f"{total_power:.2f}")

if __name__ == "__main__":
    app_gui = SchedulerGUI2()
    app_gui.mainloop()