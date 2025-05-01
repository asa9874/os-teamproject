from enum import Enum

class SchedulerType(Enum):
    FCFS = "fcfs"
    RR = "rr"
    SPN = "spn"
    HRRN = "hrrn"
    SRTN = "srtn"
    CUSTOM = "custom"
