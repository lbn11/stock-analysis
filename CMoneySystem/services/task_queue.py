"""异步任务队列模块

支持长时间运行的分析任务，避免阻塞主线程
"""
from typing import Dict, List, Any, Callable, Optional
from datetime import datetime
import logging
import threading
import queue
import uuid
import json


class Task:
    """任务对象"""

    def __init__(self, task_id: str, func: Callable, args: tuple = (),
                 kwargs: dict = None, priority: int = 5):
        """
        初始化任务

        Args:
            task_id: 任务ID
            func: 要执行的函数
            args: 位置参数
            kwargs: 关键字参数
            priority: 优先级 (1-10, 数字越小优先级越高)
        """
        self.task_id = task_id
        self.func = func
        self.args = args
        self.kwargs = kwargs or {}
        self.priority = priority
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.status = 'pending'  # pending, running, completed, failed
        self.result = None
        self.error = None

    def __lt__(self, other):
        """用于优先级队列排序"""
        return self.priority < other.priority


class TaskQueue:
    """简单的任务队列实现"""

    def __init__(self, max_workers: int = 3):
        """
        初始化任务队列

        Args:
            max_workers: 最大工作线程数
        """
        self.logger = logging.getLogger(f"TaskQueue")
        self.max_workers = max_workers
        self.queue = queue.PriorityQueue()
        self.tasks: Dict[str, Task] = {}
        self.workers = []
        self.is_running = False

    def submit(self, func: Callable, args: tuple = (), kwargs: dict = None,
               priority: int = 5, task_id: str = None) -> str:
        """
        提交任务到队列

        Args:
            func: 要执行的函数
            args: 位置参数
            kwargs: 关键字参数
            priority: 优先级 (1-10)
            task_id: 任务ID（可选，自动生成UUID）

        Returns:
            任务ID
        """
        if task_id is None:
            task_id = str(uuid.uuid4())

        task = Task(task_id, func, args, kwargs, priority)
        self.tasks[task_id] = task
        self.queue.put(task)

        self.logger.info(f"Task {task_id} submitted with priority {priority}")
        return task_id

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务状态

        Args:
            task_id: 任务ID

        Returns:
            任务状态信息
        """
        if task_id not in self.tasks:
            return {'error': 'Task not found'}

        task = self.tasks[task_id]

        return {
            'task_id': task.task_id,
            'status': task.status,
            'created_at': task.created_at.isoformat() if task.created_at else None,
            'started_at': task.started_at.isoformat() if task.started_at else None,
            'completed_at': task.completed_at.isoformat() if task.completed_at else None,
            'priority': task.priority,
            'result': task.result if task.status == 'completed' else None,
            'error': str(task.error) if task.error else None
        }

    def get_task_result(self, task_id: str, timeout: float = None) -> Any:
        """
        获取任务结果（阻塞等待）

        Args:
            task_id: 任务ID
            timeout: 超时时间（秒）

        Returns:
            任务结果
        """
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")

        task = self.tasks[task_id]

        # 简单轮询实现（实际应该使用条件变量）
        import time
        start_time = time.time()

        while task.status not in ['completed', 'failed']:
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(f"Task {task_id} timeout")

            time.sleep(0.1)

        if task.status == 'failed':
            raise RuntimeError(task.error)

        return task.result

    def start_workers(self):
        """启动工作线程"""
        if self.is_running:
            self.logger.warning("Workers already running")
            return

        self.is_running = True

        for i in range(self.max_workers):
            worker = threading.Thread(target=self._worker_loop, daemon=True)
            worker.name = f"TaskWorker-{i}"
            worker.start()
            self.workers.append(worker)

        self.logger.info(f"Started {self.max_workers} worker threads")

    def stop_workers(self):
        """停止工作线程"""
        self.is_running = False
        self.logger.info("Stopping workers")

    def _worker_loop(self):
        """工作线程循环"""
        while self.is_running:
            try:
                # 获取任务（超时1秒）
                try:
                    task = self.queue.get(timeout=1)
                except queue.Empty:
                    continue

                # 执行任务
                self._execute_task(task)

                # 标记任务完成
                self.queue.task_done()

            except Exception as e:
                self.logger.error(f"Worker error: {e}")

    def _execute_task(self, task: Task):
        """执行单个任务"""
        task.status = 'running'
        task.started_at = datetime.now()

        self.logger.info(f"Executing task {task.task_id}")

        try:
            result = task.func(*task.args, **task.kwargs)
            task.result = result
            task.status = 'completed'
            self.logger.info(f"Task {task.task_id} completed successfully")

        except Exception as e:
            task.error = e
            task.status = 'failed'
            self.logger.error(f"Task {task.task_id} failed: {e}")

        finally:
            task.completed_at = datetime.now()


class AsyncTaskManager:
    """异步任务管理器

    提供更高级的任务管理功能
    """

    def __init__(self, max_workers: int = 3):
        """初始化任务管理器"""
        self.logger = logging.getLogger("AsyncTaskManager")
        self.task_queue = TaskQueue(max_workers)
        self.task_history: Dict[str, Dict] = {}
        self.is_running = False

    def start(self):
        """启动任务管理器"""
        if not self.is_running:
            self.task_queue.start_workers()
            self.is_running = True
            self.logger.info("AsyncTaskManager started")

    def stop(self):
        """停止任务管理器"""
        if self.is_running:
            self.task_queue.stop_workers()
            self.is_running = False
            self.logger.info("AsyncTaskManager stopped")

    def submit_analysis_task(self, stock_code: str, analysis_type: str = 'comprehensive',
                            time_horizon: str = 'medium', priority: int = 5) -> str:
        """
        提交股票分析任务

        Args:
            stock_code: 股票代码
            analysis_type: 分析类型
            time_horizon: 时间范围
            priority: 优先级

        Returns:
            任务ID
        """
        def analysis_task():
            from services.analysis_engine import AnalysisEngine
            engine = AnalysisEngine()
            return engine.analyze(
                stock_code=stock_code,
                analysis_type=analysis_type,
                time_horizon=time_horizon
            )

        task_id = self.task_queue.submit(
            func=analysis_task,
            priority=priority
        )

        # 记录任务历史
        self.task_history[task_id] = {
            'type': 'analysis',
            'stock_code': stock_code,
            'analysis_type': analysis_type,
            'time_horizon': time_horizon,
            'submitted_at': datetime.now().isoformat()
        }

        return task_id

    def submit_prediction_task(self, stock_code: str, time_horizon: str = 'short',
                              priority: int = 5) -> str:
        """
        提交股价预测任务

        Args:
            stock_code: 股票代码
            time_horizon: 时间范围
            priority: 优先级

        Returns:
            任务ID
        """
        def prediction_task():
            from services.prediction_service import PredictionService
            from data.real_collector import RealDataCollector

            collector = RealDataCollector()
            service = PredictionService()

            # 收集数据
            historical_data = collector.collect_stock_data(stock_code).get('historical', [])

            # 预测
            return service.predict(stock_code, historical_data, time_horizon)

        task_id = self.task_queue.submit(
            func=prediction_task,
            priority=priority
        )

        self.task_history[task_id] = {
            'type': 'prediction',
            'stock_code': stock_code,
            'time_horizon': time_horizon,
            'submitted_at': datetime.now().isoformat()
        }

        return task_id

    def submit_batch_analysis_task(self, stock_codes: List[str],
                                   analysis_type: str = 'comprehensive',
                                   priority: int = 5) -> List[str]:
        """
        提交批量分析任务

        Args:
            stock_codes: 股票代码列表
            analysis_type: 分析类型
            priority: 优先级

        Returns:
            任务ID列表
        """
        task_ids = []

        for stock_code in stock_codes:
            task_id = self.submit_analysis_task(stock_code, analysis_type, priority=priority)
            task_ids.append(task_id)

        self.logger.info(f"Submitted {len(task_ids)} batch analysis tasks")
        return task_ids

    def get_all_tasks(self) -> Dict[str, Dict]:
        """获取所有任务状态"""
        all_tasks = {}

        for task_id, task in self.task_queue.tasks.items():
            status = self.task_queue.get_task_status(task_id)

            # 合并任务历史信息
            if task_id in self.task_history:
                status.update(self.task_history[task_id])

            all_tasks[task_id] = status

        return all_tasks

    def get_active_tasks(self) -> Dict[str, Dict]:
        """获取活跃任务（pending 或 running）"""
        all_tasks = self.get_all_tasks()
        return {
            task_id: task
            for task_id, task in all_tasks.items()
            if task.get('status') in ['pending', 'running']
        }

    def get_completed_tasks(self) -> Dict[str, Dict]:
        """获取已完成任务"""
        all_tasks = self.get_all_tasks()
        return {
            task_id: task
            for task_id, task in all_tasks.items()
            if task.get('status') in ['completed', 'failed']
        }

    def clear_completed_tasks(self, older_than_hours: int = 24):
        """
        清理已完成的任务

        Args:
            older_than_hours: 清理多少小时前的任务
        """
        from datetime import timedelta

        cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
        task_ids_to_remove = []

        for task_id, task in self.task_queue.tasks.items():
            if task.status in ['completed', 'failed']:
                if task.completed_at and task.completed_at < cutoff_time:
                    task_ids_to_remove.append(task_id)

        for task_id in task_ids_to_remove:
            del self.task_queue.tasks[task_id]
            if task_id in self.task_history:
                del self.task_history[task_id]

        self.logger.info(f"Cleared {len(task_ids_to_remove)} completed tasks")

    def get_statistics(self) -> Dict[str, Any]:
        """获取任务统计信息"""
        all_tasks = self.get_all_tasks()

        stats = {
            'total_tasks': len(all_tasks),
            'pending': sum(1 for t in all_tasks.values() if t.get('status') == 'pending'),
            'running': sum(1 for t in all_tasks.values() if t.get('status') == 'running'),
            'completed': sum(1 for t in all_tasks.values() if t.get('status') == 'completed'),
            'failed': sum(1 for t in all_tasks.values() if t.get('status') == 'failed'),
            'is_running': self.is_running,
            'max_workers': self.task_queue.max_workers
        }

        return stats


# 全局任务管理器实例
global_task_manager = AsyncTaskManager()


def start_task_manager(max_workers: int = 3):
    """启动全局任务管理器"""
    global_task_manager.max_workers = max_workers
    global_task_manager.start()


def stop_task_manager():
    """停止全局任务管理器"""
    global_task_manager.stop()
