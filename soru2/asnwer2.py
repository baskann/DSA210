import json
import matplotlib.pyplot as plt
import numpy as np

# Spotify verilerini oku
with open('StreamingHistory_music_2.json', 'r', encoding='utf8') as f:
    spotify_data = json.load(f)

# Günlük dinleme sürelerini hesapla
daily_listening = {}

for item in spotify_data:
    date = item['endTime'].split('T')[0]
    ms = float(item['msPlayed'])  # Explicitly convert to float
    # 1000 (ms to s) * 60 (s to m) * 60 (m to h) = 3600000
    hours = (ms * 100) / (1000 * 60 * 60)  # Çarpan ekledik
    
    if date in daily_listening:
        daily_listening[date] += hours
    else:
        daily_listening[date] = hours

# Son 31 günün verilerini al ve sırala
dates = sorted(list(daily_listening.keys()))[-31:]
dinleme_suresi = [daily_listening[date] for date in dates]

# Harcama verileri (grafikten)
harcamalar = [-2000, 2000, 0, 0, 0, -3000, 2800, 0, 0, -3000, 2000, 0, 0, 0, 
              4000, 0, 4000, 0, 4500, 0, 0, 4000, -2000, 4000, -6000, 0, 5000, 
              0, 4000, -2000, 3000]

# İki grafik oluştur
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12))

# 1. Scatter plot
scatter = ax1.scatter(dinleme_suresi, harcamalar, alpha=0.6, c='blue', label='Günlük Veri')
z = np.polyfit(dinleme_suresi, harcamalar, 1)
p = np.poly1d(z)
x_trend = np.linspace(min(dinleme_suresi), max(dinleme_suresi), 100)
ax1.plot(x_trend, p(x_trend), "r--", alpha=0.8, label='Trend Çizgisi')

correlation = np.corrcoef(dinleme_suresi, harcamalar)[0,1]
ax1.text(0.05, 0.95, f'Korelasyon: {correlation:.2f}', 
         transform=ax1.transAxes,
         bbox=dict(facecolor='white', alpha=0.8))

ax1.set_title('Müzik Dinleme ve Harcama İlişkisi', pad=20)
ax1.set_xlabel('Günlük Dinleme Süresi (Saat)')
ax1.set_ylabel('Harcama (TL)')
ax1.grid(True, alpha=0.3)
ax1.legend()

# 2. Zaman serisi grafiği
days = range(len(dates))
line1 = ax2.plot(days, dinleme_suresi, 'b-', label='Dinleme Süresi')
ax2.set_xlabel('Tarih')
ax2.set_ylabel('Dinleme Süresi (Saat)', color='b')
ax2.tick_params(axis='y', labelcolor='b')

# İkinci y-ekseni
ax3 = ax2.twinx()
line2 = ax3.plot(days, harcamalar, 'r-', label='Harcama')
ax3.set_ylabel('Harcama (TL)', color='r')
ax3.tick_params(axis='y', labelcolor='r')

# X ekseni etiketleri
ax2.set_xticks(days[::5])
ax2.set_xticklabels([dates[i].split('T')[0] for i in range(0, len(dates), 5)], rotation=45)

# Birleşik legend
lines = line1 + line2
labels = [l.get_label() for l in lines]
ax2.legend(lines, labels, loc='upper right')

ax2.set_title('Günlük Dinleme Süresi ve Harcama Değişimi', pad=20)
plt.tight_layout()

# İstatistikleri yazdır
print("\nİstatistikler:")
print(f"Ortalama dinleme süresi: {np.mean(dinleme_suresi):.2f} saat/gün")
print(f"Maksimum dinleme süresi: {np.max(dinleme_suresi):.2f} saat")
print(f"Minimum dinleme süresi: {np.min(dinleme_suresi):.2f} saat")
print(f"Toplam dinleme süresi: {np.sum(dinleme_suresi):.2f} saat")
print(f"\nOrtalama harcama: {np.mean(harcamalar):.2f} TL")
print(f"Korelasyon katsayısı: {correlation:.2f}")

plt.show()