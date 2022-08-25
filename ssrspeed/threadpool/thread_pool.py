from ssrspeed.threadpool.work_thread import WorkThread


class ThreadPool:
    def __init__(self, maxsize, tasklist):
        if maxsize < 0:
            raise ValueError("Thread must be more than 0.")

        self.tasklist = tasklist
        self.work_threads = []

        for i in range(maxsize):
            work_thread = WorkThread(self.tasklist)
            self.work_threads.append(work_thread)
            work_thread.start()

    def join(self):
        self.tasklist.join()
        for work_thread in self.work_threads:
            work_thread.dismiss()

    def is_over(self):
        return self.tasklist.empty()
