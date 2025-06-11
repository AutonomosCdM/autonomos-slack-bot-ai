"""
Redis Memory Manager para sesiones activas
Complementa SQLite con memoria temporal y rápida
"""

import os
import json
import logging
import redis
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RedisMemoryManager:
    """Maneja memoria temporal con Redis para sesiones activas"""
    
    def __init__(self):
        self.redis_client = None
        self._connect_redis()
        
    def _connect_redis(self):
        """Conecta a Redis con fallback para desarrollo local"""
        try:
            # Producción (Render/Railway con Redis addon)
            redis_url = os.getenv("REDIS_URL")
            if redis_url:
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                logger.info("✅ Conectado a Redis (producción)")
                return
            
            # Desarrollo local
            redis_host = os.getenv("REDIS_HOST", "localhost")
            redis_port = int(os.getenv("REDIS_PORT", 6379))
            redis_password = os.getenv("REDIS_PASSWORD")
            
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                password=redis_password,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test conexión
            self.redis_client.ping()
            logger.info("✅ Conectado a Redis (desarrollo)")
            
        except Exception as e:
            logger.warning(f"⚠️ Redis no disponible: {e}")
            self.redis_client = None
    
    def is_available(self) -> bool:
        """Verifica si Redis está disponible"""
        if not self.redis_client:
            return False
        try:
            self.redis_client.ping()
            return True
        except:
            return False
    
    # ============================================================================
    # SESIONES ACTIVAS
    # ============================================================================
    
    def start_active_session(self, user_id: str, channel_id: str, metadata: Dict = None):
        """Inicia una sesión activa para un usuario"""
        if not self.is_available():
            return
        
        try:
            session_key = f"session:{user_id}:{channel_id}"
            session_data = {
                "user_id": user_id,
                "channel_id": channel_id,
                "started_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "message_count": 0,
                "metadata": metadata or {}
            }
            
            # Sesión expira en 30 minutos de inactividad
            self.redis_client.setex(
                session_key, 
                1800,  # 30 minutos
                json.dumps(session_data)
            )
            
            # Agregar a índice de sesiones activas
            self.redis_client.sadd("active_sessions", session_key)
            
            logger.info(f"🚀 Sesión iniciada: {user_id} en {channel_id}")
            
        except Exception as e:
            logger.error(f"❌ Error iniciando sesión: {e}")
    
    def update_session_activity(self, user_id: str, channel_id: str):
        """Actualiza la actividad de una sesión"""
        if not self.is_available():
            return
        
        try:
            session_key = f"session:{user_id}:{channel_id}"
            session_data = self.redis_client.get(session_key)
            
            if session_data:
                data = json.loads(session_data)
                data["last_activity"] = datetime.now().isoformat()
                data["message_count"] = data.get("message_count", 0) + 1
                
                # Renovar TTL
                self.redis_client.setex(session_key, 1800, json.dumps(data))
                
        except Exception as e:
            logger.error(f"❌ Error actualizando sesión: {e}")
    
    def get_active_session(self, user_id: str, channel_id: str) -> Optional[Dict]:
        """Obtiene datos de sesión activa"""
        if not self.is_available():
            return None
        
        try:
            session_key = f"session:{user_id}:{channel_id}"
            session_data = self.redis_client.get(session_key)
            
            if session_data:
                return json.loads(session_data)
            return None
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo sesión: {e}")
            return None
    
    def end_session(self, user_id: str, channel_id: str):
        """Termina una sesión activa"""
        if not self.is_available():
            return
        
        try:
            session_key = f"session:{user_id}:{channel_id}"
            self.redis_client.delete(session_key)
            self.redis_client.srem("active_sessions", session_key)
            
            logger.info(f"🛑 Sesión terminada: {user_id} en {channel_id}")
            
        except Exception as e:
            logger.error(f"❌ Error terminando sesión: {e}")
    
    # ============================================================================
    # CONTEXTO RÁPIDO TEMPORAL
    # ============================================================================
    
    def cache_recent_context(self, user_id: str, channel_id: str, context: List[Dict]):
        """Cachea contexto reciente para acceso rápido"""
        if not self.is_available():
            return
        
        try:
            context_key = f"context:{user_id}:{channel_id}"
            
            # Solo últimos 5 mensajes para cache rápido
            recent_context = context[-5:] if len(context) > 5 else context
            
            # Cache por 10 minutos
            self.redis_client.setex(
                context_key,
                600,  # 10 minutos
                json.dumps(recent_context)
            )
            
        except Exception as e:
            logger.error(f"❌ Error cacheando contexto: {e}")
    
    def get_cached_context(self, user_id: str, channel_id: str) -> Optional[List[Dict]]:
        """Obtiene contexto cacheado"""
        if not self.is_available():
            return None
        
        try:
            context_key = f"context:{user_id}:{channel_id}"
            cached_data = self.redis_client.get(context_key)
            
            if cached_data:
                return json.loads(cached_data)
            return None
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo contexto cache: {e}")
            return None
    
    # ============================================================================
    # ESTADÍSTICAS EN TIEMPO REAL
    # ============================================================================
    
    def increment_message_counter(self, category: str = "total"):
        """Incrementa contadores de mensajes"""
        if not self.is_available():
            return
        
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            counter_key = f"stats:{category}:{today}"
            
            # Incrementar y set TTL de 7 días
            self.redis_client.incr(counter_key)
            self.redis_client.expire(counter_key, 604800)  # 7 días
            
        except Exception as e:
            logger.error(f"❌ Error incrementando contador: {e}")
    
    def get_realtime_stats(self) -> Dict:
        """Obtiene estadísticas en tiempo real"""
        if not self.is_available():
            return {"redis_available": False}
        
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Sesiones activas
            active_sessions = self.redis_client.scard("active_sessions")
            
            # Mensajes hoy
            messages_today = self.redis_client.get(f"stats:total:{today}") or 0
            
            # Usuarios únicos activos (aproximado)
            active_users = len([key for key in self.redis_client.scan_iter("session:*")])
            
            return {
                "redis_available": True,
                "active_sessions": active_sessions,
                "messages_today": int(messages_today),
                "active_users": active_users,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo stats: {e}")
            return {"redis_available": False, "error": str(e)}
    
    # ============================================================================
    # LIMPIEZA Y MANTENIMIENTO
    # ============================================================================
    
    def cleanup_expired_sessions(self):
        """Limpia sesiones expiradas del índice"""
        if not self.is_available():
            return
        
        try:
            active_sessions = self.redis_client.smembers("active_sessions")
            expired_count = 0
            
            for session_key in active_sessions:
                if not self.redis_client.exists(session_key):
                    self.redis_client.srem("active_sessions", session_key)
                    expired_count += 1
            
            if expired_count > 0:
                logger.info(f"🧹 Limpiadas {expired_count} sesiones expiradas")
                
        except Exception as e:
            logger.error(f"❌ Error limpiando sesiones: {e}")

# Instancia global
redis_memory = RedisMemoryManager()