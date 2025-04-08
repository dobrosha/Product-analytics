import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
from pandas.tseries.offsets import DateOffset
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY

# Инициализация
fake = Faker()
Faker.seed(42)
random.seed(42)
np.random.seed(42)

# Параметры
total_users = 10000
premium_users = 1200

# Начальная дата и дата окончания
start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 6, 30)

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
price_by_type = {
    "3_months": 899,
    "6_months": 1690,
    "12_months": 3190
}

locations = ["Moscow", "Saint Petersburg", "Novosibirsk", "Ekaterinburg", "Kazan", "Nizhny Novgorod"]

activity_categories = {
    'active': {'percentage': 0.20, 'min_sessions': 15, 'max_sessions': 30, 'min_events': 20, 'max_events': 40},
    'medium': {'percentage': 0.50, 'min_sessions': 8, 'max_sessions': 20, 'min_events': 10, 'max_events': 20},
    'rare': {'percentage': 0.30, 'min_sessions': 3, 'max_sessions': 8, 'min_events': 1, 'max_events': 10}
}

# start_date = datetime(2023, 1, 1)
# end_date = datetime(2023, 6, 30)

# Шаг 1: Базовые данные пользователей
user_data = pd.DataFrame({
    "user_id": np.arange(1, total_users + 1),
    "location": np.random.choice(locations, total_users)
})

def assign_activity_category():
    rand_value = np.random.random()
    if rand_value < activity_categories['active']['percentage']:
        return 'active'
    elif rand_value < (activity_categories['active']['percentage'] + activity_categories['medium']['percentage']):
        return 'medium'
    else:
        return 'rare'

user_data['activity_category'] = user_data['user_id'].apply(lambda x: assign_activity_category())

# Шаг 2: Премиум статус
conversion_rate_by_activity = {
    "active": 0.20,
    "medium": 0.05,
    "rare": 0.05
}

premium_user_ids = []

for user in user_data.itertuples():
    activity_category = user.activity_category
    if np.random.random() < conversion_rate_by_activity[activity_category]:
        premium_user_ids.append(user.user_id)

user_data["is_premium"] = user_data["user_id"].isin(premium_user_ids).astype(int)

# Шаг 3: Преобладающая платформа
def assign_dominant_platform():
    return np.random.choice(["iOS", "Android"], p=[0.6, 0.4])

user_data["dominant_platform"] = user_data["user_id"].apply(lambda x: assign_dominant_platform())

# Шаг 4: Генерация логов
logs = []
premium_logs = []  # Создадим список для премиум логов

# Контекстная логика премиум-событий
def get_contextual_premium_event(user, timestamp):
    hour = timestamp.hour
    platform = user.dominant_platform

    # Ночные фичи: облако, эмодзи
    if 0 <= hour <= 6:
        night_features = ["extra_cloud_storage", "emoji_status_profile"]
        weights = [0.7, 0.3]
        return np.random.choice(night_features, p=weights)

    # Утро-день: голос в текст и сторис
    elif 7 <= hour <= 17:
        day_features = ["voice_to_text", "post_story", "use_custom_emoji"]
        weights = [0.4, 0.3, 0.3]
        return np.random.choice(day_features, p=weights)

    # Вечер: реакшены, иконки, аватарки
    else:
        evening_features = ["extra_reactions", "telegram_app_icon", "animated_profile_picture"]
        weights = [0.5, 0.3, 0.2]

        # iOS чаще меняет иконку
        if platform == "iOS":
            weights = [0.4, 0.4, 0.2]

        return np.random.choice(evening_features, p=weights)


