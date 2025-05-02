# visualization/gui.py

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sys
import os
from collections import defaultdict
import random
import time # For potential small delays if needed, though 'after' is better

# --- Add parent directory to path to import modules ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
# ---

try:
    from core.process import Process
    from core.processor import Processor
    from simulator import SchedulerApp, SchedulerType
    # We will need access to the scheduler instance directly later
    from scheduler.base_scheduler import BaseScheduler
except ImportError as e:
    messagebox.showerror("Import Error", f"Failed to import necessary modules: {e}\n"
                         "Ensure core, scheduler, and simulator.py are in the parent directory.")
    sys.exit(1)


# --- Main GUI Application Class ---
class SchedulerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CPU Scheduler Simulator (Live)")
        self.geometry("1100x800") # Slightly wider for new controls

        # --- Data Storage ---
        self.app = SchedulerApp() # Use the simulator app
        self.process_data = []
        self.processor_data = []
        self.process_colors = {}

        # --- Simulation State ---
        self.simulation_running = False
        self.simulation_paused = False
        self.current_after_id = None
        self.simulation_speed_ms = 300 # Delay between steps in milliseconds

        # --- Style ---
        style = ttk.Style(self)
        style.theme_use('clam')

        # --- Main Layout Frames ---
        self.control_frame = ttk.Frame(self, padding="10")
        self.control_frame.pack(side=tk.TOP, fill=tk.X)

        self.input_frame = ttk.Frame(self, padding="10")
        self.input_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)

        self.output_frame = ttk.Frame(self, padding="10")
        self.output_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        # --- Control Frame Widgets ---
        self.setup_control_widgets() # Modified to add new controls

        # --- Input Frame Widgets ---
        self.setup_input_widgets() # No changes needed here

        # --- Output Frame Widgets ---
        self.setup_output_widgets() # Gantt drawing logic will change

        # --- Gantt Chart Drawing Parameters ---
        self.gantt_padding = 30
        self.gantt_header_height = 30
        self.gantt_row_height = 40
        self.gantt_time_scale = 25 # Pixels per time unit

    # --- Widget Setup Methods ---

    def setup_control_widgets(self):
        """Sets up widgets in the top control frame."""
        # --- Scheduler Selection ---
        ttk.Label(self.control_frame, text="Scheduler:", font=('Arial', 11, 'bold')).pack(side=tk.LEFT, padx=5)
        scheduler_names = [s.name for s in SchedulerType]
        self.scheduler_var = tk.StringVar(value=scheduler_names[0])
        self.scheduler_combo = ttk.Combobox(self.control_frame, textvariable=self.scheduler_var,
                                           values=scheduler_names, state="readonly", width=10)
        self.scheduler_combo.pack(side=tk.LEFT, padx=5)
        self.scheduler_combo.bind("<<ComboboxSelected>>", self.update_rr_quantum_visibility)

        # --- RR Quantum (conditionally visible) ---
        self.rr_quantum_label = ttk.Label(self.control_frame, text="RR Quantum:")
        self.rr_quantum_entry = ttk.Entry(self.control_frame, width=5)
        # Packed/unpacked in update_rr_quantum_visibility

        # --- Simulation Control Buttons ---
        self.start_button = ttk.Button(self.control_frame, text="Start", command=self.start_simulation)
        self.start_button.pack(side=tk.LEFT, padx=(20, 5))

        self.pause_resume_button = ttk.Button(self.control_frame, text="Pause", state=tk.DISABLED, command=self.toggle_pause_simulation)
        self.pause_resume_button.pack(side=tk.LEFT, padx=5)

        self.step_button = ttk.Button(self.control_frame, text="Step", state=tk.DISABLED, command=self.step_simulation)
        self.step_button.pack(side=tk.LEFT, padx=5)

        self.reset_button = ttk.Button(self.control_frame, text="Reset All", command=self.reset_all)
        self.reset_button.pack(side=tk.LEFT, padx=20)

        # --- Speed Control ---
        ttk.Label(self.control_frame, text="Speed (ms/step):").pack(side=tk.LEFT, padx=(10, 2))
        self.speed_scale = ttk.Scale(self.control_frame, from_=50, to=2000, orient=tk.HORIZONTAL,
                                     command=self.update_speed, length=150)
        self.speed_scale.set(self.simulation_speed_ms)
        self.speed_scale.pack(side=tk.LEFT, padx=2)
        self.speed_label_var = tk.StringVar(value=f"{self.simulation_speed_ms} ms")
        ttk.Label(self.control_frame, textvariable=self.speed_label_var, width=7).pack(side=tk.LEFT)


    def setup_input_widgets(self):
        """Sets up widgets in the left input frame. (No changes from previous version)"""
        input_notebook = ttk.Notebook(self.input_frame)

        # --- Process Input Tab ---
        process_tab = ttk.Frame(input_notebook, padding="10")
        input_notebook.add(process_tab, text='Processes')
        process_input_frame = ttk.LabelFrame(process_tab, text="Add Process")
        process_input_frame.pack(pady=10, fill=tk.X)
        ttk.Label(process_input_frame, text="PID:").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        self.pid_entry = ttk.Entry(process_input_frame, width=5)
        self.pid_entry.grid(row=0, column=1, padx=5, pady=2)
        self.pid_entry.insert(0,"1")
        ttk.Label(process_input_frame, text="Arrival:").grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        self.arrival_entry = ttk.Entry(process_input_frame, width=5)
        self.arrival_entry.grid(row=1, column=1, padx=5, pady=2)
        ttk.Label(process_input_frame, text="Burst:").grid(row=2, column=0, padx=5, pady=2, sticky=tk.W)
        self.burst_entry = ttk.Entry(process_input_frame, width=5)
        self.burst_entry.grid(row=2, column=1, padx=5, pady=2)
        self.add_process_button = ttk.Button(process_input_frame, text="Add", width=6, command=self.add_process)
        self.add_process_button.grid(row=0, column=2, rowspan=3, padx=10, pady=5, sticky=tk.NS)
        process_list_frame = ttk.LabelFrame(process_tab, text="Process List")
        process_list_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        self.process_tree = ttk.Treeview(process_list_frame, columns=("pid", "arrival", "burst"), show="headings", height=8)
        self.process_tree.heading("pid", text="PID")
        self.process_tree.heading("arrival", text="Arrival")
        self.process_tree.heading("burst", text="Burst")
        self.process_tree.column("pid", width=50, anchor=tk.CENTER)
        self.process_tree.column("arrival", width=70, anchor=tk.CENTER)
        self.process_tree.column("burst", width=70, anchor=tk.CENTER)
        self.process_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        process_scrollbar = ttk.Scrollbar(process_list_frame, orient=tk.VERTICAL, command=self.process_tree.yview)
        process_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.process_tree.configure(yscrollcommand=process_scrollbar.set)
        self.remove_process_button = ttk.Button(process_tab, text="Remove Selected Process", command=self.remove_process)
        self.remove_process_button.pack(pady=5)

        # --- Processor Input Tab ---
        processor_tab = ttk.Frame(input_notebook, padding="10")
        input_notebook.add(processor_tab, text='Processors')
        processor_input_frame = ttk.LabelFrame(processor_tab, text="Add Processor")
        processor_input_frame.pack(pady=10, fill=tk.X)
        ttk.Label(processor_input_frame, text="ID:").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        self.proc_id_entry = ttk.Entry(processor_input_frame, width=5)
        self.proc_id_entry.grid(row=0, column=1, padx=5, pady=2)
        self.proc_id_entry.insert(0,"1")
        ttk.Label(processor_input_frame, text="Type:").grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        self.proc_type_var = tk.StringVar(value='P')
        proc_type_p = ttk.Radiobutton(processor_input_frame, text="P-Core", variable=self.proc_type_var, value='P')
        proc_type_e = ttk.Radiobutton(processor_input_frame, text="E-Core", variable=self.proc_type_var, value='E')
        proc_type_p.grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)
        proc_type_e.grid(row=2, column=1, padx=5, pady=2, sticky=tk.W)
        self.add_processor_button = ttk.Button(processor_input_frame, text="Add", width=6, command=self.add_processor)
        self.add_processor_button.grid(row=0, column=2, rowspan=3, padx=10, pady=5, sticky=tk.NS)
        processor_list_frame = ttk.LabelFrame(processor_tab, text="Processor List")
        processor_list_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        self.processor_tree = ttk.Treeview(processor_list_frame, columns=("id", "type", "quantum"), show="headings", height=8)
        self.processor_tree.heading("id", text="ID")
        self.processor_tree.heading("type", text="Type")
        self.processor_tree.heading("quantum", text="Quantum")
        self.processor_tree.column("id", width=50, anchor=tk.CENTER)
        self.processor_tree.column("type", width=60, anchor=tk.CENTER)
        self.processor_tree.column("quantum", width=70, anchor=tk.CENTER)
        self.processor_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        processor_scrollbar = ttk.Scrollbar(processor_list_frame, orient=tk.VERTICAL, command=self.processor_tree.yview)
        processor_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.processor_tree.configure(yscrollcommand=processor_scrollbar.set)
        self.remove_processor_button = ttk.Button(processor_tab, text="Remove Selected Processor", command=self.remove_processor)
        self.remove_processor_button.pack(pady=5)

        input_notebook.pack(expand=True, fill=tk.BOTH)
        self.update_rr_quantum_visibility() # Ensure quantum is initially hidden/shown correctly


    def setup_output_widgets(self):
        """Sets up widgets in the right output frame."""
        output_notebook = ttk.Notebook(self.output_frame)

        # --- Gantt Chart Tab ---
        gantt_tab = ttk.Frame(output_notebook)
        output_notebook.add(gantt_tab, text='Gantt Chart')
        # Initial large scroll region, will be adjusted
        self.gantt_canvas = tk.Canvas(gantt_tab, bg='white', scrollregion=(0,0,2000,500))
        gantt_hbar = ttk.Scrollbar(gantt_tab, orient=tk.HORIZONTAL, command=self.gantt_canvas.xview)
        gantt_hbar.pack(side=tk.BOTTOM, fill=tk.X)
        gantt_vbar = ttk.Scrollbar(gantt_tab, orient=tk.VERTICAL, command=self.gantt_canvas.yview)
        gantt_vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.gantt_canvas.configure(xscrollcommand=gantt_hbar.set, yscrollcommand=gantt_vbar.set)
        self.gantt_canvas.pack(fill=tk.BOTH, expand=True)

        # --- Results Table Tab ---
        results_tab = ttk.Frame(output_notebook)
        output_notebook.add(results_tab, text='Results Table')
        self.results_tree = ttk.Treeview(results_tab,
                                         columns=("pid", "arrival", "burst","remain", "start", "wait", "turnaround", "ntt"),
                                         show="headings")
        self.results_tree.heading("pid", text="PID")
        self.results_tree.heading("arrival", text="Arrival")
        self.results_tree.heading("burst", text="Burst")
        self.results_tree.heading("remain", text="Remain") # Added Remaining Time
        self.results_tree.heading("start", text="Start")
        self.results_tree.heading("wait", text="Wait")
        self.results_tree.heading("turnaround", text="TT")
        self.results_tree.heading("ntt", text="NTT")
        for col in self.results_tree['columns']:
             self.results_tree.column(col, width=70, anchor=tk.CENTER)
        self.results_tree.column("ntt", width=80)
        results_scrollbar = ttk.Scrollbar(results_tab, orient=tk.VERTICAL, command=self.results_tree.yview)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_tree.configure(yscrollcommand=results_scrollbar.set)
        self.results_tree.pack(fill=tk.BOTH, expand=True)
        # Store item IDs for easy updating
        self.results_tree_items = {}


        # --- Summary Stats Tab ---
        summary_tab = ttk.Frame(output_notebook, padding="20")
        output_notebook.add(summary_tab, text='Summary')
        self.summary_label_vars = {}
        stats = [
            "Current Time", "Avg Wait Time", "Avg Turnaround Time", "Avg Normalized TT",
            "Total Power Used", "Final Time"
        ]
        for i, stat_name in enumerate(stats):
            ttk.Label(summary_tab, text=f"{stat_name}:", font=('Arial', 12, 'bold')).grid(row=i, column=0, padx=10, pady=5, sticky=tk.W)
            var = tk.StringVar(value="N/A")
            self.summary_label_vars[stat_name] = var
            ttk.Label(summary_tab, textvariable=var, font=('Arial', 12)).grid(row=i, column=1, padx=10, pady=5, sticky=tk.W)

        output_notebook.pack(expand=True, fill=tk.BOTH)

    # --- Event Handler Methods ---

    def get_unique_pid(self):
        existing_pids = {int(self.process_tree.item(item, 'values')[0]) for item in self.process_tree.get_children()}
        pid = 1
        while pid in existing_pids: pid += 1
        return pid

    def get_unique_processor_id(self):
        existing_ids = {int(self.processor_tree.item(item, 'values')[0]) for item in self.processor_tree.get_children()}
        pid = 1
        while pid in existing_ids: pid += 1
        return pid

    def add_process(self):
        if self.simulation_running: return # Don't allow changes during run
        try:
            pid_str = self.pid_entry.get()
            pid = int(pid_str) if pid_str else self.get_unique_pid()
            arrival = int(self.arrival_entry.get())
            burst = int(self.burst_entry.get())
            if arrival < 0 or burst <= 0: raise ValueError("Arrival >= 0, Burst > 0.")
            if any(int(self.process_tree.item(item, 'values')[0]) == pid for item in self.process_tree.get_children()):
                messagebox.showerror("Error", f"PID {pid} already exists.")
                return
            self.process_tree.insert("", tk.END, values=(pid, arrival, burst))
            self.process_data.append({'pid': pid, 'arrival': arrival, 'burst': burst})
            self.pid_entry.delete(0, tk.END)
            self.arrival_entry.delete(0, tk.END)
            self.burst_entry.delete(0, tk.END)
            self.pid_entry.insert(0, str(self.get_unique_pid()))
        except ValueError as e: messagebox.showerror("Input Error", f"Invalid process input: {e}")

    def remove_process(self):
        if self.simulation_running: return
        selected_items = self.process_tree.selection()
        if not selected_items: return
        if messagebox.askyesno("Confirm", "Remove selected process(es)?"):
            for item in selected_items:
                pid_to_remove = int(self.process_tree.item(item, 'values')[0])
                self.process_data = [p for p in self.process_data if p['pid'] != pid_to_remove]
                self.process_tree.delete(item)
            self.pid_entry.delete(0, tk.END); self.pid_entry.insert(0, str(self.get_unique_pid()))

    def add_processor(self):
        if self.simulation_running: return
        try:
            proc_id_str = self.proc_id_entry.get()
            proc_id = int(proc_id_str) if proc_id_str else self.get_unique_processor_id()
            proc_type = self.proc_type_var.get().upper()
            if proc_type not in ['P', 'E']: raise ValueError("Type must be 'P' or 'E'.")
            if any(int(self.processor_tree.item(item, 'values')[0]) == proc_id for item in self.processor_tree.get_children()):
                messagebox.showerror("Error", f"Processor ID {proc_id} already exists.")
                return
            # Quantum handling moved to update_rr_quantum_visibility and start_simulation
            quantum_display = "-"
            selected_scheduler = self.scheduler_var.get()
            if selected_scheduler == SchedulerType.RR.name:
                 quantum_display = self.rr_quantum_entry.get() if self.rr_quantum_entry.get() else "?" # Show potential quantum

            self.processor_tree.insert("", tk.END, values=(proc_id, proc_type, quantum_display))
            self.processor_data.append({'id': proc_id, 'type': proc_type, 'quantum': None}) # Actual quantum set later
            self.proc_id_entry.delete(0, tk.END)
            self.proc_id_entry.insert(0, str(self.get_unique_processor_id()))
            self.draw_initial_gantt_layout() # Update layout if processor added
        except ValueError as e: messagebox.showerror("Input Error", f"Invalid processor input: {e}")

    def remove_processor(self):
        if self.simulation_running: return
        selected_items = self.processor_tree.selection()
        if not selected_items: return
        if messagebox.askyesno("Confirm", "Remove selected processor(es)?"):
            for item in selected_items:
                 id_to_remove = int(self.processor_tree.item(item, 'values')[0])
                 self.processor_data = [p for p in self.processor_data if p['id'] != id_to_remove]
                 self.processor_tree.delete(item)
            self.proc_id_entry.delete(0, tk.END); self.proc_id_entry.insert(0, str(self.get_unique_processor_id()))
            self.draw_initial_gantt_layout() # Update layout if processor removed

    def update_rr_quantum_visibility(self, event=None):
        """Shows or hides the RR time quantum input based on scheduler selection."""
        selected_scheduler = self.scheduler_var.get()
        is_rr = selected_scheduler == SchedulerType.RR.name

        # Update visibility of entry widget
        if is_rr:
            self.rr_quantum_label.pack(side=tk.LEFT, padx=(15, 2))
            self.rr_quantum_entry.pack(side=tk.LEFT, padx=(0, 5))
            if not self.rr_quantum_entry.get(): # Add default if empty
                 self.rr_quantum_entry.insert(0, "4")
        else:
            self.rr_quantum_label.pack_forget()
            self.rr_quantum_entry.pack_forget()

        # Update quantum display in the processor list
        quantum_display = self.rr_quantum_entry.get() if is_rr and self.rr_quantum_entry.get() else "-"
        for item_id in self.processor_tree.get_children():
            current_values = list(self.processor_tree.item(item_id, 'values'))
            current_values[2] = quantum_display
            self.processor_tree.item(item_id, values=tuple(current_values))


    def update_speed(self, value):
        """Updates simulation speed from the slider."""
        self.simulation_speed_ms = int(float(value))
        self.speed_label_var.set(f"{self.simulation_speed_ms} ms")

    def reset_all(self):
        """Resets all inputs, outputs, and the simulator app state."""
        # Stop any ongoing simulation first
        if self.current_after_id:
            self.after_cancel(self.current_after_id)
            self.current_after_id = None

        self.simulation_running = False
        self.simulation_paused = False

        # Reset GUI elements
        self.process_tree.delete(*self.process_tree.get_children())
        self.processor_tree.delete(*self.processor_tree.get_children())
        self.process_data.clear()
        self.processor_data.clear()
        self.pid_entry.delete(0, tk.END); self.pid_entry.insert(0,"1")
        self.arrival_entry.delete(0, tk.END)
        self.burst_entry.delete(0, tk.END)
        self.proc_id_entry.delete(0, tk.END); self.proc_id_entry.insert(0,"1")
        self.proc_type_var.set('P')
        self.rr_quantum_entry.delete(0, tk.END)
        self.scheduler_combo.current(0)
        self.update_rr_quantum_visibility()
        self.speed_scale.set(300); self.update_speed(300)

        # Clear outputs
        self.clear_outputs()

        # Reset controls to initial state
        self.start_button.config(text="Start", state=tk.NORMAL)
        self.pause_resume_button.config(text="Pause", state=tk.DISABLED)
        self.step_button.config(state=tk.DISABLED)
        self.enable_inputs()

        # Reset the underlying simulator application (important!)
        self.app = SchedulerApp()
        self.process_colors.clear() # Clear color map

        print("--- GUI Reset ---")

    def clear_outputs(self):
        """Clears the output areas (Gantt, results table, summary)."""
        self.gantt_canvas.delete("all")
        # Reset scroll region to something reasonable
        self.gantt_canvas.configure(scrollregion=(0, 0, 800, 400))
        self.results_tree.delete(*self.results_tree.get_children())
        self.results_tree_items.clear()
        for key in self.summary_label_vars:
            self.summary_label_vars[key].set("N/A")

    def generate_color(self, pid):
        """Generates a unique, somewhat pleasant color for a PID."""
        if pid == 0: return "#E0E0E0" # Idle
        if pid not in self.process_colors:
            random.seed(pid)
            r, g, b = [random.randint(100, 230) for _ in range(3)]
            # Avoid colors too close to white/gray used for idle
            if r > 200 and g > 200 and b > 200:
                 b = random.randint(100,180) # Make one component darker
            self.process_colors[pid] = f'#{r:02x}{g:02x}{b:02x}'
        return self.process_colors[pid]

    def disable_inputs(self):
        """Disables input widgets during simulation."""
        self.add_process_button.config(state=tk.DISABLED)
        self.remove_process_button.config(state=tk.DISABLED)
        self.add_processor_button.config(state=tk.DISABLED)
        self.remove_processor_button.config(state=tk.DISABLED)
        self.scheduler_combo.config(state=tk.DISABLED)
        self.pid_entry.config(state=tk.DISABLED)
        self.arrival_entry.config(state=tk.DISABLED)
        self.burst_entry.config(state=tk.DISABLED)
        self.proc_id_entry.config(state=tk.DISABLED)
        # Keep RR quantum entry disabled if it's visible
        if self.scheduler_var.get() == SchedulerType.RR.name:
             self.rr_quantum_entry.config(state=tk.DISABLED)


    def enable_inputs(self):
        """Enables input widgets when simulation is not running."""
        self.add_process_button.config(state=tk.NORMAL)
        self.remove_process_button.config(state=tk.NORMAL)
        self.add_processor_button.config(state=tk.NORMAL)
        self.remove_processor_button.config(state=tk.NORMAL)
        self.scheduler_combo.config(state="readonly")
        self.pid_entry.config(state=tk.NORMAL)
        self.arrival_entry.config(state=tk.NORMAL)
        self.burst_entry.config(state=tk.NORMAL)
        self.proc_id_entry.config(state=tk.NORMAL)
        if self.scheduler_var.get() == SchedulerType.RR.name:
             self.rr_quantum_entry.config(state=tk.NORMAL)


    # --- Simulation Control ---

    def start_simulation(self):
        """Starts the step-by-step simulation."""
        if self.simulation_running: return # Already running

        self.clear_outputs()
        print("--- Preparing Simulation ---")

        # --- 1. Configure SchedulerApp ---
        self.app = SchedulerApp() # Start fresh

        # Set Scheduler Type
        selected_scheduler_name = self.scheduler_var.get()
        try: self.app.scheduler_type = SchedulerType[selected_scheduler_name]
        except KeyError: messagebox.showerror("Error", f"Invalid scheduler: {selected_scheduler_name}"); return

        # Get RR Quantum if needed
        time_quantum = None
        if self.app.scheduler_type == SchedulerType.RR:
            try:
                quantum_str = self.rr_quantum_entry.get()
                if not quantum_str: messagebox.showerror("Input Error", "Enter RR Time Quantum."); return
                time_quantum = int(quantum_str)
                if time_quantum <= 0: raise ValueError("Quantum must be positive.")
            except ValueError as e: messagebox.showerror("Input Error", f"Invalid Quantum: {e}"); return

        # Add Processes
        if not self.process_data: messagebox.showwarning("Input Needed", "Add processes."); return
        for p_data in self.process_data: self.app.add_process(**p_data)

        # Add Processors & Set Quantum Correctly
        if not self.processor_data: messagebox.showwarning("Input Needed", "Add processors."); return
        for i, proc_data in enumerate(self.processor_data):
             q_for_processor = time_quantum if self.app.scheduler_type == SchedulerType.RR else None
             self.app.add_processor(id=proc_data['id'], type=proc_data['type'], time_quantum=q_for_processor)
             # Update internal data list with actual quantum used for RR
             if self.app.scheduler_type == SchedulerType.RR:
                 self.processor_data[i]['quantum'] = q_for_processor


        # --- 2. Initialize Scheduler ---
        try:
            # This selects the correct class and initializes the scheduler instance
            # with the processes and processors we just added to self.app
            self.app.select_scheduler()
            # Now self.app.scheduler is the initialized scheduler instance (e.g., FCFSScheduler)
            print(f"Selected Scheduler: {type(self.app.scheduler).__name__}")

            # Prepare output areas for live updates
            self.prepare_results_table(self.app.scheduler.processes)
            self.draw_initial_gantt_layout() # Draw axes and processor labels

        except Exception as e:
            messagebox.showerror("Initialization Error", f"Failed to initialize scheduler: {e}")
            import traceback; traceback.print_exc()
            self.reset_all()
            return

        # --- 3. Start Step-by-Step Execution ---
        self.simulation_running = True
        self.simulation_paused = False
        self.disable_inputs()
        self.start_button.config(state=tk.DISABLED) # Start becomes inactive once running
        self.pause_resume_button.config(text="Pause", state=tk.NORMAL)
        self.step_button.config(state=tk.NORMAL) # Enable step initially

        print("--- Starting Simulation Steps ---")
        self.simulation_step() # Start the first step

    def toggle_pause_simulation(self):
        """Pauses or resumes the automatic simulation."""
        if not self.simulation_running: return

        self.simulation_paused = not self.simulation_paused
        if self.simulation_paused:
            self.pause_resume_button.config(text="Resume")
            if self.current_after_id:
                self.after_cancel(self.current_after_id)
                self.current_after_id = None
            print("--- Simulation Paused ---")
        else:
            self.pause_resume_button.config(text="Pause")
            print("--- Simulation Resumed ---")
            # Re-enable step button only if paused
            self.step_button.config(state=tk.NORMAL)
            # Schedule the next step immediately
            self.simulation_step()


    def step_simulation(self):
        """Executes exactly one simulation step."""
        if not self.simulation_running: return

        # If running automatically, pause first
        if not self.simulation_paused:
            self.simulation_paused = True
            self.pause_resume_button.config(text="Resume")
            if self.current_after_id:
                self.after_cancel(self.current_after_id)
                self.current_after_id = None
            print("--- Paused for Stepping ---")

        # Execute one step manually
        self._execute_one_step()


    def _execute_one_step(self):
        """Internal method to perform the logic of a single simulation time step."""
        scheduler = self.app.scheduler
        if not scheduler or not isinstance(scheduler, BaseScheduler):
             print("Error: Scheduler not properly initialized.")
             self.simulation_finished()
             return

        if scheduler.hasNext():
            current_time = scheduler.current_time
            print(f"\n--- Time: {current_time} ---") # Console log for step

            # Execute the core logic for one time step using BaseScheduler's public methods
            scheduler.ready_queue_update()
            scheduler.schedule()         # Processor executes its current process
            scheduler.assign_process()   # Assign processes from ready queue if processors available
            scheduler.processor_power_off() # Turn off idle processors if conditions met
            scheduler.process_waiting_time_update() # Increment wait time for ready processes

            # Get current state AFTER the step's logic
            current_processes = scheduler.get_process()
            current_processors = scheduler.get_processors()

            # Update GUI (Live)
            self.update_gantt_chart_live(current_processors, current_time)
            self.update_results_table_live(current_processes)
            self.update_summary_live(current_time, scheduler.get_current_power())

            # Original log state (optional, prints detailed info to console)
            # scheduler.log_state()

            # Advance time for the *next* step
            scheduler.update_current_time()

            return True # Step was executed
        else:
            # Simulation has finished
            self.simulation_finished()
            return False # No more steps

    def simulation_step(self):
        """Method called repeatedly by 'after' for automatic execution."""
        if not self.simulation_running or self.simulation_paused:
            return # Stop if paused or reset

        executed = self._execute_one_step()

        if executed:
            # Schedule the next step if simulation is still running and not paused
             self.current_after_id = self.after(self.simulation_speed_ms, self.simulation_step)
        # else: simulation_finished() was called by _execute_one_step


    def simulation_finished(self):
        """Called when scheduler.hasNext() is false."""
        print("--- Simulation Finished ---")
        self.simulation_running = False
        self.simulation_paused = False

        # Final updates
        final_processes = self.app.scheduler.get_process()
        final_processors = self.app.scheduler.get_processors()
        final_time = self.app.scheduler.current_time
        total_power = self.app.scheduler.get_current_power()

        # Ensure final state is reflected in GUI (might be redundant but safe)
        self.update_results_table_live(final_processes)
        self.calculate_and_display_summary(final_processes, final_processors, total_power, final_time)


        # Reset controls
        self.start_button.config(text="Start", state=tk.NORMAL) # Allow restarting
        self.pause_resume_button.config(text="Pause", state=tk.DISABLED)
        self.step_button.config(state=tk.DISABLED)
        self.enable_inputs()

        if self.current_after_id:
            self.after_cancel(self.current_after_id)
            self.current_after_id = None

        messagebox.showinfo("Simulation Complete", f"Simulation finished at time {final_time}.")


    # --- Live Update Methods ---

    def draw_initial_gantt_layout(self):
         """Draws the axes, processor labels, and initial grid."""
         self.gantt_canvas.delete("all")
         self.process_colors.clear() # Reset colors

         num_processors = len(self.processor_data)
         if num_processors == 0: return

         # Estimate initial canvas size (can be expanded later)
         initial_width = 800
         canvas_height = self.gantt_header_height + (num_processors * (self.gantt_row_height + self.gantt_padding)) + self.gantt_padding

         self.gantt_canvas.configure(scrollregion=(0, 0, initial_width, canvas_height))

         # Draw Initial Time Axis (up to a certain point)
         max_initial_time = int((initial_width - self.gantt_padding * 2) / self.gantt_time_scale)
         for t in range(max_initial_time + 1):
             x = self.gantt_padding + (t * self.gantt_time_scale)
             # Time tick line
             self.gantt_canvas.create_line(x, self.gantt_padding, x, canvas_height - self.gantt_padding, fill="lightgrey", dash=(2, 2), tags="time_grid")
             # Time label
             if t % 5 == 0 or max_initial_time <= 20:
                 self.gantt_canvas.create_text(x, self.gantt_padding + self.gantt_header_height / 2, text=str(t), anchor=tk.CENTER, tags="time_label")


         # Draw Processor Rows
         for i, processor_info in enumerate(self.processor_data):
             y_top = self.gantt_padding + self.gantt_header_height + i * (self.gantt_row_height + self.gantt_padding)
             y_bottom = y_top + self.gantt_row_height

             # Processor Label
             self.gantt_canvas.create_text(self.gantt_padding - 10, y_top + self.gantt_row_height / 2,
                                         text=f"CPU {processor_info['id']} ({processor_info['type']})", anchor=tk.E, tags="proc_label")
             # Draw initial empty timeline rectangle outline (optional, maybe just draw blocks)
             # self.gantt_canvas.create_rectangle(padding, y_top, padding + initial_width - 2*padding, y_bottom, outline="grey", tags="proc_timeline")


    def update_gantt_chart_live(self, processors: list[Processor], current_time: int):
        """Draws the segment for the *current* time step on the Gantt chart."""
        if current_time == 0: return # Nothing to draw at time 0

        time_step = current_time - 1 # The block represents time [t-1, t]

        # --- Check and Expand Canvas/Grid if necessary ---
        required_width = self.gantt_padding + (current_time * self.gantt_time_scale) + self.gantt_padding
        current_scroll_region = self.gantt_canvas.cget('scrollregion')
        if current_scroll_region:
             _, _, current_width, current_height = map(int, current_scroll_region.split())
        else:
            current_width, current_height = 800, 400 # Default if not set

        needs_redraw = False
        if required_width > current_width:
            new_width = required_width + 200 # Add buffer
            self.gantt_canvas.configure(scrollregion=(0, 0, new_width, current_height))
             # Extend time grid and labels
            for t in range(int(current_width / self.gantt_time_scale) + 1 , int(new_width / self.gantt_time_scale) + 1):
                 x = self.gantt_padding + (t * self.gantt_time_scale)
                 self.gantt_canvas.create_line(x, self.gantt_padding, x, current_height - self.gantt_padding, fill="lightgrey", dash=(2, 2), tags="time_grid")
                 if t % 5 == 0:
                     self.gantt_canvas.create_text(x, self.gantt_padding + self.gantt_header_height / 2, text=str(t), anchor=tk.CENTER, tags="time_label")
            current_width = new_width # Update for scrolling check
            needs_redraw = True # Signal that xview_moveto might be needed

        # Scroll horizontally to keep the current time visible
        visible_width = self.gantt_canvas.winfo_width() # Actual widget width
        if required_width > visible_width + self.gantt_canvas.xview()[0] * current_width or needs_redraw:
             # Calculate how much to scroll (fraction of total width)
             scroll_fraction = (required_width - visible_width + 50) / current_width
             self.gantt_canvas.xview_moveto(min(max(0, scroll_fraction), 1.0))


        # --- Draw Blocks for the Current Time Step ---
        for i, processor in enumerate(processors):
             # Find the matching processor info from our input data to get the correct index 'i'
             try:
                 # Find index based on processor ID - safer if order changes
                 gui_proc_index = next(idx for idx, data in enumerate(self.processor_data) if data['id'] == processor.id)
             except StopIteration:
                 print(f"Warning: Processor ID {processor.id} not found in GUI data.")
                 continue # Skip if processor not found (shouldn't happen ideally)

             y_top = self.gantt_padding + self.gantt_header_height + gui_proc_index * (self.gantt_row_height + self.gantt_padding)
             y_bottom = y_top + self.gantt_row_height

             # Determine PID running in the *previous* interval [t-1, t]
             # The processor.current_process is the one assigned *for* time t,
             # but the block visually represents what ran *until* time t.
             # The processor's process_queue stores the PID that *started* at each time step.
             pid_at_step = 0 # Default to idle
             if time_step < len(processor.process_queue):
                 pid_at_step = processor.process_queue[time_step] # Get PID that ran during [t-1, t]
                 if pid_at_step is None: pid_at_step = 0 # Treat potential None as idle

             # if processor.current_process: # This reflects state *after* schedule() at time t-1
             #     pid = processor.current_process.pid
             # else: # Processor was idle during [t-1, t]
             #     pid = 0
             pid = pid_at_step # Use the logged PID

             x_start = self.gantt_padding + time_step * self.gantt_time_scale
             x_end = x_start + self.gantt_time_scale
             color = self.generate_color(pid)

             # Draw the block segment
             tag_name = f"t{time_step}_p{processor.id}" # Unique tag for this block segment
             if pid != 0:
                 self.gantt_canvas.create_rectangle(x_start, y_top + 2, x_end, y_bottom - 2,
                                                    fill=color, outline="black", tags=(tag_name, "block"))
                 # Add PID text if block is wide enough
                 if self.gantt_time_scale > 18:
                      text_color = "white" if sum(int(color[i:i+2], 16) for i in (1, 3, 5)) < 384 else "black" # Dark/light text
                      self.gantt_canvas.create_text(x_start + self.gantt_time_scale / 2, y_top + self.gantt_row_height / 2,
                                                  text=str(pid), fill=text_color, font=('Arial', 9, 'bold'), tags=(tag_name, "block_text"))
             # else: # Optionally draw idle blocks explicitly lighter grey
             #    self.gantt_canvas.create_rectangle(x_start, y_top + 2, x_end, y_bottom - 2,
             #                                       fill=color, outline="lightgrey", tags=(tag_name, "idle_block"))

    def prepare_results_table(self, initial_processes: list[Process]):
        """Populates the results table initially and stores item IDs."""
        self.results_tree.delete(*self.results_tree.get_children())
        self.results_tree_items.clear()
        initial_processes.sort(key=lambda p: p.pid)

        for p in initial_processes:
             # Initial values
             item_id = self.results_tree.insert("", tk.END, values=(
                 p.pid, p.arrival, p.burst, p.remaining_time, "-", "-", "-", "-"
             ))
             self.results_tree_items[p.pid] = item_id # Store Treeview item ID by PID

    def update_results_table_live(self, current_processes: list[Process]):
        """Updates the values in the results table rows."""
        for p in current_processes:
            if p.pid in self.results_tree_items:
                item_id = self.results_tree_items[p.pid]
                st = p.start_time if p.start_time is not None else "-"
                wt = p.wait_time # wait_time is updated each step
                tt = p.turnaround_time if p.turnaround_time is not None else "-"
                ntt = f"{p.normalized_turnaround_time:.3f}" if p.normalized_turnaround_time is not None else "-"
                remain = p.remaining_time

                # Update the specific row using its item_id
                self.results_tree.item(item_id, values=(
                    p.pid, p.arrival, p.burst, remain, st, wt, tt, ntt
                ))
            # else: Process not found in table (shouldn't happen if prepare was called)

    def update_summary_live(self, current_time: int, current_power: float):
         """Updates summary stats that change frequently."""
         self.summary_label_vars["Current Time"].set(str(current_time))
         self.summary_label_vars["Total Power Used"].set(f"{current_power:.2f}")
         # Averages are calculated at the end in calculate_and_display_summary


    def calculate_and_display_summary(self, processes: list[Process], processors: list[Processor], total_power: float, final_time: int):
        """Calculates final summary statistics and updates the summary labels."""
        num_processes = len(processes)
        if num_processes == 0:
             self.summary_label_vars["Final Time"].set(str(final_time))
             return

        # Filter completed processes for accurate averages
        completed_processes = [p for p in processes if p.is_completed()]
        num_completed = len(completed_processes)

        if num_completed > 0:
            total_wait = sum(p.wait_time for p in completed_processes)
            total_turnaround = sum(p.turnaround_time for p in completed_processes)
            total_ntt = sum(p.normalized_turnaround_time for p in completed_processes)
            avg_wait = total_wait / num_completed
            avg_turnaround = total_turnaround / num_completed
            avg_ntt = total_ntt / num_completed
            self.summary_label_vars["Avg Wait Time"].set(f"{avg_wait:.3f}")
            self.summary_label_vars["Avg Turnaround Time"].set(f"{avg_turnaround:.3f}")
            self.summary_label_vars["Avg Normalized TT"].set(f"{avg_ntt:.3f}")
        else:
             self.summary_label_vars["Avg Wait Time"].set("N/A (0 completed)")
             self.summary_label_vars["Avg Turnaround Time"].set("N/A (0 completed)")
             self.summary_label_vars["Avg Normalized TT"].set("N/A (0 completed)")

        # Update stats that were live-updated as well
        self.summary_label_vars["Total Power Used"].set(f"{total_power:.2f}")
        self.summary_label_vars["Final Time"].set(str(final_time))
        self.summary_label_vars["Current Time"].set(str(final_time)) # Current time = Final time at end

# --- Main Execution ---
if __name__ == "__main__":
    # Optional: Basic check for scheduler files (as before)
    scheduler_dir = os.path.join(parent_dir, "scheduler")
    required_files = ["__init__.py", "base_scheduler.py", "fcfs_scheduler.py",
                     "rr_scheduler.py", "spn_scheduler.py", "srtn_scheduler.py",
                     "hrrn_scheduler.py", "custom_scheduler.py"]
    missing_files = [f for f in required_files if not os.path.exists(os.path.join(scheduler_dir, f))]
    if missing_files:
        messagebox.showwarning("Missing Files",
                               f"Scheduler files missing in '{scheduler_dir}':\n{', '.join(missing_files)}\n"
                               "Simulator might not work for all types.")

    app_gui = SchedulerGUI()
    app_gui.mainloop()