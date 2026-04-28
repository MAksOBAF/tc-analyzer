from collections import Counter
from datetime import datetime

def get_users(messages):
    return sorted(list(set(str(m.get("from", "System")) for m in messages if "from" in m)))

def analyze(messages, filter_user="Все"):
    stats = Counter()
    daily_data = {} # {date: {'msgs': int, 'hours': float}}
    periods = {"Утро (06-12)": 0, "День (12-18)": 0, "Вечер (18-00)": 0, "Ночь (00-06)": 0}
    total_sec = 0
    
    msgs = [m for m in messages if "from" in m and "date" in m]
    if filter_user != "Все":
        msgs = [m for m in msgs if str(m.get("from")) == filter_user]
    
    msgs.sort(key=lambda x: x["date"])
    prev_time = None

    for m in msgs:
        date_str = m["date"].replace("Z", "+00:00")
        curr_time = datetime.fromisoformat(date_str)
        day = curr_time.date()
        hour = curr_time.hour
        
        # Статистика пользователей
        stats[str(m["from"])] += 1
        
        # Распределение по времени суток
        if 6 <= hour < 12: periods["Утро (06-12)"] += 1
        elif 12 <= hour < 18: periods["День (12-18)"] += 1
        elif 18 <= hour < 24: periods["Вечер (18-00)"] += 1
        else: periods["Ночь (00-06)"] += 1

        # Данные по дням
        if day not in daily_data: 
            daily_data[day] = {'msgs': 0, 'hours': 0.0, 'sessions': 1}
        
        daily_data[day]['msgs'] += 1
        
        # Считаем время (порог сессии 15 минут)
        if prev_time and prev_time.date() == day:
            diff = (curr_time - prev_time).total_seconds()
            if diff < 1800: 
                daily_data[day]['hours'] += diff / 3600
                total_sec += diff
            else:
                daily_data[day]['sessions'] += 1
        prev_time = curr_time

    if not daily_data:
        return stats, {}, 0, {}

    # Вычисление рекордов
    most_active_msgs = max(daily_data.items(), key=lambda x: x[1]['msgs'])
    most_active_hours = max(daily_data.items(), key=lambda x: x[1]['hours'])
    
    # Топ 4 дня по времени
    top_days = sorted(daily_data.items(), key=lambda x: x[1]['hours'], reverse=True)[:4]

    # Превращаем периоды в проценты
    total_msgs = sum(periods.values())
    periods_pct = {k: (v / total_msgs * 100 if total_msgs > 0 else 0) for k, v in periods.items()}

    extra_metrics = {
        "max_msgs_day": (most_active_msgs[0], most_active_msgs[1]['msgs']),
        "max_hours_day": (most_active_hours[0], most_active_hours[1]['hours']),
        "time_periods": periods_pct,
        "top_days": top_days,
        "total_msgs": sum(stats.values())
    }
        
    return stats, daily_data, total_sec / 3600, extra_metrics
