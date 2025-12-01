"""
Core AI Assistant Logic
Handles conversation, FAQ matching, and escalation decisions
"""
import openai
from typing import List, Dict, Optional
import config
from backend.app.core.faq_database import FAQDatabase


class AIAssistant:
    """Main AI Assistant class for handling support conversations"""
    
    def __init__(self):
        openai.api_key = config.OPENAI_API_KEY
        self.faq_db = FAQDatabase()
        self.conversation_history = []
        self.escalation_triggered = False
        
    def process_query(self, user_message: str, language: str = "en") -> Dict:
        """
        Process user query and generate response
        Returns dict with response, type (faq/ai/escalation), and metadata
        """
        # Check for escalation keywords first
        if self._should_escalate(user_message):
            return self._create_escalation_response(user_message, language)
        
        # Search FAQ database
        faq_results = self.faq_db.search_faq(user_message)
        
        # If strong FAQ match found, use it
        if faq_results and faq_results[0]["score"] >= 3:
            return self._create_faq_response(faq_results[0], language)
        
        # Otherwise, use AI for response
        return self._create_ai_response(user_message, language, faq_results)
    
    def _should_escalate(self, message: str) -> bool:
        """Check if query should be escalated to human agent"""
        message_lower = message.lower()
        
        # Check for escalation keywords
        for keyword in config.ESCALATION_KEYWORDS:
            if keyword in message_lower:
                return True
        
        # Check for complex issues (multiple questions, frustration indicators)
        frustration_indicators = ["frustrated", "angry", "terrible", "awful", "disgusted"]
        if any(indicator in message_lower for indicator in frustration_indicators):
            return True
        
        return False
    
    def _create_escalation_response(self, message: str, language: str) -> Dict:
        """Create escalation response"""
        self.escalation_triggered = True
        
        escalation_messages = {
            "en": "I understand this is important. I'm connecting you with a human support agent who can better assist you. They'll be with you shortly.",
            "es": "Entiendo que esto es importante. Te estoy conectando con un agente de soporte humano que puede asistirte mejor. Estarán contigo en breve.",
            "fr": "Je comprends que c'est important. Je vous mets en relation avec un agent de support humain qui pourra mieux vous aider. Ils seront avec vous sous peu.",
            "de": "Ich verstehe, dass dies wichtig ist. Ich verbinde Sie mit einem menschlichen Support-Agenten, der Ihnen besser helfen kann. Sie werden in Kürze bei Ihnen sein.",
            "hi": "मैं समझता हूं कि यह महत्वपूर्ण है। मैं आपको एक मानव सहायता एजेंट से जोड़ रहा हूं जो आपकी बेहतर सहायता कर सकता है। वे शीघ्र ही आपके पास होंगे।",
            "zh": "我理解这很重要。我正在将您连接到可以更好地协助您的人工支持代理。他们很快就会为您服务。",
            "pt": "Entendo que isso é importante. Estou conectando você com um agente de suporte humano que pode ajudá-lo melhor. Eles estarão com você em breve.",
            "it": "Capisco che questo è importante. Ti sto connettendo con un agente di supporto umano che può assisterti meglio. Saranno con te a breve.",
            "ja": "これが重要であることを理解しています。より良いサポートができる人間のサポートエージェントにおつなぎします。すぐに対応いたします。",
            "ar": "أفهم أن هذا مهم. أقوم بتوصيلك بوكيل دعم بشري يمكنه مساعدتك بشكل أفضل. سيكونون معك قريبًا."
        }
        
        return {
            "response": escalation_messages.get(language, escalation_messages["en"]),
            "type": "escalation",
            "escalated": True,
            "metadata": {
                "reason": "Escalation requested or complex issue detected"
            }
        }
    
    def _create_faq_response(self, faq: Dict, language: str) -> Dict:
        """Create response based on FAQ match"""
        return {
            "response": faq["answer"],
            "type": "faq",
            "escalated": False,
            "metadata": {
                "category": faq["category"],
                "question": faq["question"],
                "confidence": faq["score"]
            }
        }
    
    def _create_ai_response(self, message: str, language: str, faq_context: List[Dict]) -> Dict:
        """Generate AI-powered response using GPT"""
        # Build context from FAQ results
        context = ""
        if faq_context:
            context = "\n\nRelated information from our knowledge base:\n"
            for idx, faq in enumerate(faq_context[:2], 1):
                context += f"{idx}. {faq['question']}: {faq['answer']}\n"
        
        # Build conversation with system prompt
        messages = [
            {
                "role": "system",
                "content": f"""You are a helpful, friendly customer support assistant. Your role is to:
1. Answer customer questions clearly and concisely
2. Be empathetic and professional
3. Use the provided knowledge base information when relevant
4. If you don't know something, admit it and offer to connect them with a specialist
5. Keep responses conversational but professional
6. Respond in {config.SUPPORTED_LANGUAGES.get(language, 'English')}

{context}"""
            }
        ]
        
        # Add conversation history (last 5 messages)
        messages.extend(self.conversation_history[-5:])
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        try:
            response = openai.chat.completions.create(
                model=config.AI_MODEL,
                messages=messages,
                temperature=config.TEMPERATURE,
                max_tokens=config.MAX_TOKENS
            )
            
            ai_response = response.choices[0].message.content
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": message})
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            return {
                "response": ai_response,
                "type": "ai",
                "escalated": False,
                "metadata": {
                    "model": config.AI_MODEL,
                    "has_context": len(faq_context) > 0
                }
            }
        
        except Exception as e:
            return {
                "response": "I apologize, but I'm having trouble processing your request right now. Please try again or connect with a human agent.",
                "type": "error",
                "escalated": False,
                "metadata": {
                    "error": str(e)
                }
            }
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
        self.escalation_triggered = False
    
    def get_conversation_summary(self) -> str:
        """Get summary of conversation for handoff to human agent"""
        if not self.conversation_history:
            return "No conversation history"
        
        summary = "Conversation Summary:\n\n"
        for msg in self.conversation_history:
            role = "Customer" if msg["role"] == "user" else "AI Assistant"
            summary += f"{role}: {msg['content']}\n\n"
        
        return summary
