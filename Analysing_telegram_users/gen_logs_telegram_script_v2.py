import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
from pandas.tseries.offsets import DateOffset

# Инициализация
fake = Faker()
Faker.seed(42)
random.seed(42)
np.random.seed(42)

# Параметры
total_users = 10000
premium_users = 1250

event_types = [
    "view_main_screen", "open_dialog", "send_message", "open_chat", "send_sticker", 
    "buy_gift", "buy_premium", "react_to_message", "voice_call", "video_call", 
    "send_voice_message", "send_video_message"
]

premium_event_types = [
    "use_custom_emoji", "post_story", "voice_to_text", "extra_cloud_storage", 
    "emoji_status_profile", "custom_profile", "telegram_app_icon", 
    "animated_profile_picture", "extra_reactions"
]

premium_event_weights = {
    "voice_to_text": 0.22,
    "emoji_status_profile": 0.10,
    "extra_reactions": 0.16,
    "post_story": 0.12,
    "use_custom_emoji": 0.16,
    "extra_cloud_storage": 0.08,
    "custom_profile": 0.05,
    "telegram_app_icon": 0.05,
    "animated_profile_picture": 0.06
}

premium_types = ["3_months", "6_months", "12_months"]
platforms = ["iOS", "Android", "Desktop", "Web"]
locations = ["Moscow", "Saint Petersburg", "Novosibirsk", "Ekaterinburg", "Kazan", "Nizhny Novgorod"]

# Категории активности
activity_categories = {
    'active': {'percentage': 0.20, 'min_sessions': 15, 'max_sessions': 30, 'min_events': 20, 'max_events': 40},
    'medium': {'percentage': 0.50, 'min_sessions': 8, 'max_sessions': 20, 'min_events': 10, 'max_events': 20},
    'rare': {'percentage': 0.30, 'min_sessions': 3, 'max_sessions': 8, 'min_events': 1, 'max_events': 10}
}

start_date = datetime(2023, 1, 1)

# Шаг 1: Генерация базовых данных пользователей
user_data = pd.DataFrame({
    "user_id": np.arange(1, total_users + 1),
    "location": np.random.choice(locations, total_users)
})

# Функция для назначения категории активности
def assign_activity_category():
    rand_value = np.random.random()
    if rand_value < activity_categories['active']['percentage']:
        return 'active'
    elif rand_value < (activity_categories['active']['percentage'] + activity_categories['medium']['percentage']):
        return 'medium'
    else:
        return 'rare'

user_data['activity_category'] = user_data['user_id'].apply(lambda x: assign_activity_category())

# Шаг 2: Распределение премиумов по активности с учетом вероятности конверсии
conversion_rate_by_activity = {
    "active": 0.20,  # вероятность покупки для активных пользователей
    "medium": 0.05,  # вероятность для средних пользователей
    "rare": 0.05     # вероятность для редких пользователей
}

premium_user_ids = []

# Для каждого пользователя проверяем, становится ли он премиум в зависимости от активности
for user in user_data.itertuples():
    activity_category = user.activity_category
    purchase_probability = conversion_rate_by_activity[activity_category]
    
    if np.random.random() < purchase_probability:
        premium_user_ids.append(user.user_id)

# Обновляем статус премиум пользователей
user_data["is_premium"] = user_data["user_id"].isin(premium_user_ids).astype(int)

# Шаг 3: Платформы
def assign_platform(row):
    if row["is_premium"] == 1:
        return np.random.choice(["iOS", "Android", "Desktop", "Web"], p=[0.75, 0.15, 0.05, 0.05])
    else:
        return np.random.choice(["iOS", "Android", "Desktop", "Web"], p=[0.4, 0.3, 0.15, 0.15])

user_data["platform"] = user_data.apply(assign_platform, axis=1)

# Шаг 4: Генерация логов
# --- ДОП. ФУНКЦИЯ: генерация сессий ---
def generate_session_events(user, session_date, session_id, event_multiplier=1.0):
    events = []
    events_count = np.random.randint(
        int(activity_categories[user.activity_category]['min_events'] * event_multiplier),
        int(activity_categories[user.activity_category]['max_events'] * event_multiplier) + 1
    )

    for _ in range(events_count):
        event_type = random.choices(
            event_types, weights=[10, 10, 15, 20, 10, 2, 0, 10, 5, 5, 8, 7], k=1
        )[0]
        timestamp = session_date + timedelta(seconds=np.random.randint(0, 86400))

        events.append({
            "user_id": user.user_id,
            "session_id": session_id,
            "timestamp": timestamp,
            "event_type": event_type
        })

        # премиум события ТОЛЬКО после подписки
        if user.is_premium == 1 and event_multiplier > 1.0:
            for _ in range(np.random.randint(1, 4)):
                premium_usage_logs.append({
                    "user_id": user.user_id,
                    "timestamp": timestamp,
                    "premium_event_type": np.random.choice(
                        list(premium_event_weights.keys()), 
                        p=list(premium_event_weights.values())
                    )
                })

    return events