# Обновлённая функция генерации событий
def generate_session_events(user, session_date, session_id, event_multiplier=1.0):
    events = []

    is_mobile = np.random.rand() < 0.80
    session_platform = user.dominant_platform if is_mobile else "Desktop"

    events_count = np.random.randint(
        int(activity_categories[user.activity_category]['min_events'] * event_multiplier),
        int(activity_categories[user.activity_category]['max_events'] * event_multiplier) + 1
    )

    weekday = session_date.weekday()

    if weekday < 5:
        if np.random.rand() < 0.7:
            evening_seconds = np.random.randint(18 * 3600, 24 * 3600)
            session_start = session_date + timedelta(seconds=evening_seconds)
        else:
            session_start = session_date + timedelta(seconds=np.random.randint(0, 86400 - 3600))
    else:
        if np.random.rand() < 0.5:
            day_seconds = np.random.randint(10 * 3600, 18 * 3600)
            session_start = session_date + timedelta(seconds=day_seconds)
        else:
            evening_seconds = np.random.randint(18 * 3600, 24 * 3600)
            session_start = session_date + timedelta(seconds=evening_seconds)

    deltas = np.cumsum(np.random.randint(2, 10, size=events_count))
    timestamps = [session_start + timedelta(seconds=int(s)) for s in deltas]

    used_timestamps = set()

    for i in range(events_count):
        timestamp = timestamps[i]
        while timestamp in used_timestamps:
            timestamp += timedelta(seconds=1)
        used_timestamps.add(timestamp)

        event_type = random.choices(
            event_types, weights=[10, 10, 15, 20, 10, 2, 0, 10, 5, 5, 8, 7], k=1
        )[0]

        events.append({
            "user_id": user.user_id,
            "session_id": session_id,
            "timestamp": timestamp,
            "event_type": event_type,
            "platform": session_platform
        })

        # Контекстные премиум-события, только если это премиум и после даты покупки
        if user.is_premium == 1 and event_multiplier > 1.0 and np.random.rand() < 0.7:
            num_premium_events = np.random.choice([1, 2, 3], p=[0.6, 0.3, 0.1])

            for _ in range(num_premium_events):
                premium_event_type = get_contextual_premium_event(user, timestamp)

                offset_sec = np.random.randint(1, 5)
                premium_timestamp = timestamp + timedelta(seconds=offset_sec)
                while premium_timestamp in used_timestamps:
                    premium_timestamp += timedelta(seconds=1)
                used_timestamps.add(premium_timestamp)

                events.append({
                    "user_id": user.user_id,
                    "session_id": session_id,
                    "timestamp": premium_timestamp,
                    "event_type": premium_event_type,
                    "platform": session_platform
                })

    return events


# Генерация сессий по активности и подписке

premium_purchase_dates = {}

for user in user_data.itertuples():
    activity_category = user.activity_category
    premium_date = None

    # Если пользователь премиум — создаём покупку
    if user.is_premium == 1:
        # Генерация случайной даты покупки в период с начала до конца периода
        premium_purchase_date = start_date + timedelta(
            days=np.random.randint(0, (end_date - start_date).days + 1),
            seconds=np.random.randint(0, 86400)
        )
        
        # Случайный выбор типа подписки
        subscription_type = np.random.choice(premium_types, p=[0.15, 0.25, 0.60])
        
        # Событие покупки премиума
        logs.append({
            "user_id": user.user_id,
            "session_id": fake.uuid4(),
            "timestamp": premium_purchase_date,
            "event_type": "buy_premium",
            "platform": user.dominant_platform
        })
        
        premium_logs.append({
            "user_id": user.user_id,
            "timestamp": premium_purchase_date,
            "subscription_type": subscription_type,
            "purchase_source": np.random.choice(["in-app", "website"], p=[0.8, 0.2]),
            "purchase_price": price_by_type[subscription_type]
        })

        premium_purchase_dates[user.user_id] = premium_purchase_date
        premium_date = premium_purchase_date

    # Генерация сессий по активности
    if activity_category == 'active':
        session_dates = pd.date_range(start=start_date, end=end_date, freq='D')
        for session_date in session_dates:
            sessions_in_day = np.random.randint(1, 3)  # 1 или 2 сессии в день
            for _ in range(sessions_in_day):
                session_id = fake.uuid4()  # Генерация уникального session_id
                multiplier = 1.4 if premium_date and session_date >= premium_date else 1.0
                logs.extend(generate_session_events(user, session_date, session_id, event_multiplier=multiplier))

    elif activity_category == 'medium':
        weeks = pd.date_range(start=start_date, end=end_date, freq='W')
        for week_start in weeks:
            session_date = week_start + timedelta(days=np.random.randint(0, 7))
            sessions_in_day = np.random.randint(1, 3)  # 1 или 2 сессии в неделю
            for _ in range(sessions_in_day):
                session_id = fake.uuid4()  # Генерация уникального session_id
                multiplier = 1.4 if premium_date and session_date >= premium_date else 1.0
                logs.extend(generate_session_events(user, session_date, session_id, event_multiplier=multiplier))

    elif activity_category == 'rare':
        months = pd.date_range(start=start_date, end=end_date, freq='M')
        for month_start in months:
            session_date = month_start + timedelta(days=np.random.randint(0, 31))
            sessions_in_day = 1  # Обычно только одна сессия в месяц
            for _ in range(sessions_in_day):
                session_id = fake.uuid4()  # Генерация уникального session_id
                multiplier = 1.4 if premium_date and session_date >= premium_date else 1.0
                logs.extend(generate_session_events(user, session_date, session_id, event_multiplier=multiplier))


