#!/usr/bin/env python3
"""
Скрипт для запуска автотестов Pair Helper
Проверяет API, статус контейнеров и логи через Portainer
"""

import sys
import os
import json
from datetime import datetime

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auto_tester import AutoTester

def main():
    """Главная функция"""
    print("🧪 Pair Helper Auto Tests")
    print("=" * 50)
    
    # Создаем тестер
    tester = AutoTester()
    
    # Запускаем тесты
    report = tester.run_all_tests()
    
    # Сохраняем отчет в файл
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"test_report_{timestamp}.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 Отчет сохранен в файл: {report_file}")
    
    # Возвращаем код выхода
    if report["success"]:
        print("\n🎉 Все тесты прошли успешно!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {report['failed_tests']} тестов провалились!")
        sys.exit(1)

if __name__ == "__main__":
    main()
