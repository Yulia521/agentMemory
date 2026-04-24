from mem0 import Memory
import os
import shutil
import logging
import platform

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'memory.log')
)
logger = logging.getLogger(__name__)

class MemoryManager:
    def __init__(self):
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

        # 3. 强制定义本地存储路径
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        storage_path = os.path.join(base_dir, "mem0_storage")
        new_data_path = os.path.join(base_dir, "new_mem0_data")

        # 4. 删除所有可能的存储目录
        for path in [storage_path, new_data_path]:
            if os.path.exists(path):
                logger.info(f"删除旧存储目录: {path}")
                shutil.rmtree(path)

        # 创建新的存储目录
        os.makedirs(storage_path, exist_ok=True)
        logger.info(f"创建新存储目录: {storage_path}")

        # 5. 核心配置：全路径本地化
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
                "provider": "qdrant",
                "config": {
                    "path": os.path.join(storage_path, "qdrant"),
                    "collection_name": "agent_memories",
                    # 使用正确的字段名
                    "embedding_model_dims": 1024
                }
            },
            "version_db_path": os.path.join(storage_path, "history.db")
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
        except Exception as e:
            logger.error(f"Memory 初始化失败: {e}")
            raise

        self.working_memory = []
        logger.info("MemoryManager 初始化完成")

    def get_context(self, user_id, query):
        logger.info(f"获取上下文，用户ID: {user_id}, 查询: {query}")
        try:
            logger.debug("执行搜索操作...")
            past_memories = self.long_term_memory.search(query, filters={"user_id": user_id})
            mem_list = [m['text'] for m in past_memories] if past_memories else []
            mem_str = "\n".join(mem_list)
            logger.info(f"检索到 {len(mem_list)} 条历史记忆")

            working_list = [f"{m['role']}: {m['content']}" for m in self.working_memory[-3:]]
            working_str = "\n".join(working_list)

            return f"历史背景:\n{mem_str}\n当前对话:\n{working_str}"
        except Exception as e:
            logger.error(f"获取上下文失败: {e}", exc_info=True)
            return "历史背景:\n\n当前对话:\n"

    def save(self, user_id, user_input, assistant_output):
        logger.info(f"保存记忆，用户ID: {user_id}")
        try:
            self.working_memory.append({"role": "user", "content": user_input})
            self.working_memory.append({"role": "assistant", "content": assistant_output})

            logger.debug("执行添加操作...")
            self.long_term_memory.add(
                f"User: {user_input}\nAssistant: {assistant_output}",
                user_id=user_id
            )
            logger.info("记忆保存成功")
        except Exception as e:
            logger.error(f"保存记忆失败: {e}", exc_info=True)
            raise
