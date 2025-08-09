import requests
import json
import time
from typing import Dict, List, Optional
from urllib3.exceptions import InsecureRequestWarning
import urllib3

# Отключаем предупреждения о небезопасных запросах для self-signed сертификатов
urllib3.disable_warnings(InsecureRequestWarning)

class PortainerClient:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.verify = False  # Для self-signed сертификатов
        self.token = None
        
    def authenticate(self) -> bool:
        """Аутентификация в Portainer API"""
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
                return True
            else:
                print(f"Ошибка аутентификации: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Ошибка при аутентификации: {e}")
            return False
    
    def get_endpoints(self) -> List[Dict]:
        """Получение списка endpoints"""
        try:
            response = self.session.get(f"{self.base_url}/api/endpoints")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Ошибка получения endpoints: {response.status_code}")
                return []
        except Exception as e:
            print(f"Ошибка при получении endpoints: {e}")
            return []
    
    def get_containers(self, endpoint_id: int) -> List[Dict]:
        """Получение списка контейнеров"""
        try:
            response = self.session.get(f"{self.base_url}/api/endpoints/{endpoint_id}/docker/containers/json")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Ошибка получения контейнеров: {response.status_code}")
                return []
        except Exception as e:
            print(f"Ошибка при получении контейнеров: {e}")
            return []
    
    def get_container_logs(self, endpoint_id: int, container_id: str, 
                          tail: int = 100, since: Optional[str] = None) -> str:
        """Получение логов контейнера"""
        try:
            params = {
                "stdout": "true",
                "stderr": "true",
                "tail": str(tail)
            }
            if since:
                params["since"] = since
                
            response = self.session.get(
                f"{self.base_url}/api/endpoints/{endpoint_id}/docker/containers/{container_id}/logs",
                params=params
            )
            
            if response.status_code == 200:
                return response.text
            else:
                print(f"Ошибка получения логов: {response.status_code}")
                return ""
        except Exception as e:
            print(f"Ошибка при получении логов: {e}")
            return ""
    
    def get_container_info(self, endpoint_id: int, container_id: str) -> Optional[Dict]:
        """Получение информации о контейнере"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/endpoints/{endpoint_id}/docker/containers/{container_id}/json"
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Ошибка получения информации о контейнере: {response.status_code}")
                return None
        except Exception as e:
            print(f"Ошибка при получении информации о контейнере: {e}")
            return None
    
    def find_container_by_name(self, endpoint_id: int, container_name: str) -> Optional[Dict]:
        """Поиск контейнера по имени"""
        containers = self.get_containers(endpoint_id)
        for container in containers:
            names = container.get("Names", [])
            if any(container_name in name for name in names):
                return container
        return None
