import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

NUM_USERS = 5000
START_DATE = datetime(2024, 2, 1)
END_DATE = datetime(2024, 5, 31)
EVENTS = [
    'open_app', 'search', 'view_product', 'add_to_cart', 'pay_page', 'finish_pay',
    'like', 'remove_from_cart', 'abandon_cart', 'apply_coupon', 'scroll_page'
]
CITIES = ['Москва', 'Санкт-Петербург', 'Казань', 'Новосибирск', 'Екатеринбург']
PLATFORMS = ['iOS', 'Android']

user_types = ['active', 'medium', 'rare']
user_type_probs = [0.3, 0.5, 0.2]
user_df = pd.DataFrame({
    'user_id': [i for i in range(NUM_USERS)],
    'city': np.random.choice(CITIES, NUM_USERS),
    'platform': np.random.choice(PLATFORMS, NUM_USERS),
    'user_type': np.random.choice(user_types, NUM_USERS, p=user_type_probs)
})

# ===== Таблица маркетинговых кампаний =====

campaigns_df = pd.DataFrame([
    {
        'campaign_id': 'push_abandon_cart',
        'campaign_type': 'push',
        'start_date': datetime(2024, 2, 5),
        'end_date': datetime(2024, 2, 19),
        'channel': 'push',
        'budget': 0,
        'goal': 'recover_abandoned_cart'
    },
    {
        'campaign_id': 'email_weekly_newsletter',
        'campaign_type': 'email',
        'start_date': datetime(2024, 3, 1),
        'end_date': datetime(2024, 4, 1),
        'channel': 'email',
        'budget': 0,
        'goal': 'engagement_increase'
    },
    {
        'campaign_id': 'push_delivery_discount',
        'campaign_type': 'push',
        'start_date': datetime(2024, 2, 20),
        'end_date': datetime(2024, 2, 27),
        'channel': 'push',
        'budget': 0,
        'goal': 'promote_delivery'
    }
])


# Симуляция сессий и ивентов
sessions = []
events_log = []

def generate_session_events(user_type, is_test_user=False):
    event_chain = ['open_app']
    if random.random() < 0.9:
        event_chain.append('search')
    if random.random() < 0.7:
        event_chain.append('view_product')
    if random.random() < 0.6:
        event_chain.append('add_to_cart')
        if random.random() < 0.3:
            event_chain.append('remove_from_cart')
    if random.random() < 0.7:
        event_chain.append('abandon_cart')
    if 'add_to_cart' in event_chain and random.random() < 0.5:
        event_chain.append('apply_coupon')
    if 'add_to_cart' in event_chain and random.random() < 0.5:
        event_chain.append('pay_page')
        
        # увеличиваем шанс конверсии для тест-группы
        if is_test_user:
            if random.random() < 0.3:  # увеличенная вероятность для тест-группы
                event_chain.append('finish_pay')
        else:
            if random.random() < 0.2:  # обычная вероятность для контроля
                event_chain.append('finish_pay')

    if random.random() < 0.5:
        event_chain.append('like')
    if random.random() < 0.7:
        event_chain.append('scroll_page')
    return event_chain


def is_valid_purchase_time(dt):
    return 7 <= dt.hour < 23





# === 1. Предсобираем eligible пользователей

eligible_user_dict = dict()  # user_id -> ts (любой один ts на пользователя)
# eligible_users = set()
temp_events_log = []

for _, row in user_df.iterrows():
    user_id = row['user_id']
    user_type = row['user_type']
    num_sessions = {
        'active': random.randint(18, 40),
        'medium': random.randint(8, 18),
        'rare': random.randint(4, 8)
    }[user_type]

    start = START_DATE + timedelta(days=random.randint(0, 10))
    for _ in range(num_sessions):
        session_time = start + timedelta(days=random.randint(0, 100), hours=random.randint(7, 22), minutes=random.randint(0, 59))
        event_chain = generate_session_events(user_type, is_test_user=False)
        session_id = f"{user_id}_{session_time.date()}_{session_time.time()}"

        for i, event in enumerate(event_chain):
            timestamp = session_time + timedelta(seconds=i * random.randint(20, 60))
            if event == 'finish_pay' and not is_valid_purchase_time(timestamp):
                continue
            temp_events_log.append({
                'user_id': user_id,
                'event': event,
                'timestamp': timestamp,
                'session_id': session_id
            })

        if ('pay_page' in event_chain and 'finish_pay' not in event_chain) or ('abandon_cart' in event_chain):
            ts = session_time + timedelta(minutes=5)
            campaign_start = campaigns_df.loc[campaigns_df['campaign_id'] == 'push_abandon_cart', 'start_date'].iloc[0]
            campaign_end = campaigns_df.loc[campaigns_df['campaign_id'] == 'push_abandon_cart', 'end_date'].iloc[0]
            if campaign_start <= ts <= campaign_end:
                if user_id not in eligible_user_dict:
                    eligible_user_dict[user_id] = ts
                # eligible_users.add((user_id, ts))

 
