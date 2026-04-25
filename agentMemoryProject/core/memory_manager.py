from mem0 import Memory
import os
import logging
import platform
import asyncio
import threading
from collections import deque
import time
import sqlite3
import json

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'memory.log')
)
logger = logging.getLogger(__name__)

class MemoryManager:
    def __init__(self, storage_path=None):
        logger.info("初始化 MemoryManager")

        # 1. 打印系统信息
        logger.debug(f"系统平台: {platform.platform()}")
        logger.debug(f"Python 版本: {platform.python_version()}")

        # 2. 获取配置
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL")
        model_name = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-7B-Instruct")
        logger.info(f"使用模型: {model_name}")
        logger.debug(f"API 基础 URL: {base_url}")

        # 3. 定义存储路径
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if storage_path:
            self.storage_path = storage_path
        else:
            self.storage_path = os.path.join(base_dir, "mem0_storage")

        # 4. 创建存储目录
        if not os.path.exists(self.storage_path):
            logger.info(f"创建存储目录: {self.storage_path}")
            os.makedirs(self.storage_path, exist_ok=True)
        else:
            logger.info(f"使用现有存储目录: {self.storage_path}")

        # 5. 核心配置：使用FAISS存储
        config = {
            "llm": {
                "provider": "openai",
                "config": {
                    "model": model_name,
                    "api_key": api_key,
                    "openai_base_url": base_url
                }
            },
            "embedder": {
                "provider": "openai",
                "config": {
                    "model": "BAAI/bge-m3", # 维度为 1024
                    "api_key": api_key,
                    "openai_base_url": base_url
                }
            },
            "vector_store": {
                "provider": "faiss",  # 使用FAISS存储
                "config": {
                    "path": os.path.join(self.storage_path, "faiss_index"),
                    "collection_name": "agent_memories",
                    "embedding_model_dims": 1024
                }
            },
            "version_db_path": os.path.join(self.storage_path, "history.db")
        }
        logger.info("配置创建完成，使用 BAAI/bge-m3 嵌入模型 (1024维度)")
        logger.debug(f"完整配置: {config}")

        # 6. 禁用默认配置，确保完全使用本地配置
        logger.debug("当前环境变量:")
        for key, value in os.environ.items():
            if key.startswith("MEM0_"):
                logger.debug(f"  {key}: {value}")

        # 清除所有相关环境变量
        mem0_env_vars = ["MEM0_CONFIG_PATH", "MEM0_STORAGE_PATH", "MEM0_EMBEDDER_MODEL",
                         "MEM0_EMBEDDER_PROVIDER", "MEM0_VECTOR_STORE_PROVIDER"]
        for var in mem0_env_vars:
            if var in os.environ:
                logger.info(f"清除环境变量: {var}")
                os.environ.pop(var)

        # 7. 初始化 Memory
        logger.info("正在初始化 Memory 实例...")
        try:
            self.long_term_memory = Memory.from_config(config)
            logger.info("Memory 实例初始化成功")

            # 检查 Memory 实例的属性
            logger.debug(f"Memory 实例类型: {type(self.long_term_memory)}")
            if hasattr(self.long_term_memory, 'vector_store'):
                logger.debug(f"向量存储类型: {type(self.long_term_memory.vector_store)}")
            if hasattr(self.long_term_memory, 'embedder'):
                logger.debug(f"嵌入器类型: {type(self.long_term_memory.embedder)}")
                if hasattr(self.long_term_memory.embedder, '_config'):
                    logger.debug(f"嵌入器配置: {self.long_term_memory.embedder._config}")

            # 检查是否有现有记忆
            logger.debug("检查是否有现有记忆...")
            try:
                existing_memories = self.long_term_memory.search("测试", filters={"user_id": "test"})
                logger.info(f"现有记忆数量: {len(existing_memories['results']) if isinstance(existing_memories, dict) and 'results' in existing_memories else len(existing_memories)}")
            except Exception as e:
                logger.debug(f"检查现有记忆时出错: {e}")

        except Exception as e:
            logger.error(f"Memory 初始化失败: {e}")
            raise

        # 初始化工作记忆（带上下文窗口管理）
        self.working_memory = []
        self.working_memory_window = 10  # 工作记忆窗口大小
        self.important_memory_flags = set()  # 重要记忆标记

        # 初始化长期记忆增强功能
        self.memory_categories = {}
        self.memory_tags = {}
        self.long_term_memory_limit = 1000  # 长期记忆上限
        self.memory_retention_days = 30  # 记忆保留天数

        # 初始化语义记忆
        self.semantic_memory_db = os.path.join(self.storage_path, "semantic_memory.db")
        self._init_semantic_memory()
        self.semantic_memory_limit = 500  # 语义记忆上限

        # 初始化记忆批处理队列
        self.memory_queue = deque()
        self.queue_lock = threading.Lock()
        self.processing_thread = None
        self.running = False
        # 启动批处理线程
        self.start_batch_processor()
        # 启动定期清理任务
        self.start_cleanup_task()
        logger.info("MemoryManager 初始化完成")

    def _init_semantic_memory(self):
        """初始化语义记忆数据库"""
        try:
            conn = sqlite3.connect(self.semantic_memory_db)
            cursor = conn.cursor()
            # 创建语义记忆表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS semantic_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                concept TEXT NOT NULL,
                definition TEXT NOT NULL,
                relationships TEXT,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_concept ON semantic_memory(concept)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON semantic_memory(category)')
            conn.commit()
            conn.close()
            logger.info("语义记忆数据库初始化成功")
        except Exception as e:
            logger.error(f"初始化语义记忆数据库失败: {e}")

    def start_batch_processor(self):
        """启动批处理线程"""
        self.running = True
        self.processing_thread = threading.Thread(target=self._process_memory_queue)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        logger.info("记忆批处理线程已启动")

    def _process_memory_queue(self):
        """处理记忆队列"""
        while self.running:
            try:
                if self.memory_queue:
                    with self.queue_lock:
                        memory_item = self.memory_queue.popleft()
                    user_id, memory, metadata = memory_item
                    self._store_memory(user_id, memory, metadata)
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"处理记忆队列时出错: {e}")
                time.sleep(1)

    def start_cleanup_task(self):
        """启动定期清理任务"""
        cleanup_thread = threading.Thread(target=self._cleanup_task)
        cleanup_thread.daemon = True
        cleanup_thread.start()
        logger.info("定期清理任务已启动")

    def _cleanup_task(self):
        """定期清理过期记忆"""
        while True:
            try:
                time.sleep(3600)  # 每小时执行一次
                self.cleanup_old_memories()
            except Exception as e:
                logger.error(f"执行清理任务时出错: {e}")
                time.sleep(60)

    def cleanup_old_memories(self):
        """清理过期记忆"""
        try:
            # 清理语义记忆
            conn = sqlite3.connect(self.semantic_memory_db)
            cursor = conn.cursor()
            # 删除超过保留天数的语义记忆
            cursor.execute('''
            DELETE FROM semantic_memory
            WHERE created_at < datetime('now', '-' || ? || ' days')
            ''', (self.memory_retention_days,))
            conn.commit()
            conn.close()

            # 清理工作记忆（保持窗口大小）
            if len(self.working_memory) > self.working_memory_window:
                self.working_memory = self.working_memory[-self.working_memory_window:]

            logger.info("记忆清理完成")
        except Exception as e:
            logger.error(f"清理记忆时出错: {e}")

    def _store_memory(self, user_id, memory, metadata):
        """存储记忆到长期记忆"""
        try:
            # 存储到长期记忆
            self.long_term_memory.add(
                memory,
                user_id=user_id,
                metadata=metadata
            )
            logger.debug(f"记忆存储成功: {memory[:50]}...")
        except Exception as e:
            logger.error(f"存储记忆失败: {e}")

    def add_memory(self, user_id, memory, metadata=None):
        """添加记忆（异步）"""
        if metadata is None:
            metadata = {}

        # 添加到工作记忆
        self.working_memory.append({
            "content": memory,
            "user_id": user_id,
            "metadata": metadata,
            "timestamp": time.time()
        })

        # 保持工作记忆窗口大小
        if len(self.working_memory) > self.working_memory_window:
            self.working_memory = self.working_memory[-self.working_memory_window:]

        # 添加到批处理队列
        with self.queue_lock:
            self.memory_queue.append((user_id, memory, metadata))

        logger.debug(f"记忆添加到队列: {memory[:50]}...")

    def get_working_memory(self, user_id):
        """获取工作记忆"""
        return [item for item in self.working_memory if item["user_id"] == user_id]

    def get_long_term_memory(self, user_id, query=None, limit=10):
        """获取长期记忆"""
        try:
            if query:
                # 搜索相关记忆
                results = self.long_term_memory.search(
                    query,
                    user_id=user_id,
                    limit=limit
                )
                # 处理结果格式
                if isinstance(results, dict) and 'results' in results:
                    return results['results']
                return results
            else:
                # 获取最近的记忆
                results = self.long_term_memory.get_all(
                    user_id=user_id,
                    limit=limit
                )
                # 处理结果格式
                if isinstance(results, dict) and 'results' in results:
                    return results['results']
                return results
        except Exception as e:
            logger.error(f"获取长期记忆失败: {e}")
            return []

    def get_semantic_memory(self, concept=None, category=None, limit=10):
        """获取语义记忆"""
        try:
            conn = sqlite3.connect(self.semantic_memory_db)
            cursor = conn.cursor()

            query = "SELECT * FROM semantic_memory WHERE 1=1"
            params = []

            if concept:
                query += " AND concept LIKE ?"
                params.append(f"%{concept}%")

            if category:
                query += " AND category = ?"
                params.append(category)

            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            results = cursor.fetchall()

            semantic_memories = []
            for row in results:
                semantic_memories.append({
                    "id": row[0],
                    "concept": row[1],
                    "definition": row[2],
                    "relationships": json.loads(row[3]) if row[3] else {},
                    "category": row[4],
                    "created_at": row[5]
                })

            conn.close()
            return semantic_memories
        except Exception as e:
            logger.error(f"获取语义记忆失败: {e}")
            return []

    def add_semantic_memory(self, concept, definition, relationships=None, category=None):
        """添加语义记忆"""
        try:
            conn = sqlite3.connect(self.semantic_memory_db)
            cursor = conn.cursor()

            cursor.execute('''
            INSERT INTO semantic_memory (concept, definition, relationships, category)
            VALUES (?, ?, ?, ?)
            ''', (concept, definition, json.dumps(relationships) if relationships else None, category))

            conn.commit()
            conn.close()
            logger.info(f"语义记忆添加成功: {concept}")
        except Exception as e:
            logger.error(f"添加语义记忆失败: {e}")

    def get_memory_count(self, user_id):
        """获取记忆数量"""
        try:
            # 获取长期记忆数量
            results = self.long_term_memory.get_all(user_id=user_id, limit=1000)
            if isinstance(results, dict) and 'results' in results:
                long_term_count = len(results['results'])
            else:
                long_term_count = len(results)

            # 获取工作记忆数量
            working_count = len([item for item in self.working_memory if item["user_id"] == user_id])

            # 获取语义记忆数量
            conn = sqlite3.connect(self.semantic_memory_db)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM semantic_memory")
            semantic_count = cursor.fetchone()[0]
            conn.close()

            return {
                "working": working_count,
                "long_term": long_term_count,
                "semantic": semantic_count
            }
        except Exception as e:
            logger.error(f"获取记忆数量失败: {e}")
            return {
                "working": 0,
                "long_term": 0,
                "semantic": 0
            }

    def shutdown(self):
        """关闭内存管理器"""
        self.running = False
        if self.processing_thread:
            self.processing_thread.join(timeout=5)
        logger.info("MemoryManager 已关闭")

def get_context(self, user_id, limit=5):
    """获取上下文信息（用于生成响应）"""
    try:
        # 获取工作记忆中的最近对话
        working_memory = self.get_working_memory(user_id)
        recent_working = working_memory[-limit:] if len(working_memory) > limit else working_memory

        # 构建上下文字符串
        context = []
        for item in recent_working:
            context.append(f"用户: {item['content']}")

        return "\n".join(context)
    except Exception as e:
        logger.error(f"获取上下文失败: {e}")
        return ""
