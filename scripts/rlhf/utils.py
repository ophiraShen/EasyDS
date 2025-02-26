# EasyDS/scripts/rlhf/utils.py
import gc
import torch
# import GPUtil
from datetime import datetime
import csv
import os
from threading import Thread
import time
from typing import Optional

class GPUMonitor:
    """GPU监控类,用于记录GPU使用情况"""
    def __init__(self, log_dir: str = "gpu_logs", interval: int = 60):
        """
        初始化GPU监控器
        Args:
            log_dir: 日志保存目录
            interval: 监控间隔(秒)
        """
        self.log_dir = log_dir
        self.interval = interval
        self.is_running = False
        
        # 创建日志目录
        os.makedirs(log_dir, exist_ok=True)
        
        # 使用日期作为文件名
        current_date = datetime.now().strftime('%Y%m%d')
        self.log_file = os.path.join(log_dir, f"gpu_stats_{current_date}.csv")
        
        # 如果文件不存在才创建表头
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Timestamp', 
                    'GPU ID', 
                    'Memory Used (MB)',
                    'Memory Total (MB)', 
                    'GPU Load (%)', 
                    'Temperature (°C)'
                ])
    
    def _monitor(self):
        """监控线程的主要逻辑"""
        while self.is_running:
            try:
                gpus = GPUtil.getGPUs()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # 收集所有GPU的数据
                gpu_stats = []
                for gpu in gpus:
                    gpu_stats.append([
                        timestamp,
                        gpu.id,
                        gpu.memoryUsed,
                        gpu.memoryTotal,
                        gpu.load * 100,
                        gpu.temperature
                    ])
                
                # 批量写入文件
                with open(self.log_file, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerows(gpu_stats)
                
                # 打印汇总信息
                print(f"\nGPU Stats at {timestamp}:")
                for gpu in gpus:
                    print(f"GPU {gpu.id}: "
                          f"Memory: {gpu.memoryUsed:>5.0f}MB, "
                          f"Util: {gpu.load*100:>5.1f}%, "
                          f"Temp: {gpu.temperature:>3.0f}°C")
                
                time.sleep(self.interval)
                
            except Exception as e:
                print(f"Error in GPU monitoring: {e}")
                time.sleep(self.interval)  # 出错时也等待
                
    def start(self):
        """启动GPU监控"""
        self.is_running = True
        self.monitor_thread = Thread(target=self._monitor, daemon=True)
        self.monitor_thread.start()
    
    def stop(self):
        """停止GPU监控"""
        self.is_running = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=1)

def empty_cache():
    """清空GPU缓存"""
    gc.collect()
    torch.cuda.empty_cache()

def get_gpu_memory_info() -> tuple:
    """
    获取当前GPU内存使用情况
    Returns:
        tuple: (已用内存, 总内存) 单位MB
    """
    if torch.cuda.is_available():
        return (
            torch.cuda.memory_allocated() / 1024**2,
            torch.cuda.get_device_properties(0).total_memory / 1024**2
        )
    return (0, 0)

def setup_devices(use_cpu: bool = False) -> torch.device:
    """
    设置计算设备
    Args:
        use_cpu: 是否强制使用CPU
    Returns:
        torch.device: 计算设备
    """
    if use_cpu:
        return torch.device('cpu')
    return torch.device('cuda' if torch.cuda.is_available() else 'cpu')