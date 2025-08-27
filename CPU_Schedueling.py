import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv, json
from collections import deque

# --- PROCESS CLASS ---
class Process:
    def __init__(self, pid, arrival, burst, priority=0):
        self.pid = pid
        self.arrival = int(arrival)
        self.burst = int(burst)
        self.remaining = int(burst)
        self.priority = int(priority)
        self.start = None
        self.completion = None

# --- CPU SCHEDULER GUI ---
class CPUSchedulerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CPU Scheduling Simulator")
        self.processes = []
        self.algorithms = ["FCFS", "SJF", "SRT", "RR", "MLFQ"]

        # Input Frame
        input_frame = tk.LabelFrame(root, text="Add Process")
        input_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(input_frame, text="PID").grid(row=0, column=0)
        tk.Label(input_frame, text="Arrival").grid(row=0, column=1)
        tk.Label(input_frame, text="Burst").grid(row=0, column=2)
        self.pid_entry = tk.Entry(input_frame, width=10)
        self.arrival_entry = tk.Entry(input_frame, width=10)
        self.burst_entry = tk.Entry(input_frame, width=10)
        self.pid_entry.grid(row=1, column=0)
        self.arrival_entry.grid(row=1, column=1)
        self.burst_entry.grid(row=1, column=2)
        tk.Button(input_frame, text="Add", command=self.add_process).grid(row=1, column=3, padx=5)
        tk.Button(input_frame, text="Load File", command=self.load_file).grid(row=1, column=4, padx=5)

        # Process List
        self.process_listbox = tk.Listbox(root, height=5)
        self.process_listbox.pack(fill="x", padx=10, pady=5)

        # Options Frame
        options_frame = tk.LabelFrame(root, text="Options")
        options_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(options_frame, text="Algorithm:").grid(row=0, column=0)
        self.algo_var = tk.StringVar(value=self.algorithms[0])
        ttk.Combobox(options_frame, textvariable=self.algo_var, values=self.algorithms, state="readonly").grid(row=0, column=1)
        tk.Label(options_frame, text="Quantum (RR/MLFQ):").grid(row=0, column=2)
        self.quantum_entry = tk.Entry(options_frame, width=5)
        self.quantum_entry.insert(0, "2")
        self.quantum_entry.grid(row=0, column=3)
        tk.Button(options_frame, text="Run", command=self.run_scheduler).grid(row=0, column=4, padx=5)
        tk.Button(options_frame, text="Save Results", command=self.save_results).grid(row=0, column=5, padx=5)

        # Gantt Chart
        gantt_frame = tk.LabelFrame(root, text="Gantt Chart")
        gantt_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.gantt_canvas = tk.Canvas(gantt_frame, height=80, bg="white")
        self.gantt_canvas.pack(fill="both", expand=True)

        # Results Table
        table_frame = tk.LabelFrame(root, text="Results")
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.tree = ttk.Treeview(table_frame, columns=("PID", "Waiting", "Turnaround", "Response"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True)

    # --- PROCESS MANAGEMENT ---
    def add_process(self):
        pid = self.pid_entry.get()
        arrival = self.arrival_entry.get()
        burst = self.burst_entry.get()
        if not pid or not arrival or not burst:
            messagebox.showwarning("Input Error", "Please fill all fields")
            return
        p = Process(pid, arrival, burst)
        self.processes.append(p)
        self.process_listbox.insert(tk.END, f"{pid} - Arrival: {arrival}, Burst: {burst}")

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json")])
        if not file_path:
            return
        try:
            if file_path.endswith(".csv"):
                with open(file_path, newline="") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        p = Process(row["PID"], row["Arrival"], row["Burst"], row.get("Priority", 0))
                        self.processes.append(p)
                        self.process_listbox.insert(tk.END, f"{p.pid} - Arrival: {p.arrival}, Burst: {p.burst}")
            elif file_path.endswith(".json"):
                with open(file_path) as f:
                    data = json.load(f)
                    for row in data:
                        p = Process(row["PID"], row["Arrival"], row["Burst"], row.get("Priority", 0))
                        self.processes.append(p)
                        self.process_listbox.insert(tk.END, f"{p.pid} - Arrival: {p.arrival}, Burst: {p.burst}")
        except Exception as e:
            messagebox.showerror("File Error", str(e))

    def save_results(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json")])
        if not file_path:
            return
        try:
            results = [self.tree.item(child)["values"] for child in self.tree.get_children()]
            if file_path.endswith(".csv"):
                with open(file_path, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["PID", "Waiting", "Turnaround", "Response"])
                    writer.writerows(results)
            else:
                json_data = [{"PID": r[0], "Waiting": r[1], "Turnaround": r[2], "Response": r[3]} for r in results]
                with open(file_path, "w") as f:
                    json.dump(json_data, f, indent=4)
            messagebox.showinfo("Success", f"Results saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    # --- SIMULATION ---
    def run_scheduler(self):
        if not self.processes:
            messagebox.showwarning("No Processes", "Please add processes first")
            return
        algo = self.algo_var.get()
        quantum = int(self.quantum_entry.get())
        procs = [Process(p.pid, p.arrival, p.burst, p.priority) for p in self.processes]

        if algo == "FCFS":
            results, gantt = self.fcfs(procs)
        elif algo == "SJF":
            results, gantt = self.sjf(procs)
        elif algo == "SRT":
            results, gantt = self.srt(procs)
        elif algo == "RR":
            results, gantt = self.rr(procs, quantum)
        elif algo == "MLFQ":
            results, gantt = self.mlfq(procs, [2, 4, 8])
        else:
            messagebox.showinfo("Error", f"{algo} not implemented.")
            return

        self.display_gantt(gantt)
        for row in self.tree.get_children():
            self.tree.delete(row)
        for r in results:
            self.tree.insert("", "end", values=r)

    # --- GANTT CHART ---
    def display_gantt(self, gantt):
        self.gantt_canvas.delete("all")
        if not gantt:
            return
        max_time = max([end for _,_,end in gantt])
        width = 800
        scale = width / max_time if max_time > 0 else 1
        x = 0
        for pid, start, end in gantt:
            w = (end - start) * scale
            color = f"#{hex(abs(hash(pid)) % 0xFFFFFF)[2:]:0>6}"
            self.gantt_canvas.create_rectangle(x, 10, x+w, 40, fill=color)
            self.gantt_canvas.create_text(x + w/2, 25, text=pid)
            self.gantt_canvas.create_text(x, 45, text=str(start))
            x += w
        self.gantt_canvas.create_text(x, 45, text=str(gantt[-1][2]))

    # --- ALGORITHMS ---
    def fcfs(self, procs):
        procs.sort(key=lambda p: p.arrival)
        time = 0
        gantt = []
        results = []
        for p in procs:
            if time < p.arrival: time = p.arrival
            p.start = time
            p.completion = time + p.burst
            time += p.burst
            gantt.append((p.pid, p.start, p.completion))
            tat = p.completion - p.arrival
            wt = tat - p.burst
            rt = p.start - p.arrival
            results.append((p.pid, wt, tat, rt))
        return results, gantt

    def sjf(self, procs):
        time = 0
        gantt = []
        results = []
        remaining = procs[:]
        while remaining:
            available = [p for p in remaining if p.arrival <= time]
            if not available:
                time += 1
                continue
            p = min(available, key=lambda x: x.burst)
            p.start = time
            p.completion = time + p.burst
            time += p.burst
            tat = p.completion - p.arrival
            wt = tat - p.burst
            rt = p.start - p.arrival
            results.append((p.pid, wt, tat, rt))
            gantt.append((p.pid, p.start, p.completion))
            remaining.remove(p)
        return results, gantt

    def srt(self, procs):
        time = 0
        gantt = []
        remaining = procs[:]
        last_pid = None
        start_time = None
        results = []
        while remaining:
            available = [p for p in remaining if p.arrival <= time and p.remaining > 0]
            if not available:
                if last_pid is not None:
                    gantt.append((last_pid, start_time, time))
                    last_pid = None
                time += 1
                continue
            current = min(available, key=lambda p: p.remaining)
            if last_pid != current.pid:
                if last_pid is not None:
                    gantt.append((last_pid, start_time, time))
                start_time = time
                last_pid = current.pid
                if current.start is None: current.start = time
            current.remaining -= 1
            time += 1
            if current.remaining == 0:
                current.completion = time
                tat = current.completion - current.arrival
                wt = tat - current.burst
                rt = current.start - current.arrival
                results.append((current.pid, wt, tat, rt))
                remaining.remove(current)
                gantt.append((current.pid, start_time, time))
                last_pid = None
                start_time = None
        return results, gantt

    def rr(self, procs, quantum):
        time = 0
        gantt = []
        queue = deque(sorted(procs, key=lambda p: p.arrival))
        results = []
        while queue:
            p = queue.popleft()
            if p.start is None: p.start = max(time, p.arrival)
            start = max(time, p.arrival)
            run_time = min(quantum, p.remaining)
            p.remaining -= run_time
            end = start + run_time
            gantt.append((p.pid, start, end))
            time = end
            if p.remaining > 0:
                queue.append(p)
            else:
                p.completion = time
                tat = p.completion - p.arrival
                wt = tat - p.burst
                rt = p.start - p.arrival
                results.append((p.pid, wt, tat, rt))
        return results, gantt

    def mlfq(self, procs, quanta=[2,4,8]):
        queues = [deque(), deque(), deque()]
        for p in sorted(procs, key=lambda p: p.arrival):
            queues[0].append(p)
        time = 0
        gantt = []
        results = []
        while any(queues):
            for i, q in enumerate(queues):
                if not q: continue
                p = q.popleft()
                if p.start is None: p.start = max(time, p.arrival)
                start = max(time, p.arrival)
                run_time = min(quanta[i], p.remaining) if i<2 else p.remaining
                p.remaining -= run_time
                end = start + run_time
                gantt.append((p.pid, start, end))
                time = end
                if p.remaining > 0:
                    next_q = queues[i+1] if i < 2 else queues[i]
                    next_q.append(p)
                else:
                    p.completion = time
                    tat = p.completion - p.arrival
                    wt = tat - p.burst
                    rt = p.start - p.arrival
                    results.append((p.pid, wt, tat, rt))
                break
            else:
                time += 1
        return results, gantt

if __name__ == "__main__":
    root = tk.Tk()
    app = CPUSchedulerGUI(root)
    root.mainloop()
