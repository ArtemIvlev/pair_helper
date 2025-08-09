import time
import json
from datetime import datetime
from typing import Dict, List, Optional
from config import TestConfig
from portainer_client import PortainerClient
from api_client import APIClient

class AutoTester:
    def __init__(self):
        self.config = TestConfig()
        self.portainer = PortainerClient(
            self.config.PORTAINER_URL,
            self.config.PORTAINER_USERNAME,
            self.config.PORTAINER_PASSWORD
        )
        self.api_client = APIClient(self.config.API_BASE_URL)
        self.test_results = []
        self.endpoint_id = None
        
    def run_all_tests(self) -> Dict:
        """Запуск всех тестов"""
        print("🚀 Запуск автотестов Pair Helper...")
        print(f"📅 Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Проверяем учетные данные
        self.config.validate_credentials()
        
        # Аутентификация в Portainer
        if not self.portainer.authenticate():
            print("❌ Ошибка аутентификации в Portainer")
            print("   Проверьте логин/пароль и доступность Portainer")
            return {"success": False, "error": "Portainer authentication failed"}
        
        # Получаем endpoint ID
        endpoints = self.portainer.get_endpoints()
        if not endpoints:
            print("❌ Не удалось получить endpoints из Portainer")
            return {"success": False, "error": "No endpoints found"}
        
        self.endpoint_id = endpoints[0]["Id"]  # Берем первый endpoint
        print(f"✅ Подключение к Portainer: {self.config.PORTAINER_URL}")
        print(f"🔗 Endpoint ID: {self.endpoint_id}")
        
        # Запускаем тесты
        tests = [
            self.test_api_health,
            self.test_api_docs,
            self.test_container_status,
            self.test_user_registration,
            self.test_invitation_system,
            self.test_container_logs
        ]
        
        for test in tests:
            try:
                result = test()
                self.test_results.append(result)
                self._print_test_result(result)
            except Exception as e:
                error_result = {
                    "test_name": test.__name__,
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                self.test_results.append(error_result)
                self._print_test_result(error_result)
        
        # Формируем итоговый отчет
        return self._generate_report()
    
    def test_api_health(self) -> Dict:
        """Тест здоровья API"""
        print("\n🔍 Тест здоровья API...")
        result = self.api_client.health_check()
        
        return {
            "test_name": "API Health Check",
            "success": result["success"],
            "status_code": result["status_code"],
            "response": result["response"],
            "timestamp": datetime.now().isoformat()
        }
    
    def test_api_docs(self) -> Dict:
        """Тест документации API"""
        print("\n📚 Тест документации API...")
        result = self.api_client.get_docs()
        
        return {
            "test_name": "API Documentation",
            "success": result["success"],
            "status_code": result["status_code"],
            "response": result["response"][:100] + "..." if len(result["response"]) > 100 else result["response"],
            "timestamp": datetime.now().isoformat()
        }
    
    def test_container_status(self) -> Dict:
        """Тест статуса контейнеров"""
        print("\n🐳 Тест статуса контейнеров...")
        containers = self.portainer.get_containers(self.endpoint_id)
        
        container_status = {}
        for container_name, expected_name in self.config.CONTAINERS.items():
            container = self.portainer.find_container_by_name(self.endpoint_id, expected_name)
            if container:
                state = container.get("State", "unknown")
                status = container.get("Status", "unknown")
                container_status[container_name] = {
                    "found": True,
                    "state": state,
                    "status": status,
                    "running": state == "running"
                }
            else:
                container_status[container_name] = {
                    "found": False,
                    "state": "not_found",
                    "status": "not_found",
                    "running": False
                }
        
        all_running = all(status["running"] for status in container_status.values())
        
        return {
            "test_name": "Container Status",
            "success": all_running,
            "container_status": container_status,
            "timestamp": datetime.now().isoformat()
        }
    
    def test_user_registration(self) -> Dict:
        """Тест регистрации пользователя"""
        print("\n👤 Тест регистрации пользователя...")
        
        # Регистрируем тестового пользователя
        register_result = self.api_client.register_user(
            self.config.TEST_TELEGRAM_ID,
            self.config.TEST_USER_FIRST_NAME
        )
        
        if not register_result["success"]:
            return {
                "test_name": "User Registration",
                "success": False,
                "error": register_result["response"],
                "timestamp": datetime.now().isoformat()
            }
        
        # Проверяем, что пользователь создался
        get_user_result = self.api_client.get_user(self.config.TEST_TELEGRAM_ID)
        
        return {
            "test_name": "User Registration",
            "success": get_user_result["success"],
            "registration_result": register_result,
            "get_user_result": get_user_result,
            "timestamp": datetime.now().isoformat()
        }
    
    def test_invitation_system(self) -> Dict:
        """Тест системы приглашений"""
        print("\n🎫 Тест системы приглашений...")
        
        # Создаем приглашение
        create_result = self.api_client.create_invitation(self.config.TEST_TELEGRAM_ID)
        
        if not create_result["success"]:
            return {
                "test_name": "Invitation System",
                "success": False,
                "error": create_result["response"],
                "timestamp": datetime.now().isoformat()
            }
        
        invitation_code = create_result["response"].get("code")
        if not invitation_code:
            return {
                "test_name": "Invitation System",
                "success": False,
                "error": "No invitation code received",
                "timestamp": datetime.now().isoformat()
            }
        
        # Получаем информацию о приглашении
        info_result = self.api_client.get_invitation_info(invitation_code)
        
        return {
            "test_name": "Invitation System",
            "success": info_result["success"],
            "invitation_code": invitation_code,
            "create_result": create_result,
            "info_result": info_result,
            "timestamp": datetime.now().isoformat()
        }
    
    def test_container_logs(self) -> Dict:
        """Тест логов контейнеров"""
        print("\n📋 Тест логов контейнеров...")
        
        logs_info = {}
        for container_name, expected_name in self.config.CONTAINERS.items():
            container = self.portainer.find_container_by_name(self.endpoint_id, expected_name)
            if container:
                container_id = container["Id"]
                logs = self.portainer.get_container_logs(self.endpoint_id, container_id, tail=50)
                
                # Анализируем логи на наличие ошибок
                error_keywords = ["ERROR", "error", "Exception", "Traceback", "Failed", "failed"]
                has_errors = any(keyword in logs for keyword in error_keywords)
                
                logs_info[container_name] = {
                    "found": True,
                    "logs_length": len(logs),
                    "has_errors": has_errors,
                    "recent_logs": logs[-500:] if logs else ""  # Последние 500 символов
                }
            else:
                logs_info[container_name] = {
                    "found": False,
                    "logs_length": 0,
                    "has_errors": False,
                    "recent_logs": ""
                }
        
        # Проверяем, что нет критических ошибок
        has_critical_errors = any(info["has_errors"] for info in logs_info.values())
        
        return {
            "test_name": "Container Logs",
            "success": not has_critical_errors,
            "logs_info": logs_info,
            "timestamp": datetime.now().isoformat()
        }
    
    def _print_test_result(self, result: Dict):
        """Вывод результата теста"""
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{status} {result['test_name']}")
        
        if not result["success"] and "error" in result:
            print(f"   Ошибка: {result['error']}")
    
    def _generate_report(self) -> Dict:
        """Генерация итогового отчета"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "=" * 60)
        print("📊 ИТОГОВЫЙ ОТЧЕТ")
        print("=" * 60)
        print(f"Всего тестов: {total_tests}")
        print(f"Пройдено: {passed_tests}")
        print(f"Провалено: {failed_tests}")
        print(f"Успешность: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Проваленные тесты:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test_name']}")
                    if "error" in result:
                        print(f"    Ошибка: {result['error']}")
        
        return {
            "success": failed_tests == 0,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests/total_tests)*100,
            "results": self.test_results,
            "timestamp": datetime.now().isoformat()
        }
