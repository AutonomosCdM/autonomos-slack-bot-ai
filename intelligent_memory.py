"""
Sistema de Memoria Inteligente - FASE 3
Análisis semántico y contexto avanzado
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import re
from collections import Counter, defaultdict

logger = logging.getLogger(__name__)

class IntelligentMemory:
    """Sistema avanzado de memoria con análisis de contexto y patrones"""
    
    def __init__(self):
        self.topic_keywords = {
            "technical": ["error", "bug", "código", "app", "bot", "servidor", "deploy", "api"],
            "personal": ["nombre", "soy", "me llamo", "trabajo", "empresa", "equipo"],
            "help": ["ayuda", "cómo", "puedes", "necesito", "problema", "soporte"],
            "casual": ["hola", "gracias", "bien", "genial", "excelente", "bueno"],
            "planning": ["proyecto", "tarea", "calendario", "planear", "hacer", "pendiente"]
        }
        
        self.sentiment_patterns = {
            "positive": ["genial", "excelente", "perfecto", "bueno", "gracias", "increíble"],
            "negative": ["problema", "error", "mal", "horrible", "falla", "roto"],
            "neutral": ["ok", "bien", "normal", "regular"],
            "questioning": ["cómo", "qué", "cuándo", "dónde", "por qué", "puedes"]
        }
    
    def analyze_message_context(self, message: str, conversation_history: List[Dict]) -> Dict:
        """Análisis completo del contexto del mensaje"""
        try:
            analysis = {
                "topics": self._extract_topics(message),
                "sentiment": self._analyze_sentiment(message),
                "intent": self._detect_intent(message),
                "entities": self._extract_entities(message),
                "conversation_flow": self._analyze_conversation_flow(conversation_history),
                "urgency": self._assess_urgency(message),
                "complexity": self._assess_complexity(message)
            }
            
            logger.debug(f"🧠 Análisis completo: {analysis}")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error en análisis de contexto: {e}")
            return {}
    
    def _extract_topics(self, message: str) -> List[str]:
        """Extrae temas principales del mensaje"""
        message_lower = message.lower()
        detected_topics = []
        
        for topic, keywords in self.topic_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                detected_topics.append(topic)
        
        return detected_topics or ["general"]
    
    def _analyze_sentiment(self, message: str) -> str:
        """Analiza el sentimiento del mensaje"""
        message_lower = message.lower()
        sentiment_scores = {}
        
        for sentiment, patterns in self.sentiment_patterns.items():
            score = sum(1 for pattern in patterns if pattern in message_lower)
            if score > 0:
                sentiment_scores[sentiment] = score
        
        if not sentiment_scores:
            return "neutral"
        
        return max(sentiment_scores.items(), key=lambda x: x[1])[0]
    
    def _detect_intent(self, message: str) -> str:
        """Detecta la intención del usuario"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["ayuda", "cómo", "puedes", "necesito"]):
            return "help_request"
        elif any(word in message_lower for word in ["gracias", "perfecto", "genial"]):
            return "acknowledgment"
        elif any(word in message_lower for word in ["problema", "error", "falla"]):
            return "issue_report"
        elif any(word in message_lower for word in ["hacer", "crear", "implementar"]):
            return "task_request"
        elif message_lower.startswith(("hola", "buenos", "qué tal")):
            return "greeting"
        else:
            return "information_seeking"
    
    def _extract_entities(self, message: str) -> Dict[str, List[str]]:
        """Extrae entidades nombradas del mensaje"""
        entities = {
            "names": [],
            "technologies": [],
            "projects": [],
            "commands": []
        }
        
        # Nombres propios (empiezan con mayúscula)
        name_pattern = r'\\b[A-Z][a-záéíóú]+\\b'
        entities["names"] = re.findall(name_pattern, message)
        
        # Tecnologías comunes
        tech_words = ["python", "react", "javascript", "slack", "redis", "sqlite", "api", "bot"]
        entities["technologies"] = [tech for tech in tech_words if tech in message.lower()]
        
        # Comandos (empiezan con /)
        command_pattern = r'/\\w+'
        entities["commands"] = re.findall(command_pattern, message)
        
        return entities
    
    def _analyze_conversation_flow(self, history: List[Dict]) -> Dict:
        """Analiza el flujo de la conversación"""
        if not history:
            return {"flow_type": "new_conversation", "topic_continuity": 0}
        
        recent_messages = history[-3:] if len(history) >= 3 else history
        
        topics_sequence = []
        for msg in recent_messages:
            topics = self._extract_topics(msg.get("content", ""))
            topics_sequence.extend(topics)
        
        topic_changes = len(set(topics_sequence))
        
        if topic_changes == 1:
            flow_type = "focused_discussion"
        elif topic_changes <= 2:
            flow_type = "related_topics"
        else:
            flow_type = "topic_jumping"
        
        return {
            "flow_type": flow_type,
            "topic_continuity": 1 / topic_changes if topic_changes > 0 else 1,
            "message_count": len(history)
        }
    
    def _assess_urgency(self, message: str) -> str:
        """Evalúa la urgencia del mensaje"""
        message_lower = message.lower()
        
        urgent_indicators = ["urgente", "inmediato", "ahora", "rápido", "emergency", "crítico"]
        medium_indicators = ["pronto", "necesito", "importante", "help"]
        
        if any(indicator in message_lower for indicator in urgent_indicators):
            return "high"
        elif any(indicator in message_lower for indicator in medium_indicators):
            return "medium"
        else:
            return "low"
    
    def _assess_complexity(self, message: str) -> str:
        """Evalúa la complejidad de la consulta"""
        word_count = len(message.split())
        question_marks = message.count('?')
        technical_terms = len(self._extract_entities(message)["technologies"])
        
        complexity_score = 0
        
        if word_count > 30:
            complexity_score += 2
        elif word_count > 15:
            complexity_score += 1
        
        if question_marks > 1:
            complexity_score += 1
        
        complexity_score += technical_terms
        
        if complexity_score >= 4:
            return "high"
        elif complexity_score >= 2:
            return "medium"
        else:
            return "low"
    
    def generate_smart_context(self, current_message: str, 
                             conversation_history: List[Dict], 
                             user_preferences: Dict = None) -> Dict:
        """Genera contexto inteligente para el LLM"""
        try:
            message_analysis = self.analyze_message_context(current_message, conversation_history)
            
            relevant_history = self._filter_relevant_messages(
                conversation_history, 
                message_analysis["topics"],
                message_analysis["intent"]
            )
            
            context_summary = self._generate_context_summary(relevant_history, message_analysis)
            response_hints = self._generate_response_hints(message_analysis, user_preferences)
            
            smart_context = {
                "message_analysis": message_analysis,
                "relevant_history": relevant_history,
                "context_summary": context_summary,
                "response_hints": response_hints,
                "recommended_tone": self._recommend_tone(message_analysis, user_preferences)
            }
            
            logger.info(f"🧠 Contexto inteligente generado: {len(relevant_history)} mensajes relevantes")
            return smart_context
            
        except Exception as e:
            logger.error(f"❌ Error generando contexto inteligente: {e}")
            return {}
    
    def _filter_relevant_messages(self, history: List[Dict], 
                                current_topics: List[str], 
                                current_intent: str) -> List[Dict]:
        """Filtra mensajes relevantes basado en temas e intención"""
        if not history:
            return []
        
        relevant_messages = []
        
        for msg in history[-10:]:
            msg_content = msg.get("content", "")
            msg_topics = self._extract_topics(msg_content)
            msg_intent = self._detect_intent(msg_content)
            
            relevance_score = 0
            
            common_topics = set(current_topics) & set(msg_topics)
            relevance_score += len(common_topics) * 2
            
            if msg_intent == current_intent:
                relevance_score += 3
            
            if len(relevant_messages) < 3:
                relevance_score += 1
            
            if relevance_score > 2:
                relevant_messages.append(msg)
        
        return relevant_messages[-5:]
    
    def _generate_context_summary(self, relevant_history: List[Dict], 
                                message_analysis: Dict) -> str:
        """Genera un resumen del contexto para el LLM"""
        if not relevant_history:
            return "Nueva conversación sin contexto previo."
        
        user_mentions = []
        key_topics = []
        
        for msg in relevant_history:
            content = msg.get("content", "")
            entities = self._extract_entities(content)
            user_mentions.extend(entities["names"])
            key_topics.extend(self._extract_topics(content))
        
        summary_parts = []
        
        if user_mentions:
            unique_names = list(set(user_mentions))
            summary_parts.append(f"Usuario mencionado: {', '.join(unique_names[:2])}")
        
        if key_topics:
            topic_counts = Counter(key_topics)
            main_topics = [topic for topic, _ in topic_counts.most_common(2)]
            summary_parts.append(f"Temas principales: {', '.join(main_topics)}")
        
        flow_info = message_analysis.get("conversation_flow", {})
        summary_parts.append(f"Flujo: {flow_info.get('flow_type', 'unknown')}")
        
        return ". ".join(summary_parts) + "."
    
    def _generate_response_hints(self, message_analysis: Dict, 
                               user_preferences: Dict = None) -> List[str]:
        """Genera sugerencias para la respuesta"""
        hints = []
        
        intent = message_analysis.get("intent", "")
        sentiment = message_analysis.get("sentiment", "")
        urgency = message_analysis.get("urgency", "")
        
        if intent == "help_request":
            hints.append("Proporcionar ayuda clara y paso a paso")
        elif intent == "issue_report":
            hints.append("Reconocer el problema y ofrecer soluciones")
        elif intent == "greeting":
            hints.append("Responder cordialmente y preguntar cómo ayudar")
        
        if sentiment == "negative":
            hints.append("Usar tono empático y comprensivo")
        elif sentiment == "positive":
            hints.append("Mantener energía positiva")
        
        if urgency == "high":
            hints.append("Responder de manera directa y eficiente")
        
        return hints or ["Responder de manera natural y útil"]
    
    def _recommend_tone(self, message_analysis: Dict, 
                       user_preferences: Dict = None) -> str:
        """Recomienda el tono de respuesta"""
        sentiment = message_analysis.get("sentiment", "neutral")
        intent = message_analysis.get("intent", "")
        urgency = message_analysis.get("urgency", "low")
        
        preferred_style = "casual"
        if user_preferences:
            preferred_style = user_preferences.get("communication_style", "casual")
        
        if urgency == "high" or intent == "issue_report":
            return "professional_helpful"
        elif sentiment == "positive":
            return "friendly_enthusiastic"
        elif sentiment == "negative":
            return "empathetic_supportive"
        else:
            return preferred_style

# Instancia global
intelligent_memory = IntelligentMemory()