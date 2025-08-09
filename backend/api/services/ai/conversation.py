"""
Conversation Service with GPT Integration
Handles conversation logic, context management, and intent recognition
"""
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import openai
from sqlalchemy.orm import Session
import uuid

from api.config import settings
from api.models.call import CallTranscript, CallEvent
from api.models.agent import Agent
from api.utils.logger import setup_logger

logger = setup_logger(__name__)


class ConversationService:
    """Service for managing conversations with GPT integration"""
    
    def __init__(self):
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
        else:
            logger.warning("OpenAI API key not configured")
        
        self.model = settings.GPT_MODEL or "gpt-4"
        self.temperature = settings.GPT_TEMPERATURE or 0.7
        self.max_tokens = settings.GPT_MAX_TOKENS or 150
    
    async def generate_response(
        self,
        db: Session,
        call_id: uuid.UUID,
        user_message: str,
        agent: Agent,
        context: Optional[Dict] = None
    ) -> Tuple[str, Optional[Dict]]:
        """
        Generate AI response based on user message and conversation history
        
        Args:
            db: Database session
            call_id: Call ID for history tracking
            user_message: The user's message
            agent: Agent configuration
            context: Optional context information
            
        Returns:
            Tuple of (response_text, intent_data)
        """
        try:
            # Get conversation history
            history = self._get_conversation_history(db, call_id)
            
            # Store user message
            self._store_transcript(
                db, call_id, user_message, "user"
            )
            
            # Detect intent
            intent = self._detect_intent(user_message, context)
            
            # Get knowledge base context if available
            kb_context = self._get_knowledge_context(
                db, agent, user_message, intent
            )
            
            # Build prompt with agent configuration
            prompt_messages = self._build_prompt(
                agent, history, user_message, 
                intent, context, kb_context
            )
            
            # Generate response
            response = await self._call_gpt(prompt_messages)
            
            # Store assistant response
            self._store_transcript(
                db, call_id, response, "assistant", intent
            )
            
            return response, intent
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            fallback = agent.fallback_message or "I apologize, I didn't understand that. Could you please repeat?"
            return fallback, None
    
    def _get_conversation_history(
        self, db: Session, call_id: uuid.UUID, limit: int = 10
    ) -> List[Dict]:
        """Get recent conversation history for context"""
        transcripts = db.query(CallTranscript).filter(
            CallTranscript.call_id == call_id
        ).order_by(CallTranscript.timestamp.desc()).limit(limit).all()
        
        # Reverse to get chronological order
        transcripts.reverse()
        
        return [
            {
                "role": "user" if t.speaker == "user" else "assistant",
                "content": t.text
            }
            for t in transcripts
        ]
    
    def _detect_intent(
        self, message: str, context: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Detect user intent from message
        
        Returns dict with intent type and entities
        """
        intent_patterns = {
            "appointment": {
                "keywords": ["appointment", "schedule", "book", "meeting", "time", "date", "available"],
                "keywords_de": ["termin", "buchung", "vereinbaren", "uhrzeit", "datum", "verfügbar"]
            },
            "support": {
                "keywords": ["problem", "help", "issue", "broken", "error", "not working"],
                "keywords_de": ["problem", "hilfe", "funktioniert nicht", "kaputt", "fehler", "störung"]
            },
            "information": {
                "keywords": ["information", "hours", "price", "cost", "where", "address", "how"],
                "keywords_de": ["information", "öffnungszeiten", "preis", "kosten", "wo", "adresse", "wie"]
            },
            "cancel": {
                "keywords": ["cancel", "cancellation", "abort", "stop"],
                "keywords_de": ["absagen", "stornieren", "abbrechen", "beenden"]
            },
            "reschedule": {
                "keywords": ["reschedule", "change", "move", "different time"],
                "keywords_de": ["verschieben", "ändern", "umbuchen", "andere zeit"]
            },
            "greeting": {
                "keywords": ["hello", "hi", "good morning", "good day"],
                "keywords_de": ["hallo", "guten tag", "hi", "servus", "grüß"]
            },
            "goodbye": {
                "keywords": ["bye", "goodbye", "thanks", "thank you", "end"],
                "keywords_de": ["tschüss", "auf wiederhören", "danke", "ende", "bis dann"]
            }
        }
        
        message_lower = message.lower()
        detected_intent = None
        max_score = 0.0
        
        for intent_type, patterns in intent_patterns.items():
            all_keywords = patterns.get("keywords", []) + patterns.get("keywords_de", [])
            matches = sum(1 for keyword in all_keywords if keyword in message_lower)
            
            if matches > 0:
                score = matches / len(all_keywords)
                if score > max_score:
                    max_score = score
                    detected_intent = intent_type
        
        if detected_intent:
            return {
                "type": detected_intent,
                "confidence": max_score,
                "entities": self._extract_entities(message, detected_intent)
            }
        
        return None
    
    def _extract_entities(self, message: str, intent_type: str) -> Dict:
        """Extract relevant entities based on intent type"""
        entities = {}
        
        if intent_type == "appointment":
            # Extract date/time references
            time_references = {
                "tomorrow": ["tomorrow", "morgen"],
                "today": ["today", "heute"],
                "monday": ["monday", "montag"],
                "tuesday": ["tuesday", "dienstag"],
                "wednesday": ["wednesday", "mittwoch"],
                "thursday": ["thursday", "donnerstag"],
                "friday": ["friday", "freitag"],
                "morning": ["morning", "vormittag", "morgens"],
                "afternoon": ["afternoon", "nachmittag", "nachmittags"],
                "evening": ["evening", "abend", "abends"]
            }
            
            message_lower = message.lower()
            for entity_type, keywords in time_references.items():
                for keyword in keywords:
                    if keyword in message_lower:
                        entities["time_reference"] = entity_type
                        break
        
        return entities
    
    def _get_knowledge_context(
        self,
        db: Session,
        agent: Agent,
        message: str,
        intent: Optional[Dict]
    ) -> Optional[str]:
        """Get relevant context from agent's knowledge base"""
        if not agent.knowledge_base:
            return None
        
        # Extract relevant information from knowledge base
        # This is a simplified version - in production, you'd use vector search
        kb = agent.knowledge_base
        context_parts = []
        
        # Add business information
        if kb.get("business_info"):
            context_parts.append(f"Business Info: {kb['business_info']}")
        
        # Add relevant FAQ based on intent
        if intent and kb.get("faqs"):
            relevant_faqs = []
            for faq in kb["faqs"]:
                if intent["type"] in faq.get("tags", []):
                    relevant_faqs.append(f"Q: {faq['question']}\nA: {faq['answer']}")
            
            if relevant_faqs:
                context_parts.append("Relevant FAQs:\n" + "\n".join(relevant_faqs[:3]))
        
        return "\n\n".join(context_parts) if context_parts else None
    
    def _build_prompt(
        self,
        agent: Agent,
        history: List[Dict],
        user_message: str,
        intent: Optional[Dict],
        context: Optional[Dict],
        kb_context: Optional[str]
    ) -> List[Dict]:
        """Build prompt messages for GPT"""
        
        # Start with agent's system prompt
        system_content = agent.system_prompt or "You are a helpful AI assistant."
        
        # Add agent personality
        if agent.personality_traits:
            traits = ", ".join(agent.personality_traits)
            system_content += f"\n\nPersonality: {traits}"
        
        # Add context
        if context:
            if context.get("caller_info"):
                system_content += f"\n\nCaller Information: {json.dumps(context['caller_info'])}"
            if context.get("business_hours"):
                system_content += f"\nBusiness Hours: {context['business_hours']}"
        
        # Add detected intent
        if intent:
            system_content += f"\n\nDetected Intent: {intent['type']} (confidence: {intent['confidence']:.2f})"
            if intent.get("entities"):
                system_content += f"\nExtracted Entities: {json.dumps(intent['entities'])}"
        
        # Add knowledge base context
        if kb_context:
            system_content += f"\n\nRelevant Information:\n{kb_context}"
        
        # Add conversation rules
        system_content += "\n\nConversation Rules:"
        system_content += f"\n- Primary language: {agent.language or 'English'}"
        system_content += "\n- Keep responses concise and natural for phone conversations"
        system_content += "\n- Be helpful and professional"
        system_content += f"\n- Maximum response length: {self.max_tokens} tokens"
        
        if agent.greeting_message and not history:
            system_content += f"\n- Start with greeting: {agent.greeting_message}"
        
        messages = [{"role": "system", "content": system_content}]
        
        # Add conversation history (last 6 messages for context)
        messages.extend(history[-6:])
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    async def _call_gpt(self, messages: List[Dict]) -> str:
        """Call OpenAI GPT API"""
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"GPT API error: {e}")
            raise
    
    def _store_transcript(
        self,
        db: Session,
        call_id: uuid.UUID,
        text: str,
        speaker: str,
        intent: Optional[Dict] = None
    ):
        """Store conversation transcript"""
        transcript = CallTranscript(
            call_id=call_id,
            text=text,
            speaker=speaker,
            intent=json.dumps(intent) if intent else None,
            timestamp=datetime.utcnow()
        )
        db.add(transcript)
        db.commit()
    
    def get_conversation_summary(
        self, db: Session, call_id: uuid.UUID
    ) -> Dict:
        """Get summary of conversation"""
        transcripts = db.query(CallTranscript).filter(
            CallTranscript.call_id == call_id
        ).order_by(CallTranscript.timestamp).all()
        
        if not transcripts:
            return {"status": "no_conversation"}
        
        # Analyze conversation
        intents = []
        for transcript in transcripts:
            if transcript.intent:
                try:
                    intent_data = json.loads(transcript.intent)
                    intents.append(intent_data)
                except:
                    pass
        
        # Determine primary intent
        intent_types = [i["type"] for i in intents if i]
        primary_intent = max(set(intent_types), key=intent_types.count) if intent_types else "unknown"
        
        # Calculate duration
        duration = (transcripts[-1].timestamp - transcripts[0].timestamp).seconds if len(transcripts) > 1 else 0
        
        return {
            "call_id": str(call_id),
            "message_count": len(transcripts),
            "primary_intent": primary_intent,
            "detected_intents": list(set(intent_types)),
            "duration_seconds": duration,
            "last_message": transcripts[-1].text if transcripts else None,
            "transcripts": [
                {
                    "speaker": t.speaker,
                    "text": t.text,
                    "timestamp": t.timestamp.isoformat()
                }
                for t in transcripts[-10:]  # Last 10 messages
            ]
        }


# Singleton instance
conversation_service = ConversationService()