logs_df = pd.DataFrame(logs)
logs_df.to_csv("telegram_logs.csv", index=False)

premium_purchase_df = pd.DataFrame(premium_logs)  # Таблица премиум пользователей
premium_purchase_df.to_csv("telegram_premium_purchases.csv", index=False)  # Сохраняем таблицу премиум пользователей

print("Основные данные сгенерированы и сохранены")


# Шаг 5: История за 2022
historical_logs = []
historical_users = user_data['user_id'].tolist()
num_hist_premium = int(len(historical_users) * 0.08)
hist_premium_ids = random.sample(historical_users, num_hist_premium)

for user_id in hist_premium_ids:
    num_purchases = np.random.choice([1, 2, 3], p=[0.6, 0.3, 0.1])
    purchase_dates = []

    for _ in range(num_purchases):
        subscription_type = np.random.choice(premium_types, p=[0.15, 0.25, 0.60])
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

def calculate_subscription_periods(premium_df):
    months = {"3_months": 3, "6_months": 6, "12_months": 12}
    premium_df = premium_df.sort_values(by=["user_id", "timestamp"])

    result = []
    current_ends = {}

    for row in premium_df.itertuples():
        user_id = row.user_id
        sub_months = months[row.subscription_type]
        purchase_time = row.timestamp

        prev_end = current_ends.get(user_id, purchase_time)
        new_start = max(purchase_time, prev_end)
        new_end = new_start + DateOffset(months=sub_months)
        current_ends[user_id] = new_end

        result.append(new_end)

    premium_df["subscription_end"] = result
    return premium_df

# Шаг 6: Обновление статуса на 30.06.2023

# Применяем логику подписки
premium_logs_df_hist = calculate_subscription_periods(premium_logs_df_hist)

# premium_logs_df_hist['subscription_end'] = premium_logs_df_hist.apply(get_subscription_end, axis=1)
check_date = pd.Timestamp("2023-06-30")

active_premium = premium_logs_df_hist[
    (premium_logs_df_hist['timestamp'] <= check_date) &
    (premium_logs_df_hist['subscription_end'] > check_date)
]['user_id'].unique()

user_data['is_premium'] = user_data['user_id'].isin(active_premium).astype(int)
user_data.to_csv("telegram_user_data.csv", index=False)

premium_logs_df_hist.to_csv("telegram_premium_historical_2022.csv", index=False)
print("Исторические данные за 2022 год сохранены")

print("Флаг is_premium обновлён на основе данных на 01.01.2023")


