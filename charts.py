import matplotlib.pyplot as plt
import numpy as np

# Цвет фона карточек из app.py
BG_COLOR = '#1e1e26' 
TEXT_COLOR = '#aaaaaa'

def setup_ax(ax):
    """Скрываем рамки и сетку для современного вида"""
    ax.set_facecolor(BG_COLOR)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(colors=TEXT_COLOR, labelsize=9, length=0)
    ax.grid(True, axis='y', alpha=0.05, color='white', linestyle='-')

def draw_line_chart(daily_data):
    plt.close('all')
    fig, ax = plt.subplots(figsize=(8, 3.5))
    fig.patch.set_facecolor(BG_COLOR)
    
    # Подготовка данных (последние 30 дней для красоты, чтобы график не был кашей)
    dates = sorted(daily_data.keys())[-30:]
    values = [daily_data[d]['hours'] for d in dates]
    labels = [d.strftime('%d.%m') for d in dates]

    ax.plot(labels, values, color='#bb86fc', lw=3, marker='o', markersize=5, markerfacecolor='#1e1e26', markeredgewidth=2)
    ax.fill_between(range(len(labels)), values, alpha=0.1, color='#bb86fc')
    
    setup_ax(ax)
    
    # Показываем только каждый 3-й лейбл на оси X, чтобы не перегружать
    if len(labels) > 10:
        ax.set_xticks(np.arange(0, len(labels), max(1, len(labels)//8)))
    
    fig.tight_layout(pad=1.0)
    return fig

def draw_pie_chart(stats):
    plt.close('all')
    fig, ax = plt.subplots(figsize=(4, 3.5))
    fig.patch.set_facecolor(BG_COLOR)
    
    # Берем топ-3 пользователей, остальных в "Другие"
    top_users = stats.most_common(3)
    labels = [u[0][:10] for u in top_users]
    sizes = [u[1] for u in top_users]
    
    colors = ['#bb86fc', '#3700b3', '#03dac6', '#cf6679']
    
    # Рисуем "бублик" (Donut chart)
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, autopct='%1.0f%%', 
        colors=colors, startangle=90, 
        textprops=dict(color="white", fontsize=10),
        wedgeprops=dict(width=0.4, edgecolor=BG_COLOR)
    )
    
    fig.tight_layout(pad=0.5)
    return fig
