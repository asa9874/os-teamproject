import customtkinter as ctk
import tkinter.ttk as ttk
from simulator import SchedulerType
from tkinter import messagebox
#from visualization.gui2 import SchedulerGUI2

MAX_PROCESSES = 15
MAX_PROCESSORS = 4
class InputManager:
    def __init__(self, app):
        self.app = app
    
    def add_process(self):
        app = self.app
        if app.simulation_running:
            messagebox.showwarning("실행 중", "시뮬레이션 중에는 프로세스를 추가할 수 없습니다.")
            return
        if len(app.process_data) >= MAX_PROCESSES:
            messagebox.showwarning("개수 초과", f"최대 {MAX_PROCESSES}개의 프로세스만 추가할 수 있습니다.")
            return
        try:
            pid = self.get_unique_pid()
            arrival = int(app.arrival_entry.get())
            burst = int(app.burst_entry.get())
            if arrival < 0 or burst <= 0:
                raise ValueError("Arrival은 0 이상, Burst는 0 보다 커야 합니다.")
            app.process_tree.insert("", "end", values=(pid, arrival, burst))
            app.process_data.append({'pid': pid, 'arrival': arrival, 'burst': burst})
            app.arrival_entry.delete(0, "end")
            app.burst_entry.delete(0, "end")
            app.arrival_entry.focus()
            app.update_list_counts()
        except ValueError as e:
            messagebox.showerror("입력 오류", f"잘못된 프로세스 정보입니다: {e}")

    def remove_process(self):
        app = self.app
        if app.simulation_running:
            messagebox.showwarning("실행 중", "시뮬레이션 중에는 프로세스를 제거할 수 없습니다.")
            return
        selected_items = app.process_tree.selection()
        if not selected_items:
            return
        if messagebox.askyesno("삭제 확인", "선택된 프로세스를 삭제하시겠습니까?"):
            pids_to_remove = [int(app.process_tree.item(item, 'values')[0]) for item in selected_items]
            app.process_data = [p for p in app.process_data if p['pid'] not in pids_to_remove]
            for item in selected_items:
                app.process_tree.delete(item)
            app.update_list_counts()

    def add_processor(self):
        app = self.app
        if app.simulation_running:
            messagebox.showwarning("실행 중", "시뮬레이션 중에는 프로세서를 추가할 수 없습니다.")
            return
        if len(app.processor_data) >= MAX_PROCESSORS:
            messagebox.showwarning("개수 초과", f"최대 {MAX_PROCESSORS}개의 프로세서만 추가할 수 있습니다.")
            return
        proc_id = self.get_unique_processor_id()
        proc_type = app.proc_type_var.get().upper()
        if proc_type not in ['P', 'E']:
            raise ValueError("프로세서 타입은 'P' 또는 'E' 여야 합니다.")
        app.processor_tree.insert("", "end", values=(proc_id, proc_type))
        app.processor_data.append({'id': proc_id, 'type': proc_type, 'quantum': None})
        app.gantt.draw_initial_gantt_layout()
        app.update_list_counts()

    def remove_processor(self):
        app = self.app
        if app.simulation_running:
            messagebox.showwarning("실행 중", "시뮬레이션 중에는 프로세서를 제거할 수 없습니다.")
            return
        selected_items = app.processor_tree.selection()
        if not selected_items:
            return
        if messagebox.askyesno("삭제 확인", "선택된 프로세서를 삭제하시겠습니까?"):
            ids_to_remove = [int(app.processor_tree.item(item, 'values')[0]) for item in selected_items]
            app.processor_data = [p for p in app.processor_data if p['id'] not in ids_to_remove]
            for item in selected_items:
                app.processor_tree.delete(item)
            app.gantt.draw_initial_gantt_layout()
            app.update_list_counts()

    def get_unique_pid(self):
        app = self.app
        existing_pids = {int(app.process_tree.item(item, 'values')[0]) for item in app.process_tree.get_children()}
        return max(existing_pids, default=0) + 1

    def get_unique_processor_id(self):
        app = self.app
        existing_ids = {int(app.processor_tree.item(item, 'values')[0]) for item in app.processor_tree.get_children()}
        return max(existing_ids, default=0) + 1