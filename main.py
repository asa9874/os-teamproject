from core.process import Process
def main():
    processes = [
        Process(pid=1, arrival=0, burst=5),
        Process(pid=2, arrival=2, burst=8),
        Process(pid=3, arrival=4, burst=6)
    ]
    

if __name__ == '__main__':
    main()