# === 2. Делим на test / control

eligible_user_ids = list(eligible_user_dict.keys())
random.shuffle(eligible_user_ids)

test_size = int(len(eligible_user_ids) * 0.5)
test_user_ids = set(eligible_user_ids[:test_size])
control_user_ids = set(eligible_user_ids[test_size:])

# Формируем test_group и control_group в том же формате: (user_id, ts)
test_group = [(user_id, eligible_user_dict[user_id]) for user_id in test_user_ids]
control_group = [(user_id, eligible_user_dict[user_id]) for user_id in control_user_ids]

test_users_set = set(user_id for user_id, _ in test_group)

# eligible_users = list(eligible_users)
# random.shuffle(eligible_users)
# test_size = int(len(eligible_users) * 0.5)
# test_group = eligible_users[:test_size]
# control_group = eligible_users[test_size:]
# test_users_set = set(user_id for user_id, _ in test_group)


# === 3. Генерируем сессии с учётом is_test_user
events_log = []

for _, row in user_df.iterrows():
    user_id = row['user_id']
    user_type = row['user_type']
    is_test = user_id in test_users_set

    num_sessions = {
        'active': random.randint(18, 40),
        'medium': random.randint(8, 18),
        'rare': random.randint(4, 8)
    }[user_type]

    start = START_DATE + timedelta(days=random.randint(0, 10))
    for _ in range(num_sessions):
        session_time = start + timedelta(days=random.randint(0, 100), hours=random.randint(7, 22), minutes=random.randint(0, 59))
        event_chain = generate_session_events(user_type, is_test_user=is_test)
        session_id = f"{user_id}_{session_time.date()}_{session_time.time()}"

        for i, event in enumerate(event_chain):
            timestamp = session_time + timedelta(seconds=i * random.randint(20, 60))
            if event == 'finish_pay' and not is_valid_purchase_time(timestamp):
                continue
            events_log.append({
                'user_id': user_id,
                'event': event,
                'timestamp': timestamp,
                'session_id': session_id
            })

events_df = pd.DataFrame(events_log).sort_values(by=['user_id', 'timestamp']).reset_index(drop=True)

# === 4. Кампании: касания
touchpoints = []

for user_id, ts in test_group:
    touchpoints.append({
        'user_id': user_id,
        'campaign_id': 'push_abandon_cart',
        'timestamp': ts,
        'reaction': np.random.choice(['clicked', 'ignored', 'converted'], p=[0.3, 0.6, 0.1])
    })

campaign_interactions_df = pd.DataFrame(touchpoints)
control_group_df = pd.DataFrame(control_group, columns=['user_id', 'fake_touch_time'])




events_df.to_csv("lavka_events_df.csv", index=False)
user_df.to_csv("lavka_user_df.csv", index=False)
campaigns_df.to_csv("lavka_campaigns_df.csv", index=False)
campaign_interactions_df.to_csv("lavka_campaign_interactions_df.csv", index=False)

# control_group_df = pd.DataFrame(control_group, columns=['user_id', 'fake_touch_time'])
control_group_df.to_csv("lavka_control_group_df.csv", index=False)


# ======================= Результат =======================
print("Users:")
print(user_df.head())

print("\nEvents:")
print(events_df.head())

print("\nCampaigns:")
print(campaigns_df.head())

print("\nCampaign Interactions:")
print(campaign_interactions_df.head())

test_user_ids = set(user_id for user_id, _ in test_group)
control_user_ids = set(user_id for user_id, _ in control_group)

intersection = test_user_ids & control_user_ids
print(f"Пересечений в группах: {len(intersection)}")  # должно быть 0
