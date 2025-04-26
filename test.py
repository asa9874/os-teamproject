import unittest
from core import Process, Processor
from algorithm import FCFSSceduler

class TestFCFSScheduler(unittest.TestCase):
    def setUp(self):
        self.processes = [
            Process(pid=1, arrival=0, burst=3),
            Process(pid=2, arrival=1, burst=7),
            Process(pid=3, arrival=3, burst=2),
            Process(pid=4, arrival=5, burst=5),
            Process(pid=5, arrival=6, burst=3),
        ]
        self.processors = [
            Processor(id=1, type="E"),  # P or E
        ]
        self.scheduler = FCFSSceduler(self.processes, self.processors)

    def test_fcfs(self):
        while self.scheduler.hasNext():
            self.scheduler.ready_queue_update()
            self.scheduler.schedule()
            self.scheduler.assign_process()
            self.scheduler.processor_power_off()
            self.scheduler.process_waiting_time_update()
            self.scheduler.log_state()
            self.scheduler.update_current_time()
        
        processors = self.scheduler.get_processors()
        processes = self.scheduler.get_proccesss()
        
        self.assertEqual(processes[0].turnaround_time, 3)  
        self.assertEqual(processes[1].turnaround_time, 9)  
        self.assertEqual(processes[2].turnaround_time, 9)  
        self.assertEqual(processes[3].turnaround_time, 12) 
        self.assertEqual(processes[4].turnaround_time, 14) 
        
        self.assertEqual(processes[0].wait_time, 0)  
        self.assertEqual(processes[1].wait_time, 2)  
        self.assertEqual(processes[2].wait_time, 7)  
        self.assertEqual(processes[3].wait_time, 7)  
        self.assertEqual(processes[4].wait_time, 11) 
        
        self.assertEqual(processors[0].used_power, 0.1 + 1 *20)      

    def test_rr(self):
        pass
    
    def test_spn(self):
        pass
    
    def test_sptn(self):
        pass
    
    def test_hrrn(self):
        pass
    
    def test_custom(self):
        pass
    
        

if __name__ == '__main__':
    unittest.main()