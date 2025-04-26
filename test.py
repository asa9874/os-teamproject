import unittest
from core import Process, Processor
from simulator import SchedulerApp  
from scheduler import SchedulerType

class TestSchedulerApp(unittest.TestCase):
    def setUp(self):
        # 공통 테스트 데이터(ppt 교안 데이터)
        self.processes = [
            Process(pid=1, arrival=0, burst=3),
            Process(pid=2, arrival=1, burst=7),
            Process(pid=3, arrival=3, burst=2),
            Process(pid=4, arrival=5, burst=5),
            Process(pid=5, arrival=6, burst=3),
        ]
        self.processors = [
            Processor(id=1, type="E"),
        ]

    def test_fcfs(self):
        app = SchedulerApp(scheduler_type=SchedulerType.FCFS)
        app.add_processes(self.processes)
        app.add_processors(self.processors)
        app.run()

        processes = app.scheduler.get_process()
        processors = app.scheduler.get_processors()

        # turnaround_time 테스트
        self.assertEqual(processes[0].turnaround_time, 3)
        self.assertEqual(processes[1].turnaround_time, 9)
        self.assertEqual(processes[2].turnaround_time, 9)
        self.assertEqual(processes[3].turnaround_time, 12)
        self.assertEqual(processes[4].turnaround_time, 14)

        # wait_time 테스트
        self.assertEqual(processes[0].wait_time, 0)
        self.assertEqual(processes[1].wait_time, 2)
        self.assertEqual(processes[2].wait_time, 7)
        self.assertEqual(processes[3].wait_time, 7)
        self.assertEqual(processes[4].wait_time, 11)

        # processor used_power 테스트
        self.assertEqual(processors[0].used_power, 0.1 + 1 * 20)

    def test_rr(self):
        while self.scheduler.hasNext():
            self.scheduler.ready_queue_update()
            self.scheduler.schedule()
            self.scheduler.assign_process()
            self.scheduler.processor_power_off()
            self.scheduler.process_waiting_time_update()
            self.scheduler.log_state()
            self.scheduler.update_current_time()
        
        processors = self.scheduler.get_processors()
        processes = self.scheduler.get_process()
        
        self.assertEqual(processes[0].turnaround_time, 5)  
        self.assertEqual(processes[1].turnaround_time, 18)  
        self.assertEqual(processes[2].turnaround_time, 4)  
        self.assertEqual(processes[3].turnaround_time, 15) 
        self.assertEqual(processes[4].turnaround_time, 12) 
        
        self.assertEqual(processes[0].wait_time, 2)  
        self.assertEqual(processes[1].wait_time, 11)  
        self.assertEqual(processes[2].wait_time, 2)  
        self.assertEqual(processes[3].wait_time, 10)  
        self.assertEqual(processes[4].wait_time, 9) 
        
        self.assertEqual(processors[0].used_power, 0.1 + 1 *20) 
    
    def test_rr(self): 
        app = SchedulerApp(scheduler_type=SchedulerType.RR)
        # time_quantum있는 프로세서 추가
        app.add_processes(self.processes)
        app.add_processor(id=1, type="E", time_quantum=2)
        app.run()

        processes = app.scheduler.get_process()
        processors = app.scheduler.get_processors()

        # turnaround_time 테스트
        self.assertEqual(processes[0].turnaround_time, 5)
        self.assertEqual(processes[1].turnaround_time, 18)
        self.assertEqual(processes[2].turnaround_time, 4)
        self.assertEqual(processes[3].turnaround_time, 15)
        self.assertEqual(processes[4].turnaround_time, 12)

        # wait_time 테스트
        self.assertEqual(processes[0].wait_time, 2)
        self.assertEqual(processes[1].wait_time, 11)
        self.assertEqual(processes[2].wait_time, 2)
        self.assertEqual(processes[3].wait_time, 10)
        self.assertEqual(processes[4].wait_time, 9)

        # processor used_power 테스트
        self.assertEqual(processors[0].used_power, ) # 계산후 추가해주세요

    def test_spn(self):
        app = SchedulerApp(scheduler_type=SchedulerType.SPN)
        app.add_processes(self.processes)
        app.add_processors(self.processors)
        app.run()

        processes = app.scheduler.get_process()
        processors = app.scheduler.get_processors()

        # turnaround_time 테스트
        self.assertEqual(processes[0].turnaround_time, 3)
        self.assertEqual(processes[1].turnaround_time, 19)
        self.assertEqual(processes[2].turnaround_time, 2)
        self.assertEqual(processes[3].turnaround_time, 5)
        self.assertEqual(processes[4].turnaround_time, 7)

        # wait_time 테스트
        self.assertEqual(processes[0].wait_time, 0)
        self.assertEqual(processes[1].wait_time, 12)
        self.assertEqual(processes[2].wait_time, 0)
        self.assertEqual(processes[3].wait_time, 0)
        self.assertEqual(processes[4].wait_time, 4)

        # processor used_power 테스트
        self.assertEqual(processors[0].used_power, ) # 계산후 추가해주세요

    def test_sptn(self):
        app = SchedulerApp(scheduler_type=SchedulerType.SPTN)
        app.add_processes(self.processes)
        app.add_processors(self.processors)
        app.run()
        
        processes = app.scheduler.get_process()
        processors = app.scheduler.get_processors()

        # turnaround_time 테스트
        self.assertEqual(processes[0].turnaround_time, ) # 계산후 추가해주세요
        self.assertEqual(processes[1].turnaround_time, ) # 계산후 추가해주세요
        self.assertEqual(processes[2].turnaround_time, ) # 계산후 추가해주세요
        self.assertEqual(processes[3].turnaround_time, ) # 계산후 추가해주세요
        self.assertEqual(processes[4].turnaround_time, ) # 계산후 추가해주세요

        # wait_time 테스트
        self.assertEqual(processes[0].wait_time, ) # 계산후 추가해주세요
        self.assertEqual(processes[1].wait_time, ) # 계산후 추가해주세요
        self.assertEqual(processes[2].wait_time, ) # 계산후 추가해주세요
        self.assertEqual(processes[3].wait_time, ) # 계산후 추가해주세요
        self.assertEqual(processes[4].wait_time, ) # 계산후 추가해주세요

        # processor used_power 테스트
        self.assertEqual(processors[0].used_power, ) # 계산후 추가해주세요

    def test_hrrn(self):
        app = SchedulerApp(scheduler_type=SchedulerType.HRRN)
        app.add_processes(self.processes)
        app.add_processors(self.processors)
        app.run()

        processes = app.scheduler.get_process()
        processors = app.scheduler.get_processors()

        # turnaround_time 테스트
        self.assertEqual(processes[0].turnaround_time, 3)
        self.assertEqual(processes[1].turnaround_time, 9)
        self.assertEqual(processes[2].turnaround_time, 9)
        self.assertEqual(processes[3].turnaround_time, 15)
        self.assertEqual(processes[4].turnaround_time, 9)

        # wait_time 테스트
        self.assertEqual(processes[0].wait_time, 0)
        self.assertEqual(processes[1].wait_time, 2)
        self.assertEqual(processes[2].wait_time, 7)
        self.assertEqual(processes[3].wait_time, 10)
        self.assertEqual(processes[4].wait_time, 6)

        # processor used_power 테스트
        self.assertEqual(processors[0].used_power, )# 계산후 추가해주세요

    def test_custom(self):
        app = SchedulerApp(scheduler_type=SchedulerType.CUSTOM)
        app.add_processes(self.processes)
        app.add_processors(self.processors)
        app.run()

        processes = app.scheduler.get_process()
        processors = app.scheduler.get_processors()

        # turnaround_time 테스트
        self.assertEqual(processes[0].turnaround_time, ) # 계산후 추가해주세요
        self.assertEqual(processes[1].turnaround_time, ) # 계산후 추가해주세요
        self.assertEqual(processes[2].turnaround_time, ) # 계산후 추가해주세요
        self.assertEqual(processes[3].turnaround_time, ) # 계산후 추가해주세요
        self.assertEqual(processes[4].turnaround_time, ) # 계산후 추가해주세요

        # wait_time 테스트
        self.assertEqual(processes[0].wait_time, ) # 계산후 추가해주세요
        self.assertEqual(processes[1].wait_time, ) # 계산후 추가해주세요
        self.assertEqual(processes[2].wait_time, ) # 계산후 추가해주세요
        self.assertEqual(processes[3].wait_time, ) # 계산후 추가해주세요
        self.assertEqual(processes[4].wait_time, ) # 계산후 추가해주세요

        # processor used_power 테스트
        self.assertEqual(processors[0].used_power, ) # 계산후 추가해주세요


if __name__ == '__main__':
    choice = input("실행할 스케줄러 입력 (fcfs, rr, spn, hrrn, sptn, custom, all): ").strip().lower()
    
    suite = unittest.TestSuite()

    if choice == 'fcfs':
        suite.addTest(TestSchedulerApp('test_fcfs'))
    elif choice == 'rr':
        suite.addTest(TestSchedulerApp('test_rr'))
    elif choice == 'spn':
        suite.addTest(TestSchedulerApp('test_spn'))
    elif choice == 'hrrn':
        suite.addTest(TestSchedulerApp('test_hrrn'))
    elif choice == 'sptn':
        suite.addTest(TestSchedulerApp('test_sptn'))
    elif choice == 'custom':
        suite.addTest(TestSchedulerApp('test_custom'))
    else:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestSchedulerApp)

    runner = unittest.TextTestRunner()
    runner.run(suite)