#!/usr/bin/env python
"""
Скрипт для выдачи 5 бесплатных раскладов всем существующим пользователям, у кого их меньше.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import UserProfile

def give_free_readings():
    updated = 0
    for user in UserProfile.objects.all():
        if user.balance < 5:
            user.balance = 5
            user.save()
            print(f"✅ Пользователь {user.username or user.telegram_user_id}: баланс установлен на 5")
            updated += 1
        else:
            print(f"⏭️  Пользователь {user.username or user.telegram_user_id}: баланс {user.balance} (не изменен)")
    print(f"\n🎯 Обновлено пользователей: {updated}")

if __name__ == '__main__':
    give_free_readings() 