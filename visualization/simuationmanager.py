import customtkinter as ctk
import tkinter.ttk as ttk
from simulator import SchedulerType
from tkinter import messagebox
from simulator import SchedulerApp, SchedulerType


class SimulationManager:
    def __init__(self, app):
        self.app = app
    
    def start_simulation(self):
        app = self.app
        if app.simulation_running:
            return
        app.clear_outputs()
        app.app = SchedulerApp()
        selected_scheduler_name = app.scheduler_var.get()
        try:
            app.app.scheduler_type = SchedulerType[selected_scheduler_name]
        except KeyError:
            messagebox.showerror("오류", f"알 수 없는 스케줄러 타입: {selected_scheduler_name}")
            return
        time_quantum = None
        if app.app.scheduler_type == SchedulerType.RR:
            try:
                quantum_str = app.rr_quantum_entry.get()
                if not quantum_str:
                    messagebox.showerror("입력 필요", "RR은 Time Quantum 값이 필요합니다.")
                    return
                time_quantum = int(quantum_str)
                if time_quantum <= 0:
                    raise ValueError("Time Quantum은 양수여야 합니다.")
            except ValueError as e:
                messagebox.showerror("입력 오류", f"잘못된 Time Quantum 값: {e}")
                return
        if not app.process_data:
            messagebox.showwarning("입력 필요", "적어도 하나 이상의 프로세스를 추가해야 합니다.")
            return
        for p_data in app.process_data:
            app.app.add_process(**p_data)
        if not app.processor_data:
            messagebox.showwarning("입력 필요", "적어도 하나 이상의 프로세서를 추가해야 합니다.")
            return
        for i, proc_data in enumerate(app.processor_data):
            q_for_processor = time_quantum if app.app.scheduler_type == SchedulerType.RR else None
            app.app.add_processor(id=proc_data['id'], type=proc_data['type'], time_quantum=q_for_processor)
            if app.app.scheduler_type == SchedulerType.RR:
                app.processor_data[i]['quantum'] = q_for_processor
        try:
            app.app.select_scheduler()
            app.prepare_results_table(app.app.scheduler.processes)
            app.gantt.draw_initial_gantt_layout()
        except Exception as e:
            messagebox.showerror("초기화 오류", f"스케줄러 초기화 실패: {e}")
            app.reset_all()
            return
        app.simulation_running = True
        app.simulation_paused = False
        app.disable_inputs()
        app.start_button.configure(state="disabled")
        app.pause_resume_button.configure(text="Pause", state="normal")
        app.step_button.configure(state="normal")
        self.simulation_step()

    def toggle_pause_simulation(self):
        app = self.app
        if not app.simulation_running:
            return
        app.simulation_paused = not app.simulation_paused
        if app.simulation_paused:
            app.pause_resume_button.configure(text="Resume")
            if app.current_after_id:
                app.after_cancel(app.current_after_id)
                app.current_after_id = None
        else:
            app.pause_resume_button.configure(text="Pause")
            app.step_button.configure(state="normal")
            app.current_after_id = app.after(app.simulation_speed_ms, self.simulation_step)

    def step_simulation(self):
        app = self.app
        if not app.simulation_running:
            return
        if not app.simulation_paused:
            app.simulation_paused = True
            app.pause_resume_button.configure(text="Resume")
            if app.current_after_id:
                app.after_cancel(app.current_after_id)
            app.current_after_id = None
        self._execute_one_step()

    def _execute_one_step(self):
        app = self.app
        scheduler = app.app.scheduler
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
            app.gantt.update_gantt_chart_live(current_processors, current_time)
            app.update_results_table_live(current_processes)
            app.update_summary_live(current_time, current_power)
            scheduler.update_current_time()
            return True
        else:
            self.simulation_finished()
            return False

    def simulation_step(self):
        app = self.app
        if not app.simulation_running or app.simulation_paused:
            app.current_after_id = None
            return
        executed = self._execute_one_step()
        if executed and app.simulation_running and not app.simulation_paused:
            app.current_after_id = app.after(app.simulation_speed_ms, self.simulation_step)
        else:
            app.current_after_id = None

    def simulation_finished(self):
        app = self.app
        app.simulation_running = False
        app.simulation_paused = False
        final_time = "N/A"
        total_power = 0.0
        if app.app and app.app.scheduler:
            final_processes = app.app.scheduler.get_process()
            final_processors = app.app.scheduler.get_processors()
            final_time = app.app.scheduler.current_time
            total_power = app.app.scheduler.calculate_total_power()
            app.update_results_table_live(final_processes)
            app.calculate_and_display_summary(total_power, final_time)
        else:
            app.calculate_and_display_summary(0.0, 0)
        app.start_button.configure(text="Start", state="normal")
        app.pause_resume_button.configure(text="Pause", state="disabled")
        app.step_button.configure(state="disabled")
        app.enable_inputs()
        if app.current_after_id:
            app.after_cancel(app.current_after_id)
            app.current_after_id = None
        ftime_display = final_time if final_time != "N/A" else 0
        messagebox.showinfo("시뮬레이션 완료", f"시뮬레이션이 시간 {ftime_display}에 종료되었습니다.")

        if current_time == 0:
            return
        time_step = current_time - 1
        num_processors = len(app.processor_data)
        required_canvas_height = app.gantt_header_height + (num_processors * (app.gantt_row_height + app.gantt_padding)) + app.gantt_padding
        if num_processors == 0:
            required_canvas_height = app.gantt_header_height + 30
        if abs(app.gantt_canvas.winfo_reqheight() - required_canvas_height) > 1:
            app.gantt_canvas.config(height=required_canvas_height)
        required_total_width = app.gantt_label_width + (current_time * app.gantt_time_scale) + app.gantt_padding
        current_scroll_region = app.gantt_canvas.cget("scrollregion")
        if current_scroll_region:
            try:
                _, _, current_scroll_width, current_scroll_height = map(int, current_scroll_region.split())
            except ValueError:
                current_scroll_width = app.gantt_label_width + 800
                current_scroll_height = required_canvas_height
        else:
            current_scroll_width = app.gantt_label_width + 800
            current_scroll_height = required_canvas_height
        current_canvas_height = required_canvas_height
        width_changed = False
        if required_total_width > current_scroll_width:
            new_scroll_width = required_total_width + 200
            app.gantt_canvas.configure(scrollregion=(0, 0, new_scroll_width, current_canvas_height))
            start_t = int((current_scroll_width - app.gantt_label_width) / app.gantt_time_scale)
            end_t = int((new_scroll_width - app.gantt_label_width) / app.gantt_time_scale) + 1
            time_axis_y = app.gantt_padding + app.gantt_header_height / 2
            grid_line_top = app.gantt_padding
            grid_line_bottom = current_canvas_height - app.gantt_padding
            for t in range(start_t, end_t):
                x = app.gantt_label_width + (t * app.gantt_time_scale)
                app.gantt_canvas.create_line(x, grid_line_top, x, grid_line_bottom, fill="lightgrey", dash=(2,2), tags="time_grid")
                if t % 5 == 0:
                    app.gantt_canvas.create_text(x, time_axis_y, text=str(t), anchor="center", tags="time_label")
            current_scroll_width = new_scroll_width
            width_changed = True
        height_changed = False
        if abs(current_scroll_height - current_canvas_height) > 1:
            app.gantt_canvas.configure(scrollregion=(0, 0, current_scroll_width, current_canvas_height))
            height_changed = True
        visible_width = app.gantt_canvas.winfo_width()
        target_x_pos = app.gantt_label_width + (current_time * app.gantt_time_scale)
        if (width_changed or height_changed or (target_x_pos > visible_width + app.gantt_canvas.xview()[0] * current_scroll_width)) and current_scroll_width > 0:
            scroll_fraction = (target_x_pos - visible_width + 50) / current_scroll_width
            app.gantt_canvas.xview_moveto(min(max(0, scroll_fraction), 1.0))
        for i, processor in enumerate(processors):
            try:
                gui_proc_index = next(idx for idx, data in enumerate(app.processor_data) if data['id'] == processor.id)
            except StopIteration:
                continue
            y_top = app.gantt_padding + app.gantt_header_height + gui_proc_index * (app.gantt_row_height + app.gantt_padding)
            y_bottom = y_top + app.gantt_row_height
            pid_at_step = 0
            if time_step < len(processor.process_queue):
                pid_at_step = processor.process_queue[time_step] if processor.process_queue[time_step] is not None else 0
            pid = pid_at_step
            x_start = app.gantt_label_width + time_step * app.gantt_time_scale
            x_end = x_start + app.gantt_time_scale
            color = app.generate_color(pid)
            tag_name = f"t{time_step}_p{processor.id}"
            if pid != 0:
                app.gantt_canvas.create_rectangle(x_start, y_top + 1, x_end, y_bottom - 1, fill=color, outline="black", width=1, tags=(tag_name, "block"))
                if app.gantt_time_scale > 18:
                    text_color = "white" if sum(int(color[i:i+2], 16) for i in (1,3,5)) < 384 else "black"
                    app.gantt_canvas.create_text(x_start + app.gantt_time_scale / 2, y_top + app.gantt_row_height / 2, text=str(pid), fill=text_color, font=('Arial', 8, 'bold'), tags=(tag_name, "block_text"))
