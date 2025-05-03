import customtkinter as ctk
import tkinter.ttk as ttk
from simulator import SchedulerType

class WidgetManager:
    def __init__(self, app ):
        self.app = app  # 부모 클래스 인스턴스를 전달받음
        
        app.control_frame = ctk.CTkFrame(app, fg_color="transparent", corner_radius=0)
        app.control_frame.pack(side="top", fill="x", padx=5, pady=5)

        # 좌우 분할용
        app.main_pane = ttk.PanedWindow(app, orient="horizontal")
        app.main_pane.pack(fill="both", expand=True)

        # 입력 프레임 (좌측)
        app.input_frame = ctk.CTkFrame(app.main_pane, corner_radius=8)
        app.main_pane.add(app.input_frame, weight=0)

        # 출력 프레임 (우측)
        app.output_container_frame = ctk.CTkFrame(app.main_pane, corner_radius=8)
        app.main_pane.add(app.output_container_frame, weight=3)
        

    def setup(self):
        self.setup_control_widgets()
        self.setup_input_widgets()
        self.setup_output_widgets()
    
    def setup_control_widgets(self):
        app = self.app  

        # 알고리즘 선택
        ctk.CTkLabel(app.control_frame, text="Algorithm:").pack(side="left", padx=(0,2))
        scheduler_names = [s.name for s in SchedulerType]
        app.scheduler_var = ctk.StringVar(value=scheduler_names[0])
        app.scheduler_combo = ctk.CTkComboBox(
            app.control_frame,
            values=scheduler_names,
            variable=app.scheduler_var,
            width=100,
            command=self.update_rr_quantum_visibility
        )
        app.scheduler_combo.pack(side="left", padx=(0,10))

        # RR용 타임 퀀텀
        app.rr_quantum_label = ctk.CTkLabel(app.control_frame, text="Time Quantum:")
        app.rr_quantum_entry = ctk.CTkEntry(app.control_frame, width=50)

        # 시뮬레이션 제어 버튼들
        app.start_button = ctk.CTkButton(app.control_frame, text="Start", command=app.simulation.start_simulation, width=70)
        app.start_button.pack(side="left", padx=(10,2))

        app.pause_resume_button = ctk.CTkButton(app.control_frame, text="Pause", command=app.simulation.toggle_pause_simulation, width=70, state="disabled")
        app.pause_resume_button.pack(side="left", padx=2)

        app.step_button = ctk.CTkButton(app.control_frame, text="Step", command=app.simulation.step_simulation, width=50, state="disabled")
        app.step_button.pack(side="left", padx=2)

        app.reset_button = ctk.CTkButton(app.control_frame, text="Reset", command=app.reset_all, width=60)
        app.reset_button.pack(side="left", padx=(10,2))

        # 속도 조절
        app.speed_label_var = ctk.StringVar(value=f"{app.simulation_speed_ms} ms")
        ctk.CTkLabel(app.control_frame, textvariable=app.speed_label_var, width=70).pack(side="right", padx=(0,5))
        app.speed_scale = ctk.CTkSlider(app.control_frame, from_=50, to=500, command=app.update_speed, width=120)
        app.speed_scale.set(app.simulation_speed_ms)
        app.speed_scale.pack(side="right", padx=2)
        ctk.CTkLabel(app.control_frame, text="Speed:").pack(side="right", padx=0)

        # RR용 퀀텀 조건부 표시
        self.update_rr_quantum_visibility()

    def setup_input_widgets(self):
        app = self.app  
        
        input_content_frame = ctk.CTkFrame(app.input_frame)
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
        app.arrival_entry = ctk.CTkEntry(process_input_frame, width=50)
        app.arrival_entry.grid(row=0, column=1, padx=5, pady=(5,2), sticky="ew")
        ctk.CTkLabel(process_input_frame, text="Burst:").grid(row=1, column=0, padx=5, pady=(2,5), sticky="w")
        app.burst_entry = ctk.CTkEntry(process_input_frame, width=50)
        app.burst_entry.grid(row=1, column=1, padx=5, pady=(2,5), sticky="ew")
        app.add_process_button = ctk.CTkButton(process_input_frame, text="Add", command=app.input.add_process, width=60)
        app.add_process_button.grid(row=0, column=2, rowspan=2, padx=10, pady=5, sticky="ns")
        process_input_frame.grid_columnconfigure(1, weight=1)

        # 프로세스 목록 (ttk.Treeview 사용)
        process_list_header = ctk.CTkLabel(process_section_frame, text="Processes", font=("Arial", 12, "bold"))
        process_list_header.pack(pady=(5,0), anchor="w", padx=5)
        app.process_list_labelframe = ctk.CTkFrame(process_section_frame)
        app.process_list_labelframe.pack(pady=5, fill="x", padx=5)
        app.process_tree = ttk.Treeview(app.process_list_labelframe, columns=("pid", "arrival", "burst"), show="headings", height=6)
        app.process_tree.heading("pid", text="PID")
        app.process_tree.column("pid", width=40, minwidth=30, anchor="center")
        app.process_tree.heading("arrival", text="Arrival")
        app.process_tree.column("arrival", width=50, minwidth=40, anchor="center")
        app.process_tree.heading("burst", text="Burst")
        app.process_tree.column("burst", width=50, minwidth=40, anchor="center")
        process_scrollbar = ttk.Scrollbar(app.process_list_labelframe, orient="vertical", command=app.process_tree.yview)
        app.process_tree.configure(yscrollcommand=process_scrollbar.set)
        process_scrollbar.pack(side="right", fill="y")
        app.process_tree.pack(side="left", fill="x", expand=True)
        app.remove_process_button = ctk.CTkButton(process_section_frame, text="Remove Selected Process", command=app.input.remove_process)
        app.remove_process_button.pack(pady=(0,5), padx=5)

        # 프로세서 입력
        processor_section_frame = ctk.CTkFrame(input_content_frame)
        processor_section_frame.pack(side="top", fill="x", padx=5)
        processor_input_header = ctk.CTkLabel(processor_section_frame, text="Add Processor", font=("Arial", 12, "bold"))
        processor_input_header.pack(pady=(5,0), anchor="w")
        processor_input_frame = ctk.CTkFrame(processor_section_frame, corner_radius=8, width=400, height=80)
        processor_input_frame.pack(pady=5, fill="x")
        processor_input_frame.pack_propagate(False)  # 지정한 width, height 유지

        ctk.CTkLabel(processor_input_frame, text="Type:").grid(row=0, column=0, padx=5, pady=(10,2), sticky="w")
        app.proc_type_var = ctk.StringVar(value="P")
        proc_type_p = ctk.CTkRadioButton(processor_input_frame, text="P-Core", variable=app.proc_type_var, value="P")
        proc_type_e = ctk.CTkRadioButton(processor_input_frame, text="E-Core", variable=app.proc_type_var, value="E")
        proc_type_p.grid(row=0, column=1, padx=5, pady=(10,2), sticky="w")
        proc_type_e.grid(row=1, column=1, padx=5, pady=(2,10), sticky="w")
        app.add_processor_button = ctk.CTkButton(processor_input_frame, text="Add", command=app.input.add_processor, width=60)
        app.add_processor_button.grid(row=0, column=2, rowspan=2, padx=10, pady=5, sticky="ns")
        processor_input_frame.grid_columnconfigure(1, weight=1)

        processor_list_header = ctk.CTkLabel(processor_section_frame, text="Processors", font=("Arial", 12, "bold"))
        processor_list_header.pack(pady=(5,0), anchor="w")
        app.processor_list_labelframe = ctk.CTkFrame(processor_section_frame)
        app.processor_list_labelframe.pack(pady=5, fill="x")
        app.processor_tree = ttk.Treeview(app.processor_list_labelframe, columns=("id", "type"), show="headings", height=4)
        app.processor_tree.heading("id", text="ID")
        app.processor_tree.column("id", width=50, minwidth=40, anchor="center")
        app.processor_tree.heading("type", text="Type")
        app.processor_tree.column("type", width=70, minwidth=50, anchor="center")
        processor_scrollbar = ttk.Scrollbar(app.processor_list_labelframe, orient="vertical", command=app.processor_tree.yview)
        app.processor_tree.configure(yscrollcommand=processor_scrollbar.set)
        processor_scrollbar.pack(side="right", fill="y")
        app.processor_tree.pack(side="left", fill="x", expand=True)
        app.remove_processor_button = ctk.CTkButton(processor_section_frame, text="Remove Selected Processor", command=app.input.remove_processor)
        app.remove_processor_button.pack(pady=(0,5))

    def setup_output_widgets(self):
        app = self.app
        
        # 간트 차트 영역
        gantt_header = ctk.CTkLabel(app.output_container_frame, text="Gantt Chart", font=("Arial", 12, "bold"))
        gantt_header.pack(pady=(5,0), anchor="w", padx=5)
        gantt_frame = ctk.CTkFrame(app.output_container_frame)  # padx, pady 제거
        gantt_frame.pack(side="top", fill="x", padx=5, pady=5)  # pack()에서 패딩 지정
        app.gantt_canvas = ctk.CTkCanvas(gantt_frame, bg="white", height=100, highlightthickness=0)
        gantt_hbar = ttk.Scrollbar(gantt_frame, orient="horizontal", command=app.gantt_canvas.xview)
        gantt_hbar.pack(side="bottom", fill="x")
        app.gantt_canvas.configure(xscrollcommand=gantt_hbar.set)
        app.gantt_canvas.pack(fill="x", expand=True)
        app.gantt.draw_initial_gantt_layout()

        # 결과 테이블 영역
        results_header = ctk.CTkLabel(app.output_container_frame, text="Results Table", font=("Arial", 12, "bold"))
        results_header.pack(pady=(5,0), anchor="w", padx=5)
        results_frame = ctk.CTkFrame(app.output_container_frame)  # padx, pady 제거
        results_frame.pack(side="top", fill="both", expand=True, padx=5, pady=(0,5))  # pack()에서 패딩 지정
        columns = ("pid", "arrival", "burst", "remain", "start", "wait", "turnaround", "ntt")
        app.results_tree = ttk.Treeview(
            results_frame,
            columns=columns,
            show="headings",
            height=5
        )
        app.results_tree.heading("pid", text="PID")
        app.results_tree.heading("arrival", text="arrival")
        app.results_tree.heading("burst", text="burst")
        app.results_tree.heading("remain", text="remain")
        app.results_tree.heading("start", text="start")
        app.results_tree.heading("wait", text="wait")
        app.results_tree.heading("turnaround", text="turnaround")
        app.results_tree.heading("ntt", text="NTT")
        for col in columns:
            app.results_tree.column(col, width=120, stretch=False)
            app.results_tree.heading(col, text=col.capitalize())
        
        # ... (Treeview 설정 코드)
        results_scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=app.results_tree.yview)
        app.results_tree.configure(yscrollcommand=results_scrollbar.set)
        results_scrollbar.pack(side="right", fill="y")
        app.results_tree.pack(side="left", fill="both", expand=True)
        app.results_tree_items = {}

        # 요약 정보 영역
        summary_frame = ctk.CTkFrame(app.output_container_frame)  # padx, pady 제거
        summary_frame.pack(side="bottom", fill="x", padx=5, pady=2)  # pack()에서 패딩 지정
        app.summary_label_vars = {}
        ctk.CTkLabel(summary_frame, text="Elapsed Time:", font=("Arial", 10, "bold")).pack(side="left", padx=(5,2))
        time_var = ctk.StringVar(value="0")
        app.summary_label_vars["Current Time"] = time_var
        ctk.CTkLabel(summary_frame, textvariable=time_var, font=("Arial", 10), width=50).pack(side="left", padx=(0,10))
        ctk.CTkLabel(summary_frame, text="Total Power Used:", font=("Arial", 10, "bold")).pack(side="left", padx=(5,2))
        power_var = ctk.StringVar(value="N/A")
        app.summary_label_vars["Total Power Used"] = power_var
        ctk.CTkLabel(summary_frame, textvariable=power_var, font=("Arial", 10)).pack(side="left", padx=(0,5))

    def update_rr_quantum_visibility(self, event=None):
        app = self.app
        selected_scheduler = app.scheduler_var.get()
        is_rr = selected_scheduler == SchedulerType.RR.name
        print(f"Selected Scheduler: {selected_scheduler}, Is RR: {is_rr}")

        if is_rr:
            if not app.rr_quantum_label.winfo_ismapped():
                app.rr_quantum_entry.pack(side="left", padx=(0, 10), before=app.start_button)
                app.rr_quantum_label.pack(side="left", padx=(0, 2), before=app.rr_quantum_entry)
            if not app.rr_quantum_entry.get():
                app.rr_quantum_entry.insert(0, "4")
        else:
            if app.rr_quantum_label.winfo_ismapped():
                app.rr_quantum_label.pack_forget()
            if app.rr_quantum_entry.winfo_ismapped():
                app.rr_quantum_entry.pack_forget()


    def disable_inputs(self):
        app = self.app
        for frame in [app.input_frame, app.control_frame]:
            for widget in frame.winfo_children():
                if widget not in [app.start_button, app.pause_resume_button, app.step_button, app.reset_button]:
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
        app = self.app
        for frame in [app.input_frame, app.control_frame]:
            for widget in frame.winfo_children():
                if widget not in [app.start_button, app.pause_resume_button, app.step_button, app.reset_button]:
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
                if widget == app.rr_quantum_entry:
                    is_rr = app.scheduler_var.get() == SchedulerType.RR.name
                    widget.configure(state="normal" if is_rr else "disabled")
