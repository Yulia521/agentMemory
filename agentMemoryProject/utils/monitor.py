import time
import logging

class PerformanceMonitor:
    """
    用于满足任务书要求的质量与效率评测基准 [cite: 28]
    """
    def __init__(self):
        self.start_time = 0
        self.stage_times = {}

    def start_timer(self):
        self.start_time = time.perf_counter()
        self.stage_times = {}

    def start_stage(self, stage_name):
        """开始记录某个阶段的时间"""
        self.stage_times[stage_name] = time.perf_counter()

    def end_stage(self, stage_name):
        """结束记录某个阶段的时间并返回该阶段的耗时"""
        if stage_name in self.stage_times:
            duration = time.perf_counter() - self.stage_times[stage_name]
            self.stage_times[stage_name] = round(duration, 3)
            return self.stage_times[stage_name]
        return 0

    def end_timer(self):
        # 计算端到端延迟 (P50/P95 统计基础) [cite: 32]
        duration = time.perf_counter() - self.start_time
        return round(duration, 3)

    def log_metrics(self, latency, tokens=0):
        print(f"  > [监控指标] 延迟: {latency}s | 消耗 Token: {tokens}")

        # 打印各个阶段的延迟
        if self.stage_times:
            print("  > [阶段延迟]")
            for stage, time_taken in self.stage_times.items():
                print(f"    - {stage}: {time_taken}s")