"""
FAQ Database and Management System
"""

class FAQDatabase:
    """Manages FAQ database with categories and intelligent matching"""
    
    def __init__(self):
        self.faqs = {
            "General Information": [
                {
                    "question": "What are your business hours?",
                    "answer": "We're available 24/7 for online support. Our phone lines are open Monday-Friday, 9 AM to 6 PM EST.",
                    "keywords": ["hours", "time", "when", "available", "open"]
                },
                {
                    "question": "Where are you located?",
                    "answer": "We have offices worldwide. Our main headquarters is in the United States, with regional offices in Europe and Asia.",
                    "keywords": ["location", "office", "address", "where"]
                },
                {
                    "question": "How can I contact support?",
                    "answer": "You can reach us via this chat, email at support@company.com, or call our hotline. We also have social media support channels.",
                    "keywords": ["contact", "reach", "support", "help", "email", "phone"]
                }
            ],
            "Technical Support": [
                {
                    "question": "How do I reset my password?",
                    "answer": "Click 'Forgot Password' on the login page, enter your email, and follow the reset link sent to your inbox.",
                    "keywords": ["password", "reset", "forgot", "login", "access"]
                },
                {
                    "question": "My app is not working properly",
                    "answer": "Try clearing your cache and cookies, updating to the latest version, or reinstalling the app. If the issue persists, please provide more details.",
                    "keywords": ["not working", "error", "crash", "bug", "problem", "issue"]
                },
                {
                    "question": "How do I update my software?",
                    "answer": "Go to Settings > Updates and click 'Check for Updates'. The system will automatically download and install available updates.",
                    "keywords": ["update", "upgrade", "version", "latest"]
                }
            ],
            "Billing & Payments": [
                {
                    "question": "What payment methods do you accept?",
                    "answer": "We accept credit/debit cards (Visa, MasterCard, Amex), PayPal, bank transfers, and cryptocurrency in select regions.",
                    "keywords": ["payment", "pay", "card", "billing", "method"]
                },
                {
                    "question": "How do I update my billing information?",
                    "answer": "Log into your account, go to Settings > Billing, and click 'Update Payment Method' to change your payment details.",
                    "keywords": ["billing", "payment", "update", "card", "change"]
                },
                {
                    "question": "When will I be charged?",
                    "answer": "Billing occurs on your subscription anniversary date. You'll receive an invoice 3 days before the charge.",
                    "keywords": ["charge", "bill", "when", "date", "invoice"]
                }
            ],
            "Account Management": [
                {
                    "question": "How do I create an account?",
                    "answer": "Click 'Sign Up', enter your email, create a password, and verify your email address. It takes less than 2 minutes!",
                    "keywords": ["create", "sign up", "register", "account", "new"]
                },
                {
                    "question": "How do I delete my account?",
                    "answer": "Go to Settings > Account > Delete Account. Note that this action is permanent and all your data will be removed.",
                    "keywords": ["delete", "remove", "close", "cancel", "account"]
                },
                {
                    "question": "Can I change my email address?",
                    "answer": "Yes! Go to Settings > Profile > Email and enter your new email. You'll need to verify it before the change takes effect.",
                    "keywords": ["email", "change", "update", "modify"]
                }
            ],
            "Product Features": [
                {
                    "question": "What features are included in the free plan?",
                    "answer": "The free plan includes basic features: up to 10 projects, 5GB storage, community support, and access to core tools.",
                    "keywords": ["free", "plan", "features", "include", "basic"]
                },
                {
                    "question": "How do I upgrade my plan?",
                    "answer": "Go to Settings > Subscription > Upgrade. Choose your preferred plan and complete the payment process.",
                    "keywords": ["upgrade", "premium", "pro", "plan", "subscription"]
                },
                {
                    "question": "Can I try premium features before purchasing?",
                    "answer": "Yes! We offer a 14-day free trial of all premium features. No credit card required to start.",
                    "keywords": ["trial", "free", "test", "try", "demo"]
                }
            ],
            "Troubleshooting": [
                {
                    "question": "I'm not receiving email notifications",
                    "answer": "Check your spam folder, verify your email in Settings, and ensure notifications are enabled in your account preferences.",
                    "keywords": ["email", "notification", "not receiving", "spam"]
                },
                {
                    "question": "The page is loading slowly",
                    "answer": "This could be due to internet connection, browser cache, or server load. Try refreshing, clearing cache, or switching browsers.",
                    "keywords": ["slow", "loading", "lag", "performance"]
                },
                {
                    "question": "I can't upload files",
                    "answer": "Check file size limits (max 50MB), supported formats, and available storage. Ensure your browser allows file uploads.",
                    "keywords": ["upload", "file", "attach", "can't", "unable"]
                }
            ]
        }
    
    def search_faq(self, query, category=None):
        """
        Search FAQs based on query and optional category
        Returns list of matching FAQs sorted by relevance
        """
        query_lower = query.lower()
        results = []
        
        categories = [category] if category else self.faqs.keys()
        
        for cat in categories:
            if cat in self.faqs:
                for faq in self.faqs[cat]:
                    score = 0
                    # Check keywords
                    for keyword in faq["keywords"]:
                        if keyword in query_lower:
                            score += 2
                    
                    # Check question
                    question_words = faq["question"].lower().split()
                    for word in question_words:
                        if len(word) > 3 and word in query_lower:
                            score += 1
                    
                    if score > 0:
                        results.append({
                            "category": cat,
                            "question": faq["question"],
                            "answer": faq["answer"],
                            "score": score
                        })
        
        # Sort by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:3]  # Return top 3 matches
    
    def get_all_categories(self):
        """Get all FAQ categories"""
        return list(self.faqs.keys())
    
    def get_faqs_by_category(self, category):
        """Get all FAQs in a specific category"""
        return self.faqs.get(category, [])
