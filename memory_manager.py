#!/usr/bin/env python3
"""
Memory Manager para Dona Slack Bot
Gestiona conversaciones, contexto y preferencias de usuario
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import os

# Importar Redis memory para FASE 2
from redis_memory import redis_memory

# Importar memoria inteligente para FASE 3
from intelligent_memory import intelligent_memory

logger = logging.getLogger(__name__)

class MemoryManager:
    """
    Gestor de memoria para el bot Dona
    Maneja conversaciones, contexto y preferencias de usuario
    """
    
    def __init__(self, db_path: str = None):
        """Inicializar el memory manager"""
        if db_path is None:
            # En producción, usar directorio temporal
            import tempfile
            temp_dir = tempfile.gettempdir()
            db_path = os.path.join(temp_dir, "dona_memory.db")
        self.db_path = db_path
        self.init_database()
        logger.info(f"💾 Memory Manager inicializado con DB: {db_path}")
    
    def init_database(self):
        """Crear tablas de la base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tabla de usuarios y preferencias
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT,
                    display_name TEXT,
                    preferences TEXT,  -- JSON string
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
                
                # Tabla de conversaciones
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    channel_id TEXT,
                    thread_ts TEXT,
                    message_ts TEXT,
                    role TEXT,  -- 'user' or 'assistant'
                    content TEXT,
                    metadata TEXT,  -- JSON string para contexto adicional
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
                """)
                
                # Tabla de contexto activo
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS active_context (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    channel_id TEXT,
                    context_summary TEXT,
                    current_topics TEXT,  -- JSON array
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
                """)
                
                # Índices para performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_user_channel ON conversations(user_id, channel_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(created_at)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_active_context_user ON active_context(user_id)")
                
                conn.commit()
                logger.info("✅ Base de datos inicializada correctamente")
                
        except Exception as e:
            logger.error(f"❌ Error inicializando base de datos: {e}")
            raise

    def add_user(self, user_id: str, username: str = None, display_name: str = None, preferences: Dict = None):
        """Agregar o actualizar usuario"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                preferences_json = json.dumps(preferences or {})
                
                cursor.execute("""
                INSERT OR REPLACE INTO users (user_id, username, display_name, preferences, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (user_id, username, display_name, preferences_json))
                
                conn.commit()
                logger.debug(f"👤 Usuario agregado/actualizado: {user_id}")
                
        except Exception as e:
            logger.error(f"❌ Error agregando usuario {user_id}: {e}")

    def log_conversation(self, user_id: str, channel_id: str, role: str, content: str, 
                        thread_ts: str = None, message_ts: str = None, metadata: Dict = None):
        """Guardar mensaje en historial de conversaciones"""
        try:
            # FASE 2: Actualizar sesión activa en Redis
            if redis_memory.is_available():
                if role == "user":
                    # Iniciar/actualizar sesión para mensajes de usuario
                    redis_memory.start_active_session(user_id, channel_id, metadata)
                    redis_memory.increment_message_counter("user")
                else:
                    redis_memory.update_session_activity(user_id, channel_id)
                    redis_memory.increment_message_counter("bot")
            
            # Guardar en SQLite (persistente)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                metadata_json = json.dumps(metadata or {})
                
                cursor.execute("""
                INSERT INTO conversations (user_id, channel_id, thread_ts, message_ts, role, content, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (user_id, channel_id, thread_ts, message_ts, role, content, metadata_json))
                
                conn.commit()
                logger.info(f"💬 Conversación guardada: {user_id} en {channel_id} - {role}: {content[:50]}...")
                
        except Exception as e:
            logger.error(f"❌ Error guardando conversación: {e}")
            logger.exception("Stack trace:")

    def get_conversation_history(self, user_id: str, channel_id: str = None, 
                               limit: int = 20, hours_back: int = 24) -> List[Dict]:
        """Obtener historial de conversaciones recientes"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Calcular timestamp de corte
                cutoff_time = datetime.now() - timedelta(hours=hours_back)
                
                if channel_id:
                    # Conversación específica de un canal
                    query = """
                    SELECT role, content, created_at, metadata
                    FROM conversations 
                    WHERE user_id = ? AND channel_id = ? AND created_at > ?
                    ORDER BY created_at ASC
                    LIMIT ?
                    """
                    cursor.execute(query, (user_id, channel_id, cutoff_time, limit))
                else:
                    # Todas las conversaciones del usuario
                    query = """
                    SELECT role, content, created_at, metadata, channel_id
                    FROM conversations 
                    WHERE user_id = ? AND created_at > ?
                    ORDER BY created_at ASC
                    LIMIT ?
                    """
                    cursor.execute(query, (user_id, cutoff_time, limit))
                
                rows = cursor.fetchall()
                
                # Formatear resultados
                history = []
                for row in rows:
                    history.append({
                        "role": row[0],
                        "content": row[1],
                        "timestamp": row[2],
                        "metadata": json.loads(row[3]) if row[3] else {},
                        "channel_id": row[4] if len(row) > 4 else channel_id
                    })
                
                logger.info(f"📚 Obtenido historial: {len(history)} mensajes para {user_id}")
                # Log primeros mensajes para debug
                if history:
                    logger.info(f"🔍 Primer mensaje: {history[0]['content'][:50]}...")
                return history
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo historial: {e}")
            return []

    def get_context_for_llm(self, user_id: str, channel_id: str, max_messages: int = 10) -> List[Dict]:
        """Obtener contexto formateado para el LLM con cache Redis"""
        try:
            # FASE 2: Intentar obtener de cache Redis primero
            if redis_memory.is_available():
                cached_context = redis_memory.get_cached_context(user_id, channel_id)
                if cached_context and len(cached_context) >= 3:
                    logger.debug(f"🚀 Contexto desde Redis cache: {len(cached_context)} mensajes")
                    return cached_context
            
            # Fallback a SQLite
            history = self.get_conversation_history(user_id, channel_id, limit=max_messages, hours_back=2)
            
            # Formatear para el LLM (formato OpenAI/Anthropic)
            llm_context = []
            for msg in history:
                llm_context.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # FASE 2: Cachear en Redis para próxima vez
            if redis_memory.is_available() and llm_context:
                redis_memory.cache_recent_context(user_id, channel_id, llm_context)
            
            logger.debug(f"🧠 Contexto para LLM: {len(llm_context)} mensajes")
            return llm_context
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo contexto para LLM: {e}")
            return []
    
    def get_intelligent_context(self, user_id: str, channel_id: str, current_message: str, max_messages: int = 10) -> Dict:
        """FASE 3: Obtener contexto inteligente con análisis semántico"""
        try:
            # Obtener historial completo
            history = self.get_conversation_history(user_id, channel_id, limit=max_messages, hours_back=4)
            
            # Obtener preferencias del usuario
            user_preferences = self.get_user_preferences(user_id)
            
            # Generar contexto inteligente
            smart_context = intelligent_memory.generate_smart_context(
                current_message, 
                history, 
                user_preferences
            )
            
            # Formatear contexto optimizado para LLM
            optimized_context = self._format_intelligent_context_for_llm(smart_context)
            
            logger.info(f"🤖 Contexto inteligente generado para {user_id}")
            return {
                "context": optimized_context,
                "analysis": smart_context.get("message_analysis", {}),
                "hints": smart_context.get("response_hints", []),
                "tone": smart_context.get("recommended_tone", "casual")
            }
            
        except Exception as e:
            logger.error(f"❌ Error generando contexto inteligente: {e}")
            # Fallback al contexto básico
            basic_context = self.get_context_for_llm(user_id, channel_id, max_messages)
            return {
                "context": basic_context,
                "analysis": {},
                "hints": ["Responder de manera natural y útil"],
                "tone": "casual"
            }
    
    def _format_intelligent_context_for_llm(self, smart_context: Dict) -> List[Dict]:
        """Formatea el contexto inteligente para el LLM"""
        try:
            # Mensajes relevantes
            relevant_history = smart_context.get("relevant_history", [])
            
            # Convertir a formato LLM
            llm_context = []
            for msg in relevant_history:
                llm_context.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
            
            # Agregar resumen de contexto como mensaje del sistema si es relevante
            context_summary = smart_context.get("context_summary", "")
            if context_summary and len(llm_context) > 2:
                llm_context.insert(0, {
                    "role": "system",
                    "content": f"Contexto de la conversación: {context_summary}"
                })
            
            return llm_context
            
        except Exception as e:
            logger.error(f"❌ Error formateando contexto inteligente: {e}")
            return smart_context.get("relevant_history", [])

    def update_active_context(self, user_id: str, channel_id: str, 
                            context_summary: str = None, topics: List[str] = None):
        """Actualizar contexto activo de la sesión"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                session_id = f"{user_id}_{channel_id}"
                topics_json = json.dumps(topics or [])
                expires_at = datetime.now() + timedelta(hours=2)  # Contexto expira en 2 horas
                
                cursor.execute("""
                INSERT OR REPLACE INTO active_context 
                (session_id, user_id, channel_id, context_summary, current_topics, last_activity, expires_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
                """, (session_id, user_id, channel_id, context_summary, topics_json, expires_at))
                
                conn.commit()
                logger.debug(f"🎯 Contexto activo actualizado: {session_id}")
                
        except Exception as e:
            logger.error(f"❌ Error actualizando contexto activo: {e}")

    def get_user_preferences(self, user_id: str) -> Dict:
        """Obtener preferencias del usuario"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT preferences FROM users WHERE user_id = ?", (user_id,))
                row = cursor.fetchone()
                
                if row and row[0]:
                    return json.loads(row[0])
                else:
                    # Preferencias por defecto
                    return {
                        "communication_style": "casual",
                        "language": "es",
                        "timezone": "UTC-5",
                        "notifications": True
                    }
                    
        except Exception as e:
            logger.error(f"❌ Error obteniendo preferencias de {user_id}: {e}")
            return {}

    def update_user_preferences(self, user_id: str, preferences: Dict):
        """Actualizar preferencias del usuario"""
        try:
            current_prefs = self.get_user_preferences(user_id)
            current_prefs.update(preferences)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                preferences_json = json.dumps(current_prefs)
                cursor.execute("""
                UPDATE users SET preferences = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE user_id = ?
                """, (preferences_json, user_id))
                
                conn.commit()
                logger.debug(f"⚙️ Preferencias actualizadas para {user_id}")
                
        except Exception as e:
            logger.error(f"❌ Error actualizando preferencias de {user_id}: {e}")

    def cleanup_old_data(self, days_to_keep: int = 30):
        """Limpiar datos antiguos para mantener la DB optimizada"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cutoff_date = datetime.now() - timedelta(days=days_to_keep)
                
                # Limpiar conversaciones antiguas
                cursor.execute("DELETE FROM conversations WHERE created_at < ?", (cutoff_date,))
                conversations_deleted = cursor.rowcount
                
                # Limpiar contexto expirado
                cursor.execute("DELETE FROM active_context WHERE expires_at < CURRENT_TIMESTAMP")
                context_deleted = cursor.rowcount
                
                conn.commit()
                logger.info(f"🧹 Limpieza completada: {conversations_deleted} conversaciones, {context_deleted} contextos")
                
        except Exception as e:
            logger.error(f"❌ Error en limpieza de datos: {e}")

    def get_memory_stats(self) -> Dict:
        """Obtener estadísticas de memoria para debugging (SQLite + Redis)"""
        try:
            # Stats de SQLite
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Contar usuarios
                cursor.execute("SELECT COUNT(*) FROM users")
                total_users = cursor.fetchone()[0]
                
                # Contar conversaciones
                cursor.execute("SELECT COUNT(*) FROM conversations")
                total_conversations = cursor.fetchone()[0]
                
                # Contar contextos activos
                cursor.execute("SELECT COUNT(*) FROM active_context WHERE expires_at > CURRENT_TIMESTAMP")
                active_contexts = cursor.fetchone()[0]
                
                # Tamaño de DB
                db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
                
                stats = {
                    "total_users": total_users,
                    "total_conversations": total_conversations,
                    "active_contexts": active_contexts,
                    "db_size_mb": round(db_size / (1024 * 1024), 2)
                }
                
                # FASE 2: Agregar stats de Redis
                if redis_memory.is_available():
                    redis_stats = redis_memory.get_realtime_stats()
                    stats.update({
                        "redis_available": True,
                        "active_sessions": redis_stats.get("active_sessions", 0),
                        "messages_today": redis_stats.get("messages_today", 0),
                        "active_users_redis": redis_stats.get("active_users", 0)
                    })
                else:
                    stats["redis_available"] = False
                
                return stats
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {e}")
            return {}

# Instancia global del memory manager
memory_manager = MemoryManager()