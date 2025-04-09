import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

NUM_USERS = 5000
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2025, 4, 1)
EVENTS = [
    'open_app', 'search', 'view_product', 'add_to_cart', 'pay_page', 'finish_pay',
    'like', 'remove_from_cart', 'abandon_cart', 'apply_coupon', 'scroll_page'
]
CITIES = ['Москва', 'Санкт-Петербург', 'Казань', 'Новосибирск', 'Екатеринбург']
PLATFORMS = ['iOS', 'Android']

user_types = ['active', 'medium', 'rare']
user_type_probs = [0.4, 0.4, 0.2]
user_df = pd.DataFrame({
    'user_id': [i for i in range(NUM_USERS)],
    'city': np.random.choice(CITIES, NUM_USERS),
    'platform': np.random.choice(PLATFORMS, NUM_USERS),
    'user_type': np.random.choice(user_types, NUM_USERS, p=user_type_probs)
})

# Симуляция сессий и ивентов
sessions = []
events_log = []

def generate_session_events(user_type):
    event_chain = ['open_app']
    if random.random() < 0.9:
        event_chain.append('search')
    if random.random() < 0.7:
        event_chain.append('view_product')
    if random.random() < 0.6:
        event_chain.append('add_to_cart')
        if random.random() < 0.3:
            event_chain.append('remove_from_cart')
    if random.random() < 0.4:
        event_chain.append('abandon_cart')
    if 'add_to_cart' in event_chain and random.random() < 0.5:
        event_chain.append('apply_coupon')
    if 'add_to_cart' in event_chain and random.random() < 0.5:
        event_chain.append('pay_page')
        if random.random() < 0.8:
            event_chain.append('finish_pay')
    if random.random() < 0.5:
        event_chain.append('like')
    if random.random() < 0.7:
        event_chain.append('scroll_page')
    return event_chain


def is_valid_purchase_time(dt):
    return 7 <= dt.hour < 23

def generate_sessions_for_user(user_id, user_type):
    sessions_for_user = []
    num_sessions = {
        'active': random.randint(30, 70),
        'medium': random.randint(15, 30),
        'rare': random.randint(3, 10)
    }[user_type]
    start = START_DATE + timedelta(days=random.randint(0, 10))
    for _ in range(num_sessions):
        session_time = start + timedelta(days=random.randint(0, 100), hours=random.randint(7, 22), minutes=random.randint(0, 59))
        event_chain = generate_session_events(user_type)
        for i, event in enumerate(event_chain):
            timestamp = session_time + timedelta(seconds=i * random.randint(20, 60))
            if event == 'finish_pay' and not is_valid_purchase_time(timestamp):
                continue
            events_log.append({
                'user_id': user_id,
                'event': event,
                'timestamp': timestamp,
                'session_id': f"{user_id}_{session_time.date()}_{session_time.time()}"
            })

for _, row in user_df.iterrows():
    generate_sessions_for_user(row['user_id'], row['user_type'])

events_df = pd.DataFrame(events_log)
events_df = events_df.sort_values(by=['user_id', 'timestamp']).reset_index(drop=True)
user_df.head(), events_df.head()