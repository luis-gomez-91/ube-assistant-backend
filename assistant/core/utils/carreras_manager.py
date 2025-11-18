from datetime import datetime, timedelta
from threading import Lock
import logging
from typing import List

from core.services.ventas_service import fetch_carreras
from schemas.ventas.carreras import CarrerasModel

logger = logging.getLogger(__name__)

class CarrerasManager:
    """Manager thread-safe con caché"""
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._carreras = None
                    cls._instance._last_fetch = None
                    cls._instance._cache_duration = timedelta(hours=1)
        return cls._instance

    async def get_carreras(self) -> List[CarrerasModel]:
        """Obtiene carreras con caché de 1 hora"""
        now = datetime.now()

        # Cache hit
        if self._carreras and self._last_fetch:
            if now - self._last_fetch < self._cache_duration:
                return self._carreras

        with self._lock:
            try:
                self._carreras = await fetch_carreras()
                self._last_fetch = now
                logger.info("Carreras cache actualizado")
            except Exception as e:
                logger.error(f"Error fetching carreras: {e}")
                if self._carreras:
                    logger.warning("Usando cache antiguo de carreras")
                    return self._carreras
                raise

        return self._carreras