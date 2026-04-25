from core.memory_manager import MemoryManager

class StorageManager:
    _instance = None

    @classmethod
    def get_instance(cls, storage_path=None):
        # 只有在第一次调用或指定了不同的存储路径时创建新实例
        if cls._instance is None or storage_path:
            cls._instance = MemoryManager(storage_path=storage_path)
        return cls._instance

# 不在这里初始化实例，避免导入时创建默认实例
# memory_manager = StorageManager.get_instance()