# --- ШАГ 4: Генерация логов с разной активностью до/после подписки ---
logs, premium_logs, premium_usage_logs = [], [], []

for user in user_data.itertuples():
    activity_category = user.activity_category
    total_sessions = np.random.randint(
        activity_categories[activity_category]['min_sessions'], 
        activity_categories[activity_category]['max_sessions'] + 1
    )

    if user.is_premium == 1:
        # покупка в случайный день между 5 и 25 числом месяца
        premium_date = start_date + timedelta(days=np.random.randint(5, 26), seconds=np.random.randint(0, 86400))
        subscription_type = np.random.choice(premium_types)

        # лог покупки премиума
        logs.append({
            "user_id": user.user_id,
            "session_id": fake.uuid4(),
            "timestamp": premium_date,
            "event_type": "buy_premium"
        })
        premium_logs.append({
            "user_id": user.user_id,
            "timestamp": premium_date,
            "subscription_type": subscription_type,
            "purchase_source": np.random.choice(["in-app", "website"], p=[0.8, 0.2]),
            "purchase_price": price_by_type[subscription_type]
        })

        # генерируем сессии до и после
        for i in range(total_sessions):
            session_id = fake.uuid4()
            session_offset = np.random.randint(-10, 10)  # +-10 дней от даты подписки
            session_date = premium_date + timedelta(days=session_offset)

            if session_date >= premium_date:
                logs.extend(generate_session_events(user, session_date, session_id, event_multiplier=1.5))  # активнее после
            else:
                logs.extend(generate_session_events(user, session_date, session_id, event_multiplier=1.0))  # обычная активность

    else:
        for _ in range(total_sessions):
            session_id = fake.uuid4()
            session_date = start_date + timedelta(days=np.random.randint(0, 31))
            logs.extend(generate_session_events(user, session_date, session_id, event_multiplier=1.0))

logs_df = pd.DataFrame(logs)
premium_logs_df = pd.DataFrame(premium_logs)
premium_usage_df = pd.DataFrame(premium_usage_logs)

logs_df.to_csv("telegram_logs.csv", index=False)
premium_logs_df.to_csv("telegram_premium_users.csv", index=False)
premium_usage_df.to_csv("telegram_premium_usage.csv", index=False)

print("Основные данные сгенерированы и сохранены")

# Шаг 5: Исторические подписки
historical_logs = []
historical_users = user_data['user_id'].tolist()
num_hist_premium = int(len(historical_users) * 0.13)
hist_premium_ids = random.sample(historical_users, num_hist_premium)

for user_id in hist_premium_ids:
    num_purchases = np.random.choice([1, 2, 3], p=[0.6, 0.3, 0.1])
    purchase_dates = []

    for _ in range(num_purchases):
        subscription_type = np.random.choice(premium_types)
        purchase_date = datetime(2022, 1, 1) + timedelta(days=np.random.randint(0, 365), seconds=np.random.randint(0, 86400))
        while purchase_date in purchase_dates:
            purchase_date = datetime(2022, 1, 1) + timedelta(days=np.random.randint(0, 365), seconds=np.random.randint(0, 86400))
        purchase_dates.append(purchase_date)

        historical_logs.append({
            "user_id": user_id,
            "timestamp": purchase_date,
            "subscription_type": subscription_type,
            "purchase_source": np.random.choice(["in-app", "website"], p=[0.8, 0.2]),
            "purchase_price": price_by_type[subscription_type]
        })

premium_logs_df_hist = pd.DataFrame(historical_logs)
premium_logs_df_hist.to_csv("telegram_premium_historical_2022.csv", index=False)

print("Исторические данные за 2022 год сохранены")

# Шаг 6: Обновление user_data по состоянию на 2023-01-01
def get_subscription_end(row):
    months = {"3_months": 3, "6_months": 6, "12_months": 12}
    return row['timestamp'] + DateOffset(months=months[row['subscription_type']])

premium_logs_df_hist['subscription_end'] = premium_logs_df_hist.apply(get_subscription_end, axis=1)
check_date = pd.Timestamp("2023-01-01")

active_premium = premium_logs_df_hist[
    (premium_logs_df_hist['timestamp'] <= check_date) &
    (premium_logs_df_hist['subscription_end'] > check_date)
]['user_id'].unique()

user_data['is_premium'] = user_data['user_id'].isin(active_premium).astype(int)
user_data.to_csv("telegram_user_data.csv", index=False)

print("Флаг is_premium обновлён на основе данных на 01.01.2023")