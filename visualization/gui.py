import customtkinter as ctk
from tkinter import messagebox
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from simulator import SchedulerApp
from visualization.widgetmanager import WidgetManager
from visualization.inputmanager import InputManager
from visualization.ganttmanager import GanttManager
from visualization.simuationmanager import SimulationManager

# 상수 정의
MAX_PROCESSES = 15
MAX_PROCESSORS = 4
""" 
pip install customtkinter 한후에 실행가능
"""
class SchedulerGUI(ctk.CTk):
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
        
        # 위젯
        self.widget = WidgetManager(self)
        
        # 입력관련
        self.input = InputManager(self)
        
        # 간트관련
        self.gantt = GanttManager(self)
        
        # 시뮬레이션 관련
        self.simulation = SimulationManager(self)
        
        # 위젯,틀 생성
        self.widget.setup()

        # 프로세스, 프로세서 목록 라벨 초기화
        self.update_list_counts()

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
            self.gantt.draw_initial_gantt_layout()
            self.update_list_counts()

    def update_speed(self, value):
        new_speed = int(float(value))
        speed_changed = new_speed != self.simulation_speed_ms
        self.simulation_speed_ms = new_speed
        self.speed_label_var.set(f"{self.simulation_speed_ms} ms")
        if speed_changed and self.simulation_running and not self.simulation_paused:
            if self.current_after_id:
                self.after_cancel(self.current_after_id)
            self.current_after_id = self.after(self.simulation_speed_ms, self.simulation.simulation_step)

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
        self.widget.update_rr_quantum_visibility()
        self.speed_scale.set(300)
        self.update_speed(300)
        self.update_list_counts()
        self.clear_outputs()
        self.start_button.configure(text="Start", state="normal")
        self.pause_resume_button.configure(text="Pause", state="disabled")
        self.step_button.configure(state="disabled")
        self.widget.enable_inputs()
        self.app = SchedulerApp()
        self.process_colors.clear()

    def clear_outputs(self):
        self.gantt_canvas.delete("all")
        self.gantt.draw_initial_gantt_layout()
        self.results_tree.delete(*self.results_tree.get_children())
        self.results_tree_items.clear()
        self.summary_label_vars["Total Power Used"].set("N/A")
        self.summary_label_vars["Current Time"].set("0")

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
    app_gui = SchedulerGUI()
    app_gui.mainloop()