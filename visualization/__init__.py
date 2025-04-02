from tkinter import *
from tkinter import ttk

# from core.process import Process
# from core.processor import Processor
# from algorithm.custom_scheduler import MyScheduler


import tkinter as tk
from tkinter import ttk

class ProcessSchedulingSimulator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Process Scheduling Simulator")
        self.geometry("1200x700")  # 창 크기는 상황에 맞게 조절

        # 폰트, 스타일 설정 (필요에 따라 추가/수정)
        style = ttk.Style()
        style.theme_use("default")
        
        # 상단 제목 라벨
        self.create_title_frame()

        # 좌측 상단: 프로세스 입력 영역 (프로세스 목록 테이블 + 입력 필드 + 추가 버튼)
        self.create_process_input_frame()

        # 우측 상단: 스케줄링 알고리즘 선택, 타이머, RUN 버튼
        self.create_control_frame()

        # 중앙(또는 우측 하단) 영역: 프로세서/코어 상태 표시 + Ready Queue 표시
        self.create_processor_frame()

        # 하단 영역: 결과 테이블, 간트 차트
        self.create_result_frame()
        self.create_gantt_chart_frame()

    def create_title_frame(self):
        """상단에 제목/로고/버전 정보 등을 표시하는 프레임."""
        title_frame = ttk.Frame(self)
        title_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # 학교 로고나 이름 (예시: 한국기술교육대학교)
        # 이미지를 삽입하려면 PhotoImage 등을 사용하면 됩니다. 여기서는 텍스트로 대체
        uni_label = ttk.Label(title_frame, text="한국기술교육대학교", font=("Arial", 16, "bold"))
        uni_label.pack(side=tk.LEFT, padx=10)

        # 타이틀
        sim_label = ttk.Label(title_frame, text="Process Scheduling Simulator (Ver 1.0)", font=("Arial", 14))
        sim_label.pack(side=tk.LEFT, padx=10)

    def create_process_input_frame(self):
        """프로세스 목록과 입력 필드를 담는 프레임."""
        process_frame = ttk.LabelFrame(self, text="Processes (15)")
        process_frame.place(x=10, y=60, width=400, height=350)

        # 트리뷰(프로세스 목록) 설정
        columns = ("p_name", "arrival_time", "workload")
        self.process_tree = ttk.Treeview(process_frame, columns=columns, show="headings", height=10)
        self.process_tree.heading("p_name", text="P Name")
        self.process_tree.heading("arrival_time", text="AT")
        self.process_tree.heading("workload", text="Workload")
        self.process_tree.column("p_name", width=80, anchor=tk.CENTER)
        self.process_tree.column("arrival_time", width=80, anchor=tk.CENTER)
        self.process_tree.column("workload", width=80, anchor=tk.CENTER)
        self.process_tree.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # 프로세스 입력 필드
        input_frame = ttk.Frame(process_frame)
        input_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        ttk.Label(input_frame, text="P Name").grid(row=0, column=0, padx=2, pady=2)
        self.entry_pname = ttk.Entry(input_frame, width=8)
        self.entry_pname.grid(row=0, column=1, padx=2, pady=2)

        ttk.Label(input_frame, text="AT").grid(row=0, column=2, padx=2, pady=2)
        self.entry_at = ttk.Entry(input_frame, width=5)
        self.entry_at.grid(row=0, column=3, padx=2, pady=2)

        ttk.Label(input_frame, text="Workload").grid(row=0, column=4, padx=2, pady=2)
        self.entry_workload = ttk.Entry(input_frame, width=5)
        self.entry_workload.grid(row=0, column=5, padx=2, pady=2)

        # 추가 버튼
        add_button = ttk.Button(input_frame, text="Add", command=self.add_process)
        add_button.grid(row=0, column=6, padx=5, pady=2)

    def create_control_frame(self):
        """스케줄링 알고리즘 선택, 타이머, RUN 버튼이 들어가는 프레임."""
        control_frame = ttk.Frame(self)
        control_frame.place(x=420, y=60, width=350, height=80)

        # 알고리즘 선택
        ttk.Label(control_frame, text="Algorithm =").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.alg_combobox = ttk.Combobox(control_frame, values=["FCFS", "SJF", "SRTN", "RR", "Priority"])
        self.alg_combobox.current(2)  # 기본값을 SRTN 등으로 설정
        self.alg_combobox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        # 시간 표시
        self.time_label = ttk.Label(control_frame, text="Time = 0s", font=("Arial", 12))
        self.time_label.grid(row=0, column=2, padx=10, pady=5)

        # RUN 버튼
        run_button = ttk.Button(control_frame, text="RUN!!!", command=self.run_simulation)
        run_button.grid(row=0, column=3, padx=5, pady=5)

    def create_processor_frame(self):
        """프로세서 및 코어 상태, Ready Queue 등을 표시하는 프레임."""
        processor_frame = ttk.LabelFrame(self, text="Processors / Ready Queue")
        processor_frame.place(x=420, y=150, width=350, height=260)

        # 프로세서 상태 표시 (예시: 4코어)
        # 실제로 2 P-Cores, 2 E-Cores 등 구분하여 표현하려면 더 복잡하게 구성 가능
        core_frame = ttk.Frame(processor_frame)
        core_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        ttk.Label(core_frame, text="Processor 0 (4 Cores or 2 P-Cores and 2 E-Cores)").pack(side=tk.TOP, anchor=tk.W)

        self.core_vars = []
        for i in range(4):
            var = tk.BooleanVar(value=False)
            self.core_vars.append(var)
            chk = ttk.Checkbutton(core_frame, text=f"Core {i} (OFF)", variable=var,
                                  command=lambda idx=i: self.toggle_core(idx))
            chk.pack(side=tk.LEFT, padx=5)

        # Ready Queue 표시
        ready_frame = ttk.Frame(processor_frame)
        ready_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        ttk.Label(ready_frame, text="Ready Queue:").pack(side=tk.LEFT)
        self.ready_queue_label = ttk.Label(ready_frame, text="[]", relief=tk.SUNKEN, width=25)
        self.ready_queue_label.pack(side=tk.LEFT, padx=5)

        # 평균 활용도, Idle Time 등 (필요시)
        info_frame = ttk.Frame(processor_frame)
        info_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.util_label = ttk.Label(info_frame, text="Avg utilization: 0%")
        self.util_label.pack(side=tk.LEFT, padx=5)
        self.idle_label = ttk.Label(info_frame, text="Idle time: 0s")
        self.idle_label.pack(side=tk.LEFT, padx=5)

    def create_result_frame(self):
        """결과 테이블을 표시하는 프레임."""
        result_frame = ttk.LabelFrame(self, text="Result (각 프로세스의 WT, TT, NTT 등)")
        result_frame.place(x=10, y=420, width=760, height=270)

        columns = ("p_name", "at", "wt", "tt", "ntt")
        self.result_tree = ttk.Treeview(result_frame, columns=columns, show="headings", height=8)
        self.result_tree.heading("p_name", text="P Name")
        self.result_tree.heading("at", text="AT")
        self.result_tree.heading("wt", text="WT")
        self.result_tree.heading("tt", text="TT")
        self.result_tree.heading("ntt", text="NTT")
        for col in columns:
            self.result_tree.column(col, width=80, anchor=tk.CENTER)
        self.result_tree.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, pady=5)

        # 스크롤바 (필요시)
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_tree.yview)
        self.result_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_gantt_chart_frame(self):
        """간트 차트 영역."""
        gantt_frame = ttk.LabelFrame(self, text="Gantt Chart")
        gantt_frame.place(x=780, y=420, width=400, height=270)

        # 예시로 Canvas를 사용해서 간트 차트를 표시할 수 있음
        self.gantt_canvas = tk.Canvas(gantt_frame, bg="white")
        self.gantt_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        # 실제 간트 차트는 스케줄링 결과에 따라 draw_rectangle 등으로 표현하면 됨

    def add_process(self):
        """프로세스 입력값을 트리뷰에 추가하는 함수."""
        p_name = self.entry_pname.get()
        at = self.entry_at.get()
        workload = self.entry_workload.get()
        
        if p_name and at.isdigit() and workload.isdigit():
            self.process_tree.insert("", tk.END, values=(p_name, at, workload))
            # 입력 칸 초기화
            self.entry_pname.delete(0, tk.END)
            self.entry_at.delete(0, tk.END)
            self.entry_workload.delete(0, tk.END)

    def run_simulation(self):
        """RUN 버튼 눌렀을 때 스케줄링 수행 로직을 여기에 구현."""
        print("Simulation started!")
        # 여기에서 스케줄링 알고리즘 수행, 결과 테이블/간트 차트 업데이트 등 구현
        # 예시로 시간 갱신:
        self.time_label.config(text="Time = 0s (Running...)")

    def toggle_core(self, idx):
        """코어 체크박스 ON/OFF에 따라 라벨을 바꾼다."""
        var = self.core_vars[idx]
        # OFF->ON, ON->OFF 식으로 텍스트 변경
        # 실제로 코어가 동작하는지 안 하는지는 별도 로직
        if var.get():
            # 체크됨
            text = f"Core {idx} (ON)"
        else:
            text = f"Core {idx} (OFF)"
        # 체크박스 위젯을 찾아서 텍스트 업데이트 (단순히 command에서만은 어렵기 때문에 다른 방식으로)
        # 체크박스가 많지 않으니, 간단히 자식 위젯 순회:
        parent = var._root()  # 이건 보통 root 객체, 여기서는 프레임
        # 더 간단히는 create_processor_frame에서 체크박스를 리스트에 저장해서 업데이트 가능
        # 여기서는 일단 pass
        # 실제로는 체크박스를 리스트로 가지고 있다면: self.checkboxes[idx].config(text=text)
        # 라고 하면 됨.
        # 이 예시에서는 보여드리기만 하고 넘어갑니다.
        print(text)


if __name__ == "__main__":
    app = ProcessSchedulingSimulator()
    app.mainloop()
