import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque

class Process:
    def __init__(self, pid, arrival, burst, priority=0):
        self.pid = pid
        self.arrival_time = int(arrival)
        self.burst_time = int(burst)
        self.remaining_time = int(burst)
        self.priority = int(priority)
        self.start_time = None
        self.completion_time = None
        self.waiting_time = 0
        self.turnaround_time = 0
        self.response_time = 0

# Simple FCFS for demo
def fcfs(processes):
    processes.sort(key=lambda p: p.arrival_time)
    time = 0
    gantt = []
    for p in processes:
        if time < p.arrival_time:
            time = p.arrival_time
        p.start_time = time
        p.response_time = time - p.arrival_time
        time += p.burst_time
        p.completion_time = time
        p.turnaround_time = time - p.arrival_time
        p.waiting_time = p.turnaround_time - p.burst_time
        gantt.append((p.pid, p.start_time, p.completion_time))
    return gantt, processes

# Add other algorithms here (SJF, RR, SRT, MLFQ) ...

class SchedulerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CPU Scheduling Simulator")
        self.processes = []

        # Input frame
        frame = tk.Frame(root)
        frame.pack(pady=10)

        tk.Label(frame, text="PID").grid(row=0,column=0)
        tk.Label(frame, text="Arrival").grid(row=0,column=1)
        tk.Label(frame, text="Burst").grid(row=0,column=2)
        tk.Label(frame, text="Priority").grid(row=0,column=3)

        self.pid_entry = tk.Entry(frame, width=5)
        self.pid_entry.grid(row=1,column=0)
        self.arrival_entry = tk.Entry(frame, width=5)
        self.arrival_entry.grid(row=1,column=1)
        self.burst_entry = tk.Entry(frame, width=5)
        self.burst_entry.grid(row=1,column=2)
        self.priority_entry = tk.Entry(frame, width=5)
        self.priority_entry.grid(row=1,column=3)

        tk.Button(frame, text="Add Process", command=self.add_process).grid(row=1,column=4)

        # Live process list
        tk.Label(root, text="Process List").pack()
        self.process_table = ttk.Treeview(root, columns=("PID","Arrival","Burst","Priority"), show="headings")
        for col in ["PID","Arrival","Burst","Priority"]:
            self.process_table.heading(col, text=col)
        self.process_table.pack()

        # Algorithm selection
        tk.Label(root, text="Algorithm").pack()
        self.algorithm = ttk.Combobox(root, values=["FCFS"]) # Add other algorithms
        self.algorithm.pack()
        self.algorithm.current(0)

        tk.Label(root, text="Quantum (for RR)").pack()
        self.quantum_entry = tk.Entry(root)
        self.quantum_entry.insert(0,"2")
        self.quantum_entry.pack()

        tk.Button(root, text="Run Simulation", command=self.run_simulation).pack(pady=5)

        # Gantt chart
        tk.Label(root, text="Gantt Chart").pack()
        self.gantt_canvas = tk.Canvas(root, height=50, width=800)
        self.gantt_canvas.pack()

        # Metrics
        tk.Label(root, text="Metrics").pack()
        self.metrics_table = ttk.Treeview(root, columns=("PID","WT","TAT","RT"), show="headings")
        for col in ["PID","WT","TAT","RT"]:
            self.metrics_table.heading(col, text=col)
        self.metrics_table.pack()

    def add_process(self):
        pid = self.pid_entry.get()
        arrival = self.arrival_entry.get()
        burst = self.burst_entry.get()
        priority = self.priority_entry.get() or 0
        if not pid or not arrival or not burst:
            messagebox.showerror("Error","Please fill all required fields")
            return
        proc = Process(pid, arrival, burst, priority)
        self.processes.append(proc)
        # Add to live table
        self.process_table.insert('',tk.END,values=(proc.pid, proc.arrival_time, proc.burst_time, proc.priority))
        # Clear entries
        self.pid_entry.delete(0,'end')
        self.arrival_entry.delete(0,'end')
        self.burst_entry.delete(0,'end')
        self.priority_entry.delete(0,'end')

    def run_simulation(self):
        if not self.processes:
            messagebox.showerror("Error","No processes added")
            return
        alg = self.algorithm.get()
        quantum = int(self.quantum_entry.get() or 2)
        if alg=="FCFS":
            gantt, procs = fcfs(self.processes)
        else:
            messagebox.showerror("Error","Algorithm not implemented")
            return
        self.display_gantt(gantt)
        self.display_metrics(procs)

    def display_gantt(self, gantt):
        self.gantt_canvas.delete("all")
        max_time = max([end for _,_,end in gantt])
        width = 800
        scale = width/max_time
        x=0
        for pid,start,end in gantt:
            w = (end-start)*scale
            color = f"#{hex(hash(pid)%0xFFFFFF)[2:]}"
            self.gantt_canvas.create_rectangle(x,10,x+w,40,fill=color)
            self.gantt_canvas.create_text(x+w/2,25,text=pid)
            x += w

    def display_metrics(self, procs):
        for row in self.metrics_table.get_children():
            self.metrics_table.delete(row)
        for p in procs:
            self.metrics_table.insert('',tk.END,values=(p.pid,p.waiting_time,p.turnaround_time,p.response_time))

if __name__=="__main__":
    root = tk.Tk()
    app = SchedulerGUI(root)
    root.mainloop()
