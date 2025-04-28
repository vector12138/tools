# 导入必要的模块
import os
import time
import queue
import uuid
from threading import Thread, Event, RLock

from .logger import Logger

# 定义任务池类，继承自 Thread 类
class TaskPool(Thread):
    
    # 内部类，用于表示任务
    class Task:
        """表示任务池中的一个任务。"""
        def __init__(self, id, priority, func, args):
            """初始化任务对象。
            
            Args:
                id (str): 任务的唯一 ID。
                priority (int): 任务的优先级。
                func (callable): 任务要执行的函数。
                args: 传递给函数的参数。
            """
            self.id = id  # 任务的唯一ID
            self.priority = priority
            self.func = func
            self.args = args
            self.timestamp = time.time()

        def __lt__(self, other):
            """自定义比较规则，用于优先级队列。"""
            # 自定义比较规则
            if self.priority == other.priority:
                return self.timestamp < other.timestamp
            return self.priority < other.priority

        def execute(self):
            """执行任务。"""
            try:
                self.func(self.args)
            except Exception as e:
                self.__class__.__logger.info(f"任务 {self.id} 执行出错: {e}")

    def __init__(self, pool_size:int=2, max_pool_size:int=3, max_queue_cnt:int=100, logfile:str='./taskpool.log'):
        """初始化任务池。
        
        Args:
            pool_size (int): 初始线程池大小，默认值为 2。
            max_pool_size (int): 最大线程池大小，默认值为 3。
            max_queue_cnt (int): 任务队列的最大容量，默认值为 100。
            logfile (str): 日志文件路径，默认值为 './taskpool.log'。
        """
        super().__init__()
        self.name = 'taskpool'
        if pool_size < 1:
            raise ValueError("pool size must >= 1")
        if max_pool_size <= pool_size:
            max_pool_size = pool_size + 1
        self.__pool_size = pool_size
        self.__max_pool_size = max_pool_size
        self.__max_queue_cnt = max_queue_cnt
        self.__queue = queue.PriorityQueue(max_queue_cnt)
        # 终止线程队列
        self.__stop_queue = queue.Queue(max_pool_size)
        self.__tasks_rlock = RLock()
        self.__tasks_dict = {}
        for i in range(max_pool_size):
            self.__tasks_dict[i] = {}
            self.__tasks_dict[i]['state'] = 'stop'
        self.__stop_event = Event()
        self.__active_tasks = 0
        # 日志
        logfile_path = os.path.abspath(logfile)
        self.__logger = Logger('taskpool', logfile)

    @classmethod
    def __task_loop(cls, para):
        """任务线程的主循环函数。
        
        Args:
            para (dict): 包含线程所需参数的字典。
        """
        which = para.get('which', None)
        name = para.get('name', None)
        task_queue = para.get('task_queue', None)
        stop_event = para.get('stop_event', None)
        stop_queue = para.get('stop_queue', None)
        logger = para.get('logger', None)
        logger.info(f"任务线程 {name} 已启动")
        free_cnt = 0
        while not stop_event.is_set():
            try:
                if task_queue.empty():
                    time.sleep(1)
                    free_cnt += 1
                    # 空闲等待 x 次释放线程
                    if free_cnt > 60:
                        stop_queue.put(which)
                        break
                    continue
                free_cnt = 0
                task = task_queue.get(timeout=1)
                logger.info(f"任务 {task.id} 已启动")
                task.execute()
                logger.info(f"任务 {task.id} 已完成")
                task_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.info(f"任务线程 {name} 出现异常: {e}")

        logger.info(f"任务线程 {name} 已结束")

    def addTask(self, func, args, priority=7):
        """向任务池添加新任务。
        
        Args:
            func (callable): 任务要执行的函数。
            args: 传递给函数的参数。
            priority (int): 任务的优先级，默认值为 7。
        
        Returns:
            str or None: 任务的唯一 ID，如果队列已满则返回 None。
        """
        try:
            # 使用 uuid 生成不重复的 task_id
            id = uuid.uuid4().hex
            task = TaskPool.Task(id, priority, func, args)
            with self.__tasks_rlock:
                if self.__active_tasks < self.__pool_size:
                    for i in range(self.__pool_size):
                        if self.__tasks_dict[i]['state'] == 'stop':
                            # 有空闲的线程则创建
                            name = f'thread-loop-{i}'
                            stop_event = Event()
                            para = {
                                'which': i,
                                'name': name,
                                'task_queue': self.__queue,
                                'stop_event': stop_event,
                                'stop_queue': self.__stop_queue,
                                'logger': self.__logger
                            }
                            thread = Thread(name=name, target=TaskPool.__task_loop, args=(para,), daemon=True)
                            self.__tasks_dict[i]['name'] = name
                            self.__tasks_dict[i]['thread'] = thread
                            self.__tasks_dict[i]['stop_event'] = stop_event
                            self.__tasks_dict[i]['state'] = 'run'
                            thread.start()
                            self.__active_tasks += 1
                            break

            self.__queue.put(task, block=True, timeout=1)
            return id
        except queue.Full:
            self.__logger.info("任务队列已满，无法添加新任务")
            return None

    def run(self):
        """任务池的主运行循环。"""
        self.__logger.info("任务池已启动")
        while not self.__stop_event.is_set():
            try:
                if self.__stop_queue.empty():
                    time.sleep(1)
                    continue
                which = self.__stop_queue.get()
                with self.__tasks_rlock:
                    self.__tasks_dict[which]['thread'].join()
                    self.__tasks_dict[which]['state'] = 'stop'
                    del self.__tasks_dict[which]['thread']
                    self.__stop_queue.task_done()
                    name = self.__tasks_dict[which]['name']
                    self.__logger.info(f"任务线程 {name} 空闲已释放")
                    self.__active_tasks -= 1
            except:
                pass 
        self.__logger.info("任务池已结束")

    def stop(self):
        """停止任务池，等待所有任务完成。"""
        with self.__tasks_rlock:
            for which, task_info in self.__tasks_dict.items():
                if 'stop_event' in task_info:
                    task_info['stop_event'].set()
                if 'thread' in task_info:
                    task_info['thread'].join()
                    self.__active_tasks -= 1
        self.__queue.join()
        self.__stop_event.set()
        self.__stop_queue.join()
        self.__logger.info("所有任务线程已停止")

    def join(self):
        """等待任务池中的所有任务完成。"""
        while self.__active_tasks > 0:
            time.sleep(1)
        super().join()

if __name__ == '__main__':
    def test(args):
        """测试函数。"""
        cnt = args['cnt']
        print(f'当前输出 {cnt}')

    task_manage = TaskPool(4, 10, logfile='./logs/taskpool.log')
    for i in range(10):
        task_manage.addTask(test, {'cnt': i})

    task_manage.start()
    time.sleep(5)  # 让任务运行一段时间
    task_manage.stop()
    task_manage.join()
    print("主线程结束")