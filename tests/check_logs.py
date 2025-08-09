#!/usr/bin/env python3
"""
Получение логов контейнеров через Portainer API
"""

import requests
import json
from urllib3.exceptions import InsecureRequestWarning
import urllib3
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Отключаем предупреждения о SSL
urllib3.disable_warnings(InsecureRequestWarning)

class PortainerLogsChecker:
    def __init__(self):
        self.base_url = "https://192.168.2.228:31015"
        self.username = os.getenv("PORTAINER_USERNAME", "admin")
        self.password = os.getenv("PORTAINER_PASSWORD", "admin")
        self.session = requests.Session()
        self.session.verify = False
        self.token = None
        
    def authenticate(self):
        """Аутентификация в Portainer"""
        try:
            auth_url = f"{self.base_url}/api/auth"
            auth_data = {
                "Username": self.username,
                "Password": self.password
            }
            
            response = self.session.post(auth_url, json=auth_data)
            if response.status_code == 200:
                self.token = response.json().get("jwt")
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                print("✅ Аутентификация в Portainer успешна")
                return True
            else:
                print(f"❌ Ошибка аутентификации: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Ошибка при аутентификации: {e}")
            return False
    
    def get_endpoints(self):
        """Получение списка endpoints"""
        try:
            response = self.session.get(f"{self.base_url}/api/endpoints")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Ошибка получения endpoints: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Ошибка при получении endpoints: {e}")
            return []
    
    def get_containers(self, endpoint_id):
        """Получение списка контейнеров"""
        try:
            response = self.session.get(f"{self.base_url}/api/endpoints/{endpoint_id}/docker/containers/json")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Ошибка получения контейнеров: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Ошибка при получении контейнеров: {e}")
            return []
    
    def get_container_logs(self, endpoint_id, container_id, tail=50):
        """Получение логов контейнера"""
        try:
            params = {
                "stdout": "true",
                "stderr": "true",
                "tail": str(tail)
            }
            
            response = self.session.get(
                f"{self.base_url}/api/endpoints/{endpoint_id}/docker/containers/{container_id}/logs",
                params=params
            )
            
            if response.status_code == 200:
                return response.text
            else:
                print(f"❌ Ошибка получения логов: {response.status_code}")
                return ""
        except Exception as e:
            print(f"❌ Ошибка при получении логов: {e}")
            return ""
    
    def find_container_by_name(self, endpoint_id, container_name):
        """Поиск контейнера по имени"""
        containers = self.get_containers(endpoint_id)
        for container in containers:
            names = container.get("Names", [])
            if any(container_name in name for name in names):
                return container
        return None
    
    def check_all_logs(self):
        """Проверка логов всех контейнеров Pair Helper"""
        print("🔍 Проверка логов контейнеров Pair Helper...")
        print("=" * 60)
        
        # Аутентификация
        if not self.authenticate():
            return
        
        # Получаем endpoints
        endpoints = self.get_endpoints()
        if not endpoints:
            print("❌ Не удалось получить endpoints")
            return
        
        endpoint_id = endpoints[0]["Id"]
        print(f"🔗 Endpoint ID: {endpoint_id}")
        
        # Контейнеры для проверки
        containers_to_check = [
            "pair-helper-backend",
            "pair-helper-frontend", 
            "pair-helper-bot",
            "pair-helper-admin"
        ]
        
        for container_name in containers_to_check:
            print(f"\n🐳 Проверка контейнера: {container_name}")
            print("-" * 40)
            
            container = self.find_container_by_name(endpoint_id, container_name)
            if container:
                container_id = container["Id"]
                state = container.get("State", "unknown")
                status = container.get("Status", "unknown")
                
                print(f"   ID: {container_id}")
                print(f"   Состояние: {state}")
                print(f"   Статус: {status}")
                
                if state == "running":
                    logs = self.get_container_logs(endpoint_id, container_id, tail=20)
                    if logs:
                        print(f"   Последние логи ({len(logs)} символов):")
                        print("   " + "─" * 50)
                        for line in logs.split('\n')[-10:]:  # Последние 10 строк
                            if line.strip():
                                print(f"   {line}")
                        print("   " + "─" * 50)
                    else:
                        print("   Логи пусты")
                else:
                    print("   Контейнер не запущен")
            else:
                print("   Контейнер не найден")
        
        print("\n" + "=" * 60)
        print("✅ Проверка логов завершена!")

def main():
    checker = PortainerLogsChecker()
    checker.check_all_logs()

if __name__ == "__main__":
    main()
