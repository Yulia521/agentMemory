import time

class PerformanceMonitor:
    """
    用于满足任务书要求的质量与效率评测基准 [cite: 28]
    """
    def __init__(self):
        self.start_time = 0

    def start_timer(self):
        self.start_time = time.perf_counter()

    def end_timer(self):
        # 计算端到端延迟 (P50/P95 统计基础) [cite: 32]
        duration = time.perf_counter() - self.start_time
        return round(duration, 3)

    @staticmethod
    def log_metrics(latency, tokens=0):
        print(f"  > [监控指标] 延迟: {latency}s | 消耗 Token: {tokens}")