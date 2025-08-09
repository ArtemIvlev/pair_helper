import requests
import json
import time
from typing import Dict, List, Optional
from urllib3.exceptions import InsecureRequestWarning
import urllib3

# Отключаем предупреждения о небезопасных запросах
urllib3.disable_warnings(InsecureRequestWarning)

class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.verify = False  # Для self-signed сертификатов
        
    def health_check(self) -> Dict:
        """Проверка здоровья API"""
        try:
            response = self.session.get(f"{self.base_url}/docs")
            return {
                "status_code": response.status_code,
                "response": response.text if response.status_code != 200 else "OK",
                "success": response.status_code == 200
            }
        except Exception as e:
            return {
                "status_code": 0,
                "response": str(e),
                "success": False
            }
    
    def get_docs(self) -> Dict:
        """Получение документации API"""
        try:
            response = self.session.get(f"{self.base_url}/docs")
            return {
                "status_code": response.status_code,
                "response": response.text[:200] + "..." if len(response.text) > 200 else response.text,
                "success": response.status_code == 200
            }
        except Exception as e:
            return {
                "status_code": 0,
                "response": str(e),
                "success": False
            }
    
    def register_user(self, telegram_id: int, first_name: str) -> Dict:
        """Регистрация пользователя"""
        try:
            data = {
                "telegram_id": telegram_id,
                "first_name": first_name,
                "accept_terms": True,
                "accept_privacy": True
            }
            response = self.session.post(f"{self.base_url}/v1/users/register", json=data)
            return {
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text,
                "success": response.status_code == 200
            }
        except Exception as e:
            return {
                "status_code": 0,
                "response": str(e),
                "success": False
            }
    
    def get_user(self, telegram_id: int) -> Dict:
        """Получение пользователя по Telegram ID"""
        try:
            response = self.session.get(f"{self.base_url}/v1/users/me", params={"telegram_id": telegram_id})
            return {
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text,
                "success": response.status_code == 200
            }
        except Exception as e:
            return {
                "status_code": 0,
                "response": str(e),
                "success": False
            }
    
    def create_invitation(self, inviter_telegram_id: int) -> Dict:
        """Создание приглашения"""
        try:
            response = self.session.post(
                f"{self.base_url}/v1/invitations/generate",
                params={"inviter_telegram_id": inviter_telegram_id}
            )
            return {
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text,
                "success": response.status_code == 200
            }
        except Exception as e:
            return {
                "status_code": 0,
                "response": str(e),
                "success": False
            }
    
    def get_invitation_info(self, code: str) -> Dict:
        """Получение информации о приглашении"""
        try:
            response = self.session.get(f"{self.base_url}/v1/invitations/{code}")
            return {
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text,
                "success": response.status_code == 200
            }
        except Exception as e:
            return {
                "status_code": 0,
                "response": str(e),
                "success": False
            }
    
    def use_invitation(self, code: str, invitee_telegram_id: int) -> Dict:
        """Использование приглашения"""
        try:
            response = self.session.post(
                f"{self.base_url}/v1/invitations/{code}/use",
                params={"invitee_telegram_id": invitee_telegram_id}
            )
            return {
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text,
                "success": response.status_code == 200
            }
        except Exception as e:
            return {
                "status_code": 0,
                "response": str(e),
                "success": False
            }
