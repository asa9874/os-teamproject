import random

class GanttManager:
    def __init__(self, app):
        self.app = app
        
    def update_gantt_chart_live(self, processors: list, current_time: int):
        app = self.app
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
            color = self.generate_color(pid)
            tag_name = f"t{time_step}_p{processor.id}"
            if pid != 0:
                app.gantt_canvas.create_rectangle(x_start, y_top + 1, x_end, y_bottom - 1, fill=color, outline="black", width=1, tags=(tag_name, "block"))
                if app.gantt_time_scale > 18:
                    text_color = "white" if sum(int(color[i:i+2], 16) for i in (1,3,5)) < 384 else "black"
                    app.gantt_canvas.create_text(x_start + app.gantt_time_scale / 2, y_top + app.gantt_row_height / 2, text=str(pid), fill=text_color, font=('Arial', 8, 'bold'), tags=(tag_name, "block_text"))

    def generate_color(self, pid):
        app = self.app
        if pid == 0:
            return "#E0E0E0"
        if pid not in app.process_colors:
            random.seed(pid)
            r, g, b = [random.randint(100, 230) for _ in range(3)]
            if r > 200 and g > 200 and b > 200:
                b = random.randint(100,180)
            app.process_colors[pid] = f'#{r:02x}{g:02x}{b:02x}'
        return app.process_colors[pid]


    def draw_initial_gantt_layout(self):
        app = self.app
        app.gantt_canvas.delete("all")
        app.process_colors.clear()
        num_processors = len(app.processor_data)
        canvas_height = app.gantt_header_height + (num_processors * (app.gantt_row_height + app.gantt_padding)) + app.gantt_padding
        if num_processors == 0:
            canvas_height = app.gantt_header_height + 30
        app.gantt_canvas.config(height=canvas_height)
        initial_drawing_width = 800
        scroll_width = app.gantt_label_width + initial_drawing_width + app.gantt_padding
        app.gantt_canvas.configure(scrollregion=(0, 0, scroll_width, canvas_height))
        drawing_width_available = initial_drawing_width
        max_initial_time = int(drawing_width_available / app.gantt_time_scale)
        max_initial_time = max(0, max_initial_time)
        time_axis_y = app.gantt_padding + app.gantt_header_height / 2
        grid_line_top = app.gantt_padding
        grid_line_bottom = canvas_height - app.gantt_padding
        for t in range(max_initial_time + 1):
            x = app.gantt_label_width + (t * app.gantt_time_scale)
            app.gantt_canvas.create_line(x, grid_line_top, x, grid_line_bottom, fill="lightgrey", dash=(2,2), tags="time_grid")
            if t % 5 == 0 or max_initial_time <= 20:
                app.gantt_canvas.create_text(x, time_axis_y, text=str(t), anchor="center", tags="time_label")
        label_x_pos = app.gantt_label_width - 5
        for i, processor_info in enumerate(app.processor_data):
            y_top = app.gantt_padding + app.gantt_header_height + i * (app.gantt_row_height + app.gantt_padding)
            label_y_center = y_top + app.gantt_row_height / 2
            app.gantt_canvas.create_text(label_x_pos, label_y_center - 6, text=f"CPU {processor_info['id']}", anchor="e", tags="proc_label", font=('Arial', 9))
            app.gantt_canvas.create_text(label_x_pos, label_y_center + 6, text=f"({processor_info['type']}-Core)", anchor="e", tags="proc_label", font=('Arial', 8))
