#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
خدمة الشات بوت المتقدمة لنظام آيديا
تستخدم نماذج لغوية متقدمة لتوفير تجربة تفاعلية ذكية
"""

import json
import os
from typing import Dict, List, Optional
from openai import OpenAI
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# إعداد عميل OpenAI
client = OpenAI()

class IdeaChatbot:
    """
    فئة الشات بوت المتقدمة لآيديا
    """
    
    def __init__(self):
        self.conversation_history = {}
        self.company_info = {
            "name": "آيديا للاستشارات والحلول التسويقية",
            "slogan": "أوسع مما تتخيل أدق مما تتوقع",
            "services": [
                "الاستشارات والتطوير",
                "الحلول التسويقية",
                "الحلول الإبداعية",
                "الحلول التقنية",
                "حلول أخرى متخصصة"
            ],
            "contact": {
                "phone": "773171477",
                "email": "info@ideateeam.com",
                "website": "www.ideateeam.com"
            },
            "specialties": [
                "تصميم الهوية البصرية",
                "التسويق الرقمي",
                "تطوير المواقع والتطبيقات",
                "إدارة وسائل التواصل الاجتماعي",
                "الاستشارات التسويقية",
                "تحليل البيانات والأداء"
            ]
        }
        
        self.system_prompt = f"""
أنت مساعد ذكي لشركة {self.company_info['name']} وشعارها "{self.company_info['slogan']}".

معلومات الشركة:
- الخدمات: {', '.join(self.company_info['services'])}
- التخصصات: {', '.join(self.company_info['specialties'])}
- التواصل: هاتف {self.company_info['contact']['phone']}, إيميل {self.company_info['contact']['email']}

مهامك:
1. الإجابة على استفسارات العملاء حول خدمات آيديا
2. تقديم معلومات مفيدة عن الحلول المتاحة
3. توجيه العملاء لطلب الاستشارة المجانية أو الحلول الشاملة
4. الحفاظ على طابع مهني ودود باللغة العربية
5. تقديم اقتراحات مناسبة بناءً على احتياجات العميل

قواعد مهمة:
- استخدم اللغة العربية دائماً
- كن مفيداً ومهنياً
- اقترح الحلول المناسبة من خدمات آيديا
- وجه العملاء لطلب استشارة مجانية عند الحاجة
- لا تقدم معلومات خارج نطاق خدمات آيديا
"""

    def get_ai_response(self, user_message: str, session_id: str) -> str:
        """
        الحصول على رد ذكي من النموذج اللغوي
        """
        try:
            # إدارة تاريخ المحادثة
            if session_id not in self.conversation_history:
                self.conversation_history[session_id] = []
            
            # إضافة رسالة المستخدم للتاريخ
            self.conversation_history[session_id].append({
                "role": "user",
                "content": user_message
            })
            
            # بناء رسائل المحادثة
            messages = [
                {"role": "system", "content": self.system_prompt}
            ] + self.conversation_history[session_id][-10:]  # آخر 10 رسائل
            
            # طلب الرد من النموذج اللغوي
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            # إضافة رد الذكاء الاصطناعي للتاريخ
            self.conversation_history[session_id].append({
                "role": "assistant",
                "content": ai_response
            })
            
            return ai_response
            
        except Exception as e:
            print(f"خطأ في الحصول على رد الذكاء الاصطناعي: {e}")
            return self.get_fallback_response(user_message)
    
    def get_fallback_response(self, user_message: str) -> str:
        """
        ردود احتياطية في حالة فشل الذكاء الاصطناعي
        """
        user_message_lower = user_message.lower()
        
        if any(word in user_message_lower for word in ["مرحبا", "سلام", "أهلا"]):
            return f"مرحباً بك في {self.company_info['name']}! {self.company_info['slogan']}. كيف يمكنني مساعدتك اليوم؟"
        
        elif any(word in user_message_lower for word in ["خدمات", "حلول", "ماذا تقدمون"]):
            services_text = "نقدم مجموعة شاملة من الحلول:\n"
            for service in self.company_info['services']:
                services_text += f"• {service}\n"
            services_text += "\nهل تود معرفة المزيد عن أي من هذه الحلول؟"
            return services_text
        
        elif any(word in user_message_lower for word in ["أسعار", "تكلفة", "سعر"]):
            return "أسعارنا تختلف حسب نوع الحل المطلوب ونطاق المشروع. يمكنك طلب استشارة مجانية للحصول على عرض سعر مخصص يناسب احتياجاتك."
        
        elif any(word in user_message_lower for word in ["تواصل", "اتصال", "تليفون"]):
            return f"يمكنك التواصل معنا:\n📞 هاتف: {self.company_info['contact']['phone']}\n📧 إيميل: {self.company_info['contact']['email']}\n🌐 موقعنا: {self.company_info['contact']['website']}"
        
        else:
            return "شكراً لك على تواصلك معنا. للحصول على إجابة مفصلة على استفسارك، يرجى التواصل مع فريقنا مباشرة أو طلب استشارة مجانية."

# إنشاء مثيل الشات بوت
chatbot = IdeaChatbot()

@app.route('/chat', methods=['POST'])
def chat():
    """
    نقطة نهاية API للشات بوت
    """
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        session_id = data.get('session_id', 'default')
        
        if not user_message:
            return jsonify({'error': 'رسالة فارغة'}), 400
        
        # الحصول على الرد
        response = chatbot.get_ai_response(user_message, session_id)
        
        return jsonify({
            'response': response,
            'session_id': session_id,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': f'خطأ في معالجة الطلب: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/chat/reset', methods=['POST'])
def reset_conversation():
    """
    إعادة تعيين تاريخ المحادثة
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id', 'default')
        
        if session_id in chatbot.conversation_history:
            del chatbot.conversation_history[session_id]
        
        return jsonify({
            'message': 'تم إعادة تعيين المحادثة بنجاح',
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': f'خطأ في إعادة التعيين: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    فحص حالة الخدمة
    """
    return jsonify({
        'status': 'healthy',
        'service': 'آيديا شات بوت',
        'version': '2.0'
    })

if __name__ == '__main__':
    print("🤖 بدء تشغيل خدمة الشات بوت المتقدمة لآيديا...")
    print("🌐 الخدمة متاحة على: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
