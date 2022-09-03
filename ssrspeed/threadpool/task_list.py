from queue import Queue

_pool_size = 15
TASK_LIST: Queue = Queue(maxsize=_pool_size)
