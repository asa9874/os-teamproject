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
from visualization.widgetbuilder import WidgetBuilder
from visualization.inputmanager import InputManager
from visualization.gantt import GanttManager

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
        
        # 위젯
        self.widget_builder = WidgetBuilder(self)
        
        # 입력관련
        self.input = InputManager(self)
        
        # 간트관련
        self.gantt = GanttManager(self)
        
        # 위젯,틀 생성
        self.widget_builder.setup()

        # 프로세스, 프로세서 목록 라벨 초기화
        self.update_list_counts()

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
        self.gantt.draw_initial_gantt_layout()
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
            self.gantt.draw_initial_gantt_layout()
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
            self.gantt.update_gantt_chart_live(current_processors, current_time)
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