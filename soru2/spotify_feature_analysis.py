import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Spotify verilerini okuma
with open('StreamingHistory_music_2.json', 'r', encoding='utf-8') as f:
    spotify_data = json.load(f)
spotify_df = pd.DataFrame(spotify_data)

# Spotify tarih sütununu datetime'a çevirme
spotify_df['endTime'] = pd.to_datetime(spotify_df['endTime'])
spotify_df['date'] = pd.to_datetime(spotify_df['endTime']).dt.date

# Banka verilerini okuma
bank_df = pd.read_excel('HesapHareketleri_28.11.2024_0124383 (1).xlsx', skiprows=7)
bank_df.columns = ['Tarih', 'Saat', 'Tutar', 'Bakiye', 'Açıklama', 'Fiş No']
bank_df = bank_df[bank_df['Tarih'].str.contains(r'\d{2}\.\d{2}\.\d{4}', na=False)]

# Tarihleri aynı formata çevirme
bank_df['Tarih'] = pd.to_datetime(bank_df['Tarih'], format='%d.%m.%Y')

# Günlük dinleme istatistikleri
daily_listening = spotify_df.groupby('date').agg({
    'msPlayed': 'sum',
    'trackName': 'count'
}).reset_index()

# Günlük harcama istatistikleri
daily_spending = bank_df.groupby('Tarih')['Tutar'].sum().reset_index()

# Dinleme süresini saate çevirme
daily_listening['hours_played'] = daily_listening['msPlayed'] / (1000 * 60 * 60)

# Verileri birleştirme için tarihleri string'e çevirme
daily_spending['Tarih'] = pd.to_datetime(daily_spending['Tarih'])
daily_listening['date'] = pd.to_datetime(daily_listening['date'])

# Günlük veriler oluşturalım
date_range = pd.date_range(start=min(daily_spending['Tarih'].min(), daily_listening['date'].min()),
                          end=max(daily_spending['Tarih'].max(), daily_listening['date'].max()),
                          freq='D')
daily_df = pd.DataFrame(index=date_range)

# Harcama verilerini günlük bazda dolduralım
daily_spending = daily_spending.set_index('Tarih')['Tutar'].reindex(date_range)
daily_spending = daily_spending.fillna(0)  # Boş günleri 0 olarak doldur

# Dinleme verilerini günlük bazda dolduralım
daily_listening = daily_listening.set_index('date')['hours_played'].reindex(date_range)
daily_listening = daily_listening.fillna(method='ffill').fillna(method='bfill')  # Boş günleri doldur

# Yeni DataFrame oluştur
final_df = pd.DataFrame({
    'Tutar': daily_spending,
    'hours_played': daily_listening
})

# Görselleştirme
plt.figure(figsize=(15, 10))

# Dinleme süresi grafiği
plt.subplot(2, 1, 1)
plt.title('Günlük Müzik Dinleme Süresi ve Harcamalar')
plt.plot(final_df.index, final_df['hours_played'], 
         label='Dinleme Süresi (Saat)', color='blue', linewidth=2)
plt.ylabel('Dinleme Süresi (Saat)')
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()

# Harcama grafiği
plt.subplot(2, 1, 2)
plt.plot(final_df.index, final_df['Tutar'], 
         label='Harcama (TL)', color='red', linewidth=2)
plt.ylabel('Harcama (TL)')
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()

# İstatistiksel analizler yazdır
print("\nGünlük ortalama dinleme süresi (saat):")
print(final_df['hours_played'].mean())

print("\nGünlük ortalama harcama (TL):")
print(final_df['Tutar'].mean())

print("\nDinleme süresi ve harcama arasındaki korelasyon:")
correlation = final_df['hours_played'].corr(final_df['Tutar'])
print(f"Korelasyon katsayısı: {correlation:.2f}")

# Haftanın günlerine göre analiz
final_df['weekday'] = final_df.index.day_name()
print("\nHaftanın günlerine göre ortalama dinleme süresi (saat):")
print(final_df.groupby('weekday')['hours_played'].mean().sort_values(ascending=False))

print("\nHaftanın günlerine göre ortalama harcama (TL):")
print(final_df.groupby('weekday')['Tutar'].mean().sort_values(ascending=False))