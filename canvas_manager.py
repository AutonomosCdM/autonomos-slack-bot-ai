#!/usr/bin/env python3
"""
Canvas Manager - Sistema inteligente de Canvas para Slack
Maneja creación automática de resúmenes, documentación y knowledge base
"""

import json
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class CanvasTemplate:
    """Template para diferentes tipos de Canvas"""
    title: str
    content_template: str
    emoji: str
    description: str

class CanvasManager:
    """Gestor inteligente de Canvas con templates y auto-generación"""
    
    def __init__(self):
        self.templates = self._initialize_templates()
        
    def _initialize_templates(self) -> Dict[str, CanvasTemplate]:
        """Inicializar templates predefinidos"""
        return {
            "summary": CanvasTemplate(
                title="📊 Resumen de Conversación",
                emoji="📊",
                description="Resumen automático de puntos clave y decisiones",
                content_template="""# 📊 Resumen de Conversación
*Generado automáticamente por Dona AI*

## 🎯 Puntos Clave
{key_points}

## 📝 Decisiones Tomadas
{decisions}

## ✅ Tareas Identificadas
{tasks}

## 🔗 Recursos Mencionados
{resources}

---
*Última actualización: {timestamp}*
*Canal: {channel_name}*
"""
            ),
            
            "knowledge": CanvasTemplate(
                title="🧠 Base de Conocimiento",
                emoji="🧠", 
                description="Documentación colaborativa por tema",
                content_template="""# 🧠 {topic} - Base de Conocimiento
*Documentación colaborativa mantenida por el equipo*

## 📖 Descripción
{description}

## 🔧 Cómo Usar
{usage_guide}

## 📚 Recursos
{resources}

## 💡 Tips y Mejores Prácticas
{best_practices}

## 🏷️ Tags
{tags}

---
*Creado: {created_at}*
*Última actualización: {last_updated}*
*Contribuidores: {contributors}*
"""
            ),
            
            "project": CanvasTemplate(
                title="🚀 Documentación de Proyecto",
                emoji="🚀",
                description="Template para documentar proyectos y features",
                content_template="""# 🚀 {project_name}
*Documentación del proyecto*

## 🎯 Objetivo
{objective}

## 📋 Requisitos
{requirements}

## 🏗️ Arquitectura
{architecture}

## 📊 Estado Actual
{current_status}

## 🔄 Próximos Pasos
{next_steps}

## 👥 Equipo
{team}

---
*Inicio: {start_date}*
*Estimación: {estimated_completion}*
"""
            ),
            
            "meeting": CanvasTemplate(
                title="📅 Notas de Reunión",
                emoji="📅",
                description="Template para documentar reuniones",
                content_template="""# 📅 {meeting_title}
*{date} | {duration}*

## 👥 Participantes
{participants}

## 📋 Agenda
{agenda}

## 💬 Puntos Discutidos
{discussion_points}

## ✅ Decisiones
{decisions}

## 📝 Acciones
{action_items}

## 🔄 Próxima Reunión
{next_meeting}

---
*Facilitador: {facilitator}*
"""
            )
        }
    
    def create_conversation_summary(self, client, channel_id: str, conversation_history: List[Dict], 
                                  analysis: Dict, channel_name: str = "Canal") -> Dict:
        """Crear Canvas con resumen automático de conversación"""
        try:
            # Generar contenido del resumen
            key_points = self._extract_key_points(conversation_history, analysis)
            decisions = self._extract_decisions(conversation_history, analysis)
            tasks = self._extract_tasks(conversation_history, analysis)
            resources = self._extract_resources(conversation_history)
            
            # Formatear contenido usando template
            template = self.templates["summary"]
            content = template.content_template.format(
                key_points=key_points,
                decisions=decisions,
                tasks=tasks,
                resources=resources,
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"),
                channel_name=channel_name
            )
            
            # Crear Canvas usando API REST directa
            logger.info(f"🎨 Intentando crear Canvas...")
            
            canvas_response = self._create_canvas_via_api(
                client=client,
                content=content,
                title=f"{template.emoji} Resumen - {channel_name}"
            )
            
            if canvas_response.get("success"):
                return {
                    "success": True,
                    "canvas_id": canvas_response["canvas_id"],
                    "canvas_url": canvas_response["canvas_url"],
                    "title": f"{template.emoji} Resumen - {channel_name}",
                    "type": "summary"
                }
            else:
                return {"success": False, "error": canvas_response.get("error", "Unknown error")}
            
        except Exception as e:
            logger.error(f"❌ Error creando Canvas de resumen: {e}")
            return {"success": False, "error": str(e)}
    
    def create_knowledge_base(self, client, topic: str, description: str, 
                            resources: List[str] = None, tags: List[str] = None) -> Dict:
        """Crear Canvas de knowledge base por tema"""
        try:
            template = self.templates["knowledge"]
            
            # Formatear recursos
            resources_text = ""
            if resources:
                resources_text = "\n".join(f"- {resource}" for resource in resources)
            else:
                resources_text = "- *(Agregar recursos relevantes)*"
            
            # Formatear tags
            tags_text = ""
            if tags:
                tags_text = " | ".join(f"`{tag}`" for tag in tags)
            else:
                tags_text = "*(Agregar tags relevantes)*"
            
            content = template.content_template.format(
                topic=topic,
                description=description,
                usage_guide="*(Completar guía de uso)*",
                resources=resources_text,
                best_practices="*(Agregar mejores prácticas)*",
                tags=tags_text,
                created_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
                last_updated=datetime.now().strftime("%Y-%m-%d %H:%M"),
                contributors="*(Automático - Lista de contribuidores)*"
            )
            
            logger.info(f"🧠 Intentando crear Knowledge Base...")
            
            canvas_response = self._create_canvas_via_api(
                client=client,
                content=content,
                title=f"{template.emoji} {topic} - Knowledge Base"
            )
            
            if canvas_response.get("success"):
                return {
                    "success": True,
                    "canvas_id": canvas_response["canvas_id"],
                    "canvas_url": canvas_response["canvas_url"],
                    "title": f"{template.emoji} {topic} - Knowledge Base",
                    "type": "knowledge"
                }
            else:
                return {"success": False, "error": canvas_response.get("error", "Unknown error")}
            
        except Exception as e:
            logger.error(f"❌ Error creando knowledge base: {e}")
            return {"success": False, "error": str(e)}
    
    def create_project_documentation(self, client, project_name: str, objective: str,
                                   requirements: List[str] = None) -> Dict:
        """Crear Canvas de documentación de proyecto"""
        try:
            template = self.templates["project"]
            
            # Formatear requisitos
            requirements_text = ""
            if requirements:
                requirements_text = "\n".join(f"- {req}" for req in requirements)
            else:
                requirements_text = "- *(Definir requisitos)*"
            
            content = template.content_template.format(
                project_name=project_name,
                objective=objective,
                requirements=requirements_text,
                architecture="*(Definir arquitectura)*",
                current_status="🟡 **En Planificación**",
                next_steps="*(Definir próximos pasos)*",
                team="*(Asignar miembros del equipo)*",
                start_date=datetime.now().strftime("%Y-%m-%d"),
                estimated_completion="*(Estimación pendiente)*"
            )
            
            canvas_response = self._create_canvas_via_api(
                client=client,
                content=content,
                title=f"{template.emoji} {project_name}"
            )
            
            if canvas_response.get("success"):
                return {
                    "success": True,
                    "canvas_id": canvas_response["canvas_id"],
                    "canvas_url": canvas_response["canvas_url"],
                    "title": f"{template.emoji} {project_name}",
                    "type": "project"
                }
            else:
                return {"success": False, "error": canvas_response.get("error", "Unknown error")}
            
        except Exception as e:
            logger.error(f"❌ Error creando documentación de proyecto: {e}")
            return {"success": False, "error": str(e)}
    
    def share_canvas_in_channel(self, client, canvas_url: str, channel_id: str, 
                              title: str, canvas_type: str) -> bool:
        """Compartir Canvas en el canal con mensaje descriptivo"""
        try:
            # Emojis y descripciones por tipo
            type_info = {
                "summary": {"emoji": "📊", "desc": "resumen de conversación"},
                "knowledge": {"emoji": "🧠", "desc": "base de conocimiento"},
                "project": {"emoji": "🚀", "desc": "documentación de proyecto"},
                "meeting": {"emoji": "📅", "desc": "notas de reunión"}
            }
            
            info = type_info.get(canvas_type, {"emoji": "📄", "desc": "documento"})
            
            message = f"{info['emoji']} **Canvas creado**: {title}\n" \
                     f"He generado un {info['desc']} colaborativo.\n" \
                     f"Pueden editarlo y agregar contenido: {canvas_url}"
            
            client.chat_postMessage(
                channel=channel_id,
                text=message,
                unfurl_links=True
            )
            
            logger.info(f"✅ Canvas compartido en canal: {channel_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error compartiendo Canvas: {e}")
            return False
    
    def _extract_key_points(self, conversation_history: List[Dict], analysis: Dict) -> str:
        """Extraer puntos clave de la conversación"""
        try:
            # Usar análisis inteligente si está disponible
            topics = analysis.get("topics", [])
            if topics:
                return "\n".join(f"- {topic}" for topic in topics[:5])
            
            # Fallback: extraer de mensajes más largos
            key_messages = [
                msg.get("content", "")[:100] + "..."
                for msg in conversation_history[-10:]
                if len(msg.get("content", "")) > 50 and msg.get("role") == "user"
            ]
            
            if key_messages:
                return "\n".join(f"- {msg}" for msg in key_messages[:3])
            
            return "- *(No se identificaron puntos clave específicos)*"
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo puntos clave: {e}")
            return "- *(Error procesando puntos clave)*"
    
    def _extract_decisions(self, conversation_history: List[Dict], analysis: Dict) -> str:
        """Extraer decisiones tomadas"""
        decision_keywords = ["decidimos", "acordamos", "vamos a", "haremos", "implementar"]
        decisions = []
        
        try:
            for msg in conversation_history[-20:]:
                content = msg.get("content", "").lower()
                if any(keyword in content for keyword in decision_keywords):
                    decisions.append(f"- {msg.get('content', '')[:100]}...")
                    
            if decisions:
                return "\n".join(decisions[:3])
            
            return "- *(No se identificaron decisiones específicas)*"
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo decisiones: {e}")
            return "- *(Error procesando decisiones)*"
    
    def _extract_tasks(self, conversation_history: List[Dict], analysis: Dict) -> str:
        """Extraer tareas identificadas"""
        task_keywords = ["task", "tarea", "hacer", "implementar", "crear", "desarrollar"]
        tasks = []
        
        try:
            for msg in conversation_history[-15:]:
                content = msg.get("content", "").lower()
                if any(keyword in content for keyword in task_keywords):
                    tasks.append(f"- [ ] {msg.get('content', '')[:80]}...")
                    
            if tasks:
                return "\n".join(tasks[:4])
            
            return "- [ ] *(No se identificaron tareas específicas)*"
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo tareas: {e}")
            return "- [ ] *(Error procesando tareas)*"
    
    def _extract_resources(self, conversation_history: List[Dict]) -> str:
        """Extraer recursos y enlaces mencionados"""
        resources = []
        
        try:
            for msg in conversation_history[-20:]:
                content = msg.get("content", "")
                # Buscar URLs
                if "http" in content or "www." in content:
                    resources.append(f"- {content[:100]}...")
                # Buscar archivos mencionados
                elif any(ext in content.lower() for ext in [".py", ".js", ".md", ".json", ".txt"]):
                    resources.append(f"- 📄 {content[:80]}...")
                    
            if resources:
                return "\n".join(resources[:3])
            
            return "- *(No se identificaron recursos específicos)*"
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo recursos: {e}")
            return "- *(Error procesando recursos)*"
    
    def _create_canvas_via_api(self, client, content: str, title: str) -> Dict:
        """Crear Canvas usando API REST directa (bypass SDK)"""
        try:
            # Obtener token del cliente
            token = client.token
            
            # API endpoint
            url = "https://slack.com/api/canvases.create"
            
            # Headers
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # Payload
            payload = {
                "document_content": {
                    "type": "markdown",
                    "markdown": content
                }
            }
            
            logger.info(f"🌐 Llamando Canvas API directamente...")
            logger.info(f"🔗 URL: {url}")
            
            # Hacer request
            response = requests.post(url, headers=headers, json=payload)
            
            logger.info(f"📊 Status code: {response.status_code}")
            logger.info(f"📋 Response: {response.text[:500]}...")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("ok"):
                    canvas_id = data.get("canvas_id")
                    canvas_url = data.get("url")
                    
                    logger.info(f"✅ Canvas creado exitosamente!")
                    logger.info(f"🆔 Canvas ID: {canvas_id}")
                    logger.info(f"🔗 Canvas URL: {canvas_url}")
                    
                    return {
                        "success": True,
                        "canvas_id": canvas_id,
                        "canvas_url": canvas_url
                    }
                else:
                    error = data.get("error", "Unknown error")
                    logger.error(f"❌ Slack API error: {error}")
                    return {"success": False, "error": f"Slack API error: {error}"}
            else:
                logger.error(f"❌ HTTP error: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Error en Canvas API: {e}")
            return {"success": False, "error": str(e)}

# Instancia global
canvas_manager = CanvasManager()