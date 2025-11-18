from datetime import datetime, timedelta
from langchain.memory import ConversationBufferMemory
from threading import Lock
import logging


logger = logging.getLogger(__name__)

class MemoriaManager:
    """Gestor centralizado de memorias thread-safe con TTL"""

    def __init__(self, ttl_hours: int = 24, max_chats: int = 1000):
        self._memorias = {}
        self._timestamps = {}
        self._lock = Lock()
        self.ttl = timedelta(hours=ttl_hours)
        self.max_chats = max_chats

    def get_memory(self, chat_id: int) -> ConversationBufferMemory:
        """Obtiene o crea memoria para un chat_id, con limpieza automática de expiradas"""
        self._cleanup_expired()

        with self._lock:
            if chat_id not in self._memorias:
                if len(self._memorias) >= self.max_chats:
                    logger.warning(f"Límite de chats alcanzado ({self.max_chats})")

                self._memorias[chat_id] = ConversationBufferMemory(
                    memory_key="chat_history",
                    return_messages=True
                )
                self._timestamps[chat_id] = datetime.now()
                logger.info(f"✅ Memoria creada para chat_id: {chat_id}")
            else:
                # Actualizar timestamp de acceso
                self._timestamps[chat_id] = datetime.now()

            return self._memorias[chat_id]

    def _cleanup_expired(self) -> None:
        """Limpia memorias expiradas"""
        now = datetime.now()
        with self._lock:
            expired = [
                chat_id for chat_id, timestamp in self._timestamps.items()
                if now - timestamp > self.ttl
            ]
            for chat_id in expired:
                self._memorias.pop(chat_id, None)
                self._timestamps.pop(chat_id, None)
                logger.info(f"🗑️ Memoria expirada eliminada: chat_id {chat_id}")

    def clear_memory(self, chat_id: int) -> None:
        """Limpia la memoria de un chat específico"""
        with self._lock:
            if chat_id in self._memorias:
                self._memorias.pop(chat_id)
                self._timestamps.pop(chat_id)
                logger.info(f"🗑️ Memoria eliminada: chat_id {chat_id}")

    def get_size(self) -> int:
        """Retorna cantidad de chats en memoria"""
        return len(self._memorias)

memoria_manager = MemoriaManager(ttl_hours=24, max_chats=500)
