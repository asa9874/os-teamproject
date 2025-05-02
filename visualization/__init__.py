import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import sys
import time # To demonstrate GUI freeze (optional)
import copy

# --- Adjust imports based on your project structure ---
try:
    from core.process import Process
    from core.processor import Processor
    # Assuming simulator.py contains SchedulerApp (logic class)
    from simulator import SchedulerApp as SimulationLogic
    from scheduler import SchedulerType, BaseScheduler # Import Base for type hint
    # Import specific schedulers needed for SchedulerApp's map
    from scheduler import (
        FCFSScheduler, RRScheduler, SPNScheduler,
        HRRNScheduler, SRTNScheduler, CustomScheduler
    )

except ImportError as e:
    print(f"Import Error: {e}")
    print("Attempting path adjustment...")
    # Fallback for running gui.py directly or different structure
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
        print(f"Added '{parent_dir}' to sys.path")

    # Retry imports after path adjustment
    try:
        from core.process import Process
        from core.processor import Processor
        from simulator import SchedulerApp as SimulationLogic
        from scheduler import SchedulerType, BaseScheduler
        from scheduler import ( # Ensure these are findable now
             FCFSScheduler, RRScheduler, SPNScheduler,
             HRRNScheduler, SRTNScheduler, CustomScheduler
         )
        print("Imports successful after path adjustment.")
    except ImportError as e2:
        print(f"Failed to import after path adjustment: {e2}")
        messagebox.showerror("Import Error", "Could not find necessary modules (core, scheduler, simulator). Please check project structure and PYTHONPATH.")
        sys.exit(1) # Exit if essential modules can't be loaded


class SimulationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CPU Scheduler Simulator (Blocking Simulation)")
        # self.root.geometry("1200x800")

        # --- Style ---
        self.style = ttk.Style()
        try:
            if os.name == 'nt': self.style.theme_use('vista')
            else: self.style.theme_use('clam')
        except tk.TclError: self.style.theme_use('default')
        self.style.configure("Treeview.Heading", font=('Segoe UI', 10, 'bold'))
        self.style.configure("Treeview", rowheight=25)
        self.style.configure("Status.TLabel", font=('Segoe UI', 10, 'bold'))
        self.style.configure("Bold.TButton", font=('Segoe UI', 9, 'bold'))

        # --- Simulation Logic Instance ---
        self.simulator_logic = SimulationLogic()

        # --- GUI State ---
        self.simulation_running = False # To prevent re-clicks during freeze

        # --- Create Widgets ---
        self._create_widgets()
        self._update_display_initial() # Initial display setup

    def _create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(1, weight=1) # Right column expands

        # --- Left Column: Controls & Input ---
        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="nw")

        # == Process Input Frame ==
        process_frame = ttk.LabelFrame(left_frame, text="Add Process", padding="10")
        process_frame.pack(fill=tk.X, pady=(0, 10))

        # PID Entry Removed - ID assigned automatically
        ttk.Label(process_frame, text="Arrival:").grid(row=0, column=0, padx=5, pady=2, sticky="w") # Start at row 0
        self.arrival_entry = ttk.Entry(process_frame, width=7)
        self.arrival_entry.grid(row=0, column=1, padx=5, pady=2) # Start at row 0

        ttk.Label(process_frame, text="Burst:").grid(row=1, column=0, padx=5, pady=2, sticky="w") # Now row 1
        self.burst_entry = ttk.Entry(process_frame, width=7)
        self.burst_entry.grid(row=1, column=1, padx=5, pady=2) # Now row 1

        self.add_proc_button = ttk.Button(process_frame, text="Add Process", command=self._add_process_gui, width=15)
        self.add_proc_button.grid(row=2, column=0, columnspan=2, pady=5) # Now row 2


        # == Processor Input Frame ==
        processor_frame = ttk.LabelFrame(left_frame, text="Add Processor", padding="10")
        processor_frame.pack(fill=tk.X, pady=(0, 10))

        # ID Entry Removed - ID assigned automatically
        ttk.Label(processor_frame, text="Type:").grid(row=0, column=0, padx=5, pady=2, sticky="w") # Start at row 0
        self.proc_type_var = tk.StringVar(value='P')
        self.proc_type_combo = ttk.Combobox(processor_frame, textvariable=self.proc_type_var, values=['P', 'E'], width=5, state='readonly')
        self.proc_type_combo.grid(row=0, column=1, padx=5, pady=2) # Start at row 0

        ttk.Label(processor_frame, text="Time Q (RR only):").grid(row=1, column=0, padx=5, pady=2, sticky="w") # Now row 1
        self.time_q_entry = ttk.Entry(processor_frame, width=7)
        self.time_q_entry.grid(row=1, column=1, padx=5, pady=2) # Now row 1

        self.add_cpu_button = ttk.Button(processor_frame, text="Add Processor", command=self._add_processor_gui, width=15)
        self.add_cpu_button.grid(row=2, column=0, columnspan=2, pady=5) # Now row 2


        # == Simulation Control Frame ==
        control_frame = ttk.LabelFrame(left_frame, text="Simulation Control", padding="10")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        # ... (Algorithm Combo, Start, Reset Buttons - same as previous version)
        ttk.Label(control_frame, text="Algorithm:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.algo_var = tk.StringVar(value=SchedulerType.FCFS.value) # Default
        self.algo_combo = ttk.Combobox(control_frame, textvariable=self.algo_var,
                                        values=[st.value for st in SchedulerType],
                                        state='readonly', width=10)
        self.algo_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.algo_combo.bind("<<ComboboxSelected>>", self._on_algorithm_select)
        self.start_button = ttk.Button(control_frame, text="Run Simulation", command=self._run_full_simulation, width=15, style="Bold.TButton")
        self.start_button.grid(row=1, column=0, padx=5, pady=10)
        self.reset_button = ttk.Button(control_frame, text="Reset", command=self._reset_simulation, width=8)
        self.reset_button.grid(row=1, column=1, padx=5, pady=10)


        # --- Right Column: Display Area ---
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        right_frame.rowconfigure(2, weight=1) # Process table expands
        right_frame.rowconfigure(4, weight=1) # Timeline expands
        right_frame.columnconfigure(0, weight=1)

        # == Status Display (Shows FINAL results) ==
        status_frame = ttk.Frame(right_frame, padding=(0, 0, 0, 10))
        status_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        # ... (Time, Ready Queue, Results Labels - adjusted text slightly)
        ttk.Label(status_frame, text="Simulation Status:", style="Status.TLabel").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.status_var = tk.StringVar(value="Idle. Ready to run.")
        ttk.Label(status_frame, textvariable=self.status_var, font=('Segoe UI', 10)).grid(row=0, column=1, columnspan=3, padx=5, pady=2, sticky="w")

        self.results_var = tk.StringVar(value="Final Results: N/A")
        ttk.Label(status_frame, textvariable=self.results_var, style="Status.TLabel").grid(row=0, column=4, padx=10, pady=2, sticky="e")


        # == Processor Status Table (Shows FINAL state) ==
        proc_status_frame = ttk.LabelFrame(right_frame, text="Processor Final Status", padding="5")
        proc_status_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky="ew")
        proc_status_frame.columnconfigure(0, weight=1)
        # ... (Processor TreeView - same columns as previous version)
        proc_cols = ("ID", "Type", "Power State", "Current Process", "Time Quantum", "Used Power")
        self.proc_tree = ttk.Treeview(proc_status_frame, columns=proc_cols, show='headings', height=3)
        for col in proc_cols:
            self.proc_tree.heading(col, text=col)
            self.proc_tree.column(col, width=80, anchor=tk.CENTER)
        self.proc_tree.column("Used Power", width=100)
        self.proc_tree.pack(fill=tk.X, expand=True)


        # == Process Status Table (Shows FINAL state) ==
        process_status_frame = ttk.LabelFrame(right_frame, text="Process Final Status", padding="5")
        process_status_frame.grid(row=2, column=0, columnspan=2, pady=5, sticky="nsew")
        process_status_frame.rowconfigure(0, weight=1)
        process_status_frame.columnconfigure(0, weight=1)
        # ... (Process TreeView - same columns as previous version)
        proc_status_cols = ("PID", "Arrival", "Burst", "Remaining", "Start Time", "Wait Time", "Turnaround", "Norm Turnaround", "Status")
        self.process_tree = ttk.Treeview(process_status_frame, columns=proc_status_cols, show='headings', height=8)
        for col in proc_status_cols:
            anchor = tk.W if col == "Status" else tk.CENTER
            width = 60
            if col == "Status": width = 80
            if col == "Norm Turnaround": width = 100
            if col == "Turnaround": width = 80
            self.process_tree.heading(col, text=col)
            self.process_tree.column(col, width=width, anchor=anchor)
        process_scroll_y = ttk.Scrollbar(process_status_frame, orient=tk.VERTICAL, command=self.process_tree.yview)
        self.process_tree.configure(yscrollcommand=process_scroll_y.set)
        process_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.process_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


        # == Timeline/Log (Shows FINAL timeline) ==
        timeline_frame = ttk.LabelFrame(right_frame, text="Final Execution Timeline", padding="5")
        timeline_frame.grid(row=4, column=0, columnspan=2, pady=5, sticky="nsew")
        timeline_frame.rowconfigure(0, weight=1)
        timeline_frame.columnconfigure(0, weight=1)
        # ... (Timeline ScrolledText - same as previous version)
        self.timeline_text = scrolledtext.ScrolledText(timeline_frame, height=6, width=80, wrap=tk.NONE, font=('Courier New', 9))
        self.timeline_text.pack(fill=tk.BOTH, expand=True)
        self.timeline_text.configure(state=tk.DISABLED)


    # --- GUI Action Handlers ---

    def _validate_entry(self, entry_widget, name, is_int=True, allow_empty=False, allow_negative=False, must_be_positive=False):
        # ... (Validation helper - same as previous version) ...
        val_str = entry_widget.get()
        if not val_str:
            if allow_empty: return None
            else: raise ValueError(f"{name} cannot be empty.")
        try:
            val = int(val_str) if is_int else float(val_str)
            if not allow_negative and val < 0: raise ValueError(f"{name} cannot be negative.")
            if must_be_positive and val <= 0: raise ValueError(f"{name} must be positive.")
            return val
        except ValueError: raise ValueError(f"Invalid {name}: Please enter a valid {'integer' if is_int else 'number'}.")

    def _add_process_gui(self):
        if self.simulation_running: return # Prevent changes during the freeze
        try:
            # Calculate next PID automatically
            next_pid = len(self.simulator_logic.processes) + 1

            arrival = self._validate_entry(self.arrival_entry, "Arrival Time", allow_negative=False)
            burst = self._validate_entry(self.burst_entry, "Burst Time", must_be_positive=True)

            # No need to check for duplicate PID if always generated sequentially

            self.simulator_logic.add_process(pid=next_pid, arrival=arrival, burst=burst)
            print(f"Process {next_pid} added.")

            # Clear only arrival and burst entries
            self.arrival_entry.delete(0, tk.END)
            self.burst_entry.delete(0, tk.END)

            self._update_process_table_initial() # Update table showing added processes
            self._update_button_states()
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))

    def _add_processor_gui(self):
        if self.simulation_running: return # Prevent changes during the freeze
        try:
            # Calculate next Processor ID automatically
            next_proc_id = len(self.simulator_logic.processors) + 1

            proc_type = self.proc_type_var.get()
            time_q = self._validate_entry(self.time_q_entry, "Time Quantum", must_be_positive=True, allow_empty=True) # Allow empty for non-RR

            # No need to check for duplicate ID if always generated sequentially

            self.simulator_logic.add_processor(id=next_proc_id, type=proc_type, time_quantum=time_q)
            print(f"Processor {next_proc_id} ({proc_type}) added.")

            # Clear only time quantum entry (type is dropdown)
            self.time_q_entry.delete(0, tk.END)

            self._update_processor_table_initial() # Update table
            self._update_button_states()
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))

    def _on_algorithm_select(self, event=None):
        if self.simulation_running: return # Prevent changes during the freeze

        selected_algo_value = self.algo_var.get()
        try:
            selected_algo_enum = next(st for st in SchedulerType if st.value == selected_algo_value)
            self.simulator_logic.scheduler_type = selected_algo_enum
            print(f"Scheduler type set to: {selected_algo_enum.value}")

            # Enable/disable Time Quantum entry based on RR selection
            is_rr = selected_algo_enum == SchedulerType.RR
            self.time_q_entry.config(state=tk.NORMAL if is_rr else tk.DISABLED)
            if not is_rr: self.time_q_entry.delete(0, tk.END)
        except StopIteration:
             messagebox.showerror("Error", f"Invalid algorithm selected: {selected_algo_value}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")


    def _run_full_simulation(self):
        if self.simulation_running:
            return # Don't start again if already "running" (frozen)

        if not self.simulator_logic.processes:
            messagebox.showinfo("No Processes", "Please add processes before starting.")
            return
        if not self.simulator_logic.processors:
             messagebox.showinfo("No Processors", "Please add processors before starting.")
             return

        self.simulation_running = True
        self._update_button_states()
        self.status_var.set("Running Simulation... GUI will freeze.")
        self.results_var.set("Final Results: Pending...")
        self.root.update_idletasks() # Force GUI update before blocking call

        start_time = time.time()
        try:
            # === THIS IS THE BLOCKING CALL ===
            self.simulator_logic.run() # Calls original simulate()
            # ==================================

            end_time = time.time()
            print(f"Simulation logic finished in {end_time - start_time:.2f} seconds.")

            # --- Simulation is complete, update GUI with FINAL results ---
            self._update_final_display() # Update display using data from completed simulation
            # Access scheduler instance after run() has created it
            final_time = self.simulator_logic.scheduler.current_time if self.simulator_logic.scheduler else "N/A"
            self.status_var.set(f"Simulation Complete (Finished at T={final_time})")

        except ValueError as e:
             messagebox.showerror("Scheduler Error", str(e))
             self.status_var.set("Error during simulation setup.")
        except Exception as e:
             messagebox.showerror("Runtime Error", f"An error occurred during simulation:\n{e}")
             self.status_var.set("Runtime Error during simulation.")
             import traceback
             traceback.print_exc()
        finally:
            # --- Always run this after simulation attempt ---
            self.simulation_running = False
            self._update_button_states()


    def _reset_simulation(self):
        if self.simulation_running: return # Can't reset while frozen

        self.simulator_logic.reset_processes()
        self.simulator_logic.reset_processors()
        self.simulator_logic.scheduler = None
        print("Simulation data reset.")

        # Reset GUI display to initial state
        self._update_display_initial()
        self._update_button_states()


    # --- Display Update ---

    def _clear_treeview(self, tree):
        for item in tree.get_children():
            tree.delete(item)

    def _update_display_initial(self):
        """Sets the GUI to its initial or reset state."""
        self.status_var.set("Idle. Ready to run.")
        self.results_var.set("Final Results: N/A")
        self._update_process_table_initial()
        self._update_processor_table_initial()
        self._clear_timeline()

    def _update_process_table_initial(self):
        """Shows processes added *before* simulation starts."""
        self._clear_treeview(self.process_tree)
        for p in self.simulator_logic.processes:
            # Display initial state before simulation
            values = [p.pid, p.arrival, p.burst, p.burst, "-", 0, "-", "-", "Pending"]
            self.process_tree.insert('', tk.END, values=values)

    def _update_processor_table_initial(self):
        """Shows processors added *before* simulation starts."""
        self._clear_treeview(self.proc_tree)
        for p in self.simulator_logic.processors:
             # Display initial state
             values = [p.id, p.type, "OFF", "-", p.time_quantum if p.time_quantum_original is not None else "-", "0.0"]
             self.proc_tree.insert('', tk.END, values=values)

    def _clear_timeline(self):
        self.timeline_text.config(state=tk.NORMAL)
        self.timeline_text.delete('1.0', tk.END)
        self.timeline_text.config(state=tk.DISABLED)

    def _update_final_display(self):
        """Update GUI elements with FINAL data after simulation completes."""
        # Check if simulation actually ran and created a scheduler instance
        if not self.simulator_logic.scheduler:
            messagebox.showwarning("Update Error", "Simulation did not run or failed to initialize scheduler. Cannot display final results.")
            return

        scheduler = self.simulator_logic.scheduler

        # --- Final Process Status ---
        self._clear_treeview(self.process_tree)
        # Iterate directly through the final process list from the scheduler
        for p in scheduler.processes:
            status = "Completed" if p.is_completed() else "Incomplete?" # Should all be completed after simulate()
            values = [
                p.pid,
                p.arrival,
                p.burst,
                p.remaining_time, # Should be 0 if completed
                p.start_time if p.start_time is not None else "-",
                p.wait_time,
                p.turnaround_time if p.turnaround_time is not None else "-",
                f"{p.normalized_turnaround_time:.2f}" if p.normalized_turnaround_time is not None else "-",
                status
            ]
            self.process_tree.insert('', tk.END, values=values)


        # --- Final Processor Status ---
        self._clear_treeview(self.proc_tree)
        # Iterate directly through the final processor list from the scheduler
        for proc in scheduler.processors_info:
            # Determine final power state based on attributes (heuristic)
            # BaseScheduler might not explicitly track final ON/OFF state if idle.
            # Assume OFF if not processing anything at the very end.
            power_state = "ON" if proc.current_process else "OFF"
            # If BaseScheduler's processor_power_off was called, PowerOn might be False
            if hasattr(proc, 'PowerOn') and not proc.PowerOn:
                power_state = "OFF"

            values = [
                proc.id,
                proc.type,
                power_state,
                proc.current_process.pid if proc.current_process else "-", # Should be None
                proc.time_quantum if proc.time_quantum_original is not None else "-", # Display last value or original? Here, last.
                f"{proc.used_power:.1f}" # Final used power
            ]
            self.proc_tree.insert('', tk.END, values=values)


        # --- Final Timeline ---
        self._update_final_timeline_display() # Uses data stored during the run

        # --- Final Metrics ---
        try:
            # Manually calculate final metrics from the scheduler's state
            if hasattr(scheduler, 'processes') and scheduler.processes:
                 completed_procs = [p for p in scheduler.processes if p.is_completed()]
                 if completed_procs: # Avoid division by zero if no processes completed
                     total_ntt = sum(p.normalized_turnaround_time for p in completed_procs if p.normalized_turnaround_time is not None)
                     avg_ntt = total_ntt / len(completed_procs)
                 else:
                     avg_ntt = 0.0

                 total_power = sum(p.used_power for p in scheduler.processors_info)
                 result_text = f"Avg NTT: {avg_ntt:.2f}, Total Power: {total_power:.1f}"
            else:
                 result_text = "Calculation Error (No process data)"

            self.results_var.set(f"Final Results: {result_text}")
        except Exception as calc_err:
             print(f"Error calculating final metrics: {calc_err}")
             self.results_var.set("Final Results: Calculation Error")


    def _update_final_timeline_display(self):
        """ Displays the timeline data stored in processor.process_queue AFTER simulation. """
        if not self.simulator_logic.scheduler:
            return

        scheduler = self.simulator_logic.scheduler
        max_time = scheduler.current_time # Final time
        timeline = {}

        # Ensure processors_info exists and has data
        if not hasattr(scheduler, 'processors_info') or not scheduler.processors_info:
             self.timeline_text.config(state=tk.NORMAL)
             self.timeline_text.delete('1.0', tk.END)
             self.timeline_text.insert(tk.END, "No processor data available for timeline.")
             self.timeline_text.config(state=tk.DISABLED)
             return

        for p in scheduler.processors_info:
            # Pad the stored queue to the final simulation time with idle symbol (0 or '.')
            # Check if process_queue exists and is a list
            proc_queue = getattr(p, 'process_queue', [])
            if not isinstance(proc_queue, list): proc_queue = []

            # Pad with 0 (idle)
            padded_queue = proc_queue[:] + [0] * (max_time - len(proc_queue))
            timeline[p.id] = padded_queue[:max_time] # Ensure correct length

        self.timeline_text.config(state=tk.NORMAL)
        self.timeline_text.delete('1.0', tk.END)

        if max_time <= 0: # Changed condition to handle time 0 correctly
             self.timeline_text.insert(tk.END, "Simulation finished at or before time 0.")
             self.timeline_text.config(state=tk.DISABLED)
             return

        # Header
        header = "CPU |"
        cell_width = 3
        # Display time steps from 0 up to max_time - 1
        for t in range(max_time):
            header += f"{str(t).rjust(cell_width)}"
        self.timeline_text.insert(tk.END, header + "\n")
        self.timeline_text.insert(tk.END, "-" * len(header) + "\n")

        # Processor Rows
        sorted_proc_ids = sorted(timeline.keys())
        for proc_id in sorted_proc_ids:
            row = f"{str(proc_id).ljust(3)} |"
            proc_timeline = timeline[proc_id]
            for pid in proc_timeline:
                # Use 0 or '.' for idle, PID otherwise
                cell = str(pid) if pid != 0 else "."
                row += f"{cell.rjust(cell_width)}"
            self.timeline_text.insert(tk.END, row + "\n")

        self.timeline_text.config(state=tk.DISABLED)


    def _update_button_states(self):
        """Enable/disable buttons based on whether simulation is 'running' (frozen)."""
        is_idle = not self.simulation_running
        # Can start only if idle and has processes AND processors
        can_start = is_idle and bool(self.simulator_logic.processes) and bool(self.simulator_logic.processors)

        self.start_button.config(state=tk.NORMAL if can_start else tk.DISABLED)
        self.reset_button.config(state=tk.NORMAL if is_idle else tk.DISABLED)
        self.add_proc_button.config(state=tk.NORMAL if is_idle else tk.DISABLED)
        self.add_cpu_button.config(state=tk.NORMAL if is_idle else tk.DISABLED)
        self.algo_combo.config(state='readonly' if is_idle else tk.DISABLED)

        if is_idle:
             # Re-check time quantum entry state when idle
             self._on_algorithm_select()


# --- Main Application Runner ---
if __name__ == "__main__":
    root = tk.Tk()
    app = SimulationGUI(root)
    root.mainloop()