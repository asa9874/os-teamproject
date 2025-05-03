from core import Process
from core import Processor
from scheduler import CustomScheduler
from simulator import SchedulerApp
from scheduler import SchedulerType
from visualization import SchedulerGUI, SchedulerGUI2


# 시간기준은 시작을 기준임 
# 현재 시간: 0초 -> 0초에 프로세스 할당끝난시점,시동전력 포함
# 현재 시간: 1초 -> 1초에 프로세스 끝,프로세스 할당끝난시점, 0초 단계 사용전략 포함
def main():
    app_gui = SchedulerGUI()
    app_gui.mainloop() # Tkinter 이벤트 루프 시작
    



if __name__ == '__main__':
    main()