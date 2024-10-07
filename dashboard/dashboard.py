import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
day_df = pd.read_csv('day.csv')
hour_df = pd.read_csv('hour.csv')

# Convert date column to datetime
day_df['dteday'] = pd.to_datetime(day_df['dteday']).dt.date  # Hanya tanggal tanpa jam untuk Day Data
hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])  # Tanggal tetap untuk Hour Data

# Title
st.title("Dashboard Analisis Penyewaan Sepeda")

# Sidebar - Pilihan Data
option = st.sidebar.selectbox("Pilih data yang ingin dianalisis", ("Day Data", "Hour Data"))

# Sidebar - Filter Tanggal (berbeda tergantung data)
st.sidebar.subheader("Filter Tanggal")

if option == "Day Data":
    # Untuk Day Data, pilih rentang tanggal (awal dan akhir)
    available_dates = day_df['dteday'].unique()
    start_date = st.sidebar.selectbox('Pilih Tanggal Awal', available_dates)
    end_date = st.sidebar.selectbox('Pilih Tanggal Akhir', available_dates[available_dates >= start_date])
else:
    # Untuk Hour Data, pilih hanya tanggal
    available_dates = hour_df['dteday'].dt.date.unique()  # Ambil hanya tanggal unik
    selected_date = st.sidebar.selectbox('Pilih Tanggal', available_dates)

# Filter data berdasarkan pilihan
if option == "Day Data":
    filtered_df = day_df[(day_df['dteday'] >= start_date) & (day_df['dteday'] <= end_date)]
else:
    filtered_df = hour_df[hour_df['dteday'].dt.date == selected_date]

# Display Data
if option == "Day Data":
    st.subheader(f"Data Penyewaan Harian - Dari {start_date} hingga {end_date}")
    
    # Batas tampilan untuk data harian
    num_days = (filtered_df['dteday'].nunique())
    if num_days > 10:
        st.write(filtered_df.head(10))  # Tampilkan hanya 10 hari pertama
        st.warning(f"Hanya 10 hari ditampilkan. Ada {num_days} hari yang dipilih.")
    else:
        st.write(filtered_df)  # Tampilkan semua jika <= 10 hari
elif option == "Hour Data":
    st.subheader(f"Data Penyewaan Per Jam - {selected_date}")
    st.write(filtered_df.head())

# Visualisasi Korelasi Fitur
st.subheader("Heatmap Korelasi Fitur")

if option == "Day Data":
    correlation_day = filtered_df.select_dtypes(include=['float64', 'int64']).corr()
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(correlation_day, annot=True, fmt='.2f', cmap='coolwarm', ax=ax)
    st.pyplot(fig)
elif option == "Hour Data":
    correlation_hour = filtered_df.select_dtypes(include=['float64', 'int64']).corr()
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(correlation_hour, annot=True, fmt='.2f', cmap='coolwarm', ax=ax)
    st.pyplot(fig)

# Visualisasi Pengguna Kasual vs Terdaftar
st.subheader("Rata-rata Penyewaan: Pengguna Kasual vs Terdaftar")

if option == "Day Data":
    casual_registered_avg = filtered_df[['casual', 'registered']].mean()
elif option == "Hour Data":
    casual_registered_avg = filtered_df[['casual', 'registered']].mean()

fig, ax = plt.subplots()
ax.bar(['Casual', 'Registered'], casual_registered_avg, color=['orange', 'blue'])
ax.set_xlabel('Tipe Pengguna')
ax.set_ylabel('Rata-rata Jumlah Penyewaan')
st.pyplot(fig)

# Visualisasi Berdasarkan Kondisi Cuaca
if option == "Day Data":
    st.subheader("Pengaruh Kondisi Cuaca terhadap Penyewaan Sepeda (Harian)")
    weather_rentals_day = filtered_df.groupby('weathersit')['cnt'].mean()
    
    # Plot data berdasarkan kategori yang ada
    fig, ax = plt.subplots()
    bars = ax.bar(weather_rentals_day.index, weather_rentals_day.values, color='green')
    ax.set_xlabel('Kondisi Cuaca')
    ax.set_ylabel('Rata-rata Penyewaan')

    # Menambahkan keterangan di atas setiap bar
    conditions = ['Cerah', 'Kabut', 'Hujan Ringan', 'Hujan Berat']  # Klasifikasi cuaca
    for bar, condition in zip(bars, conditions):
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, yval, f'{int(yval)}\n({condition})', 
                ha='center', va='bottom')

    st.pyplot(fig)

    # Informasikan berapa kategori cuaca yang ada jika kurang dari 3
    if len(weather_rentals_day) < 3:
        st.warning(f"Data hanya memiliki {len(weather_rentals_day)} kategori cuaca.")

elif option == "Hour Data":
    st.subheader("Pengaruh Kondisi Cuaca terhadap Penyewaan Sepeda (Per Jam)")
    weather_rentals_hour = filtered_df.groupby('weathersit')['cnt'].mean()
    if len(weather_rentals_hour) > 0:
        fig, ax = plt.subplots()
        bars = ax.bar(weather_rentals_hour.index, weather_rentals_hour.values, color='green')
        ax.set_xlabel('Kondisi Cuaca')
        ax.set_ylabel('Rata-rata Penyewaan')

        # Menambahkan keterangan di atas setiap bar
        conditions_hour = ['Kabut', 'Cerah', 'Hujan Ringan', 'Hujan Berat']  # Klasifikasi cuaca
        for bar, condition in zip(bars, conditions_hour):
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, yval, f'{int(yval)}\n({condition})', 
                    ha='center', va='bottom')

        st.pyplot(fig)
    else:
        st.warning("Data tidak memiliki kategori cuaca yang cukup.")

