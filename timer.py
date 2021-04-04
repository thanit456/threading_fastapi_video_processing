import time 

class Timer: 
    def __init__(self, period=30):
        self.start_time = time.time()
        self.period = period
        time.sleep(2)

    def count(self):
        diff_time = time.time() - self.start_time
        if diff_time >= self.period:
            return False, None 
        print(int(diff_time))
        return True, int(diff_time)