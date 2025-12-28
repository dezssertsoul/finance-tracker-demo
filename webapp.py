import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
from datetime import datetime

# 1. KONFIGURASI HALAMAN (Wajib di baris pertama)
st.set_page_config(page_title="Keuanganku", page_icon="💰", layout="centered")

# Nama File Database
nama_file = 'keuanganku.xlsx'

# --- FUNGSI PENDUKUNG ---
def load_data():
    """Membaca data dari Excel"""
    if not os.path.exists(nama_file):
        return pd.DataFrame(columns=['Tanggal', 'Kategori', 'Tipe', 'Nominal', 'Keterangan'])
    try:
        return pd.read_excel(nama_file)
    except Exception as e:
        st.error(f"Error membaca file: {e}")
        return pd.DataFrame()

def save_data(df):
    """Menyimpan data ke Excel"""
    try:
        df.to_excel(nama_file, index=False)
    except Exception as e:
        st.error(f"Gagal menyimpan: {e}. Tutup file Excelnya dulu!")

# --- UI UTAMA (SIDEBAR) ---
st.sidebar.title("📱 Menu Aplikasi")
menu = st.sidebar.radio("Pilih Menu:", ["Dashboard & Laporan", "Input Transaksi", "Analisis Grafik"])

# --- MENU 1: DASHBOARD ---
if menu == "Dashboard & Laporan":
    st.title("💰 Laporan Keuangan")
    st.markdown("Rekap saldo dan riwayat transaksi kamu.")
    
    df = load_data()
    
    # Hitung Saldo Real-time
    if not df.empty:
        total_masuk = df[df['Tipe'] == 'Pemasukan']['Nominal'].sum()
        total_keluar = df[df['Tipe'] == 'Pengeluaran']['Nominal'].sum()
        saldo = total_masuk - total_keluar
        
        # Tampilkan dalam kotak metrics cantik
        col1, col2, col3 = st.columns(3)
        col1.metric("Pemasukan", f"Rp {total_masuk:,.0f}")
        col2.metric("Pengeluaran", f"Rp {total_keluar:,.0f}")
        col3.metric("Sisa Saldo", f"Rp {saldo:,.0f}")
        
        st.divider() # Garis pemisah
        
        # Tampilkan Tabel Data
        st.subheader("Riwayat Transaksi")
        # Mengurutkan dari yang terbaru
        st.dataframe(df.sort_index(ascending=False), use_container_width=True)
    else:
        st.info("Belum ada data transaksi. Yuk input dulu!")

# --- MENU 2: INPUT TRANSAKSI ---
elif menu == "Input Transaksi":
    st.title("➕ Tambah Transaksi")
    
    with st.form("form_input"):
        tanggal = st.date_input("Tanggal", datetime.now())
        tipe = st.selectbox("Tipe Transaksi", ["Pengeluaran", "Pemasukan"])
        
        # Pilihan kategori dinamis berdasarkan tipe
        if tipe == "Pengeluaran":
            list_kategori = ["Makan", "Transport", "Belanja", "Tagihan", "Hiburan", "Lainnya"]
        else:
            list_kategori = ["Gaji", "Bonus", "Freelance", "Lainnya"]
            
        kategori = st.selectbox("Kategori", list_kategori)
        nominal = st.number_input("Nominal (Rp)", min_value=0, step=1000)
        keterangan = st.text_input("Keterangan (Opsional)")
        
        submit = st.form_submit_button("Simpan Data")
        
        if submit:
            df_lama = load_data()
            
            data_baru = {
                'Tanggal': [tanggal],
                'Kategori': [kategori],
                'Tipe': [tipe],
                'Nominal': [nominal],
                'Keterangan': [keterangan]
            }
            df_baru = pd.DataFrame(data_baru)
            df_update = pd.concat([df_lama, df_baru], ignore_index=True)
            
            save_data(df_update)
            st.success(f"Berhasil menyimpan {kategori} sebesar Rp {nominal:,.0f}!")
            st.balloons() # Efek animasi balon

# --- MENU 3: ANALISIS GRAFIK ---
elif menu == "Analisis Grafik":
    st.title("📊 Analisis Pengeluaran")
    
    df = load_data()
    df_pengeluaran = df[df['Tipe'] == 'Pengeluaran']
    
    if df_pengeluaran.empty:
        st.warning("Belum ada data pengeluaran untuk dianalsis.")
    else:
        # Pie Chart Logic
        st.subheader("Persentase Pengeluaran")
        
        # Grouping data
        data_pie = df_pengeluaran.groupby('Kategori')['Nominal'].sum()
        
        # Membuat Plot dengan Matplotlib
        fig, ax = plt.subplots()
        ax.pie(data_pie, labels=data_pie.index, autopct='%1.1f%%', startangle=90)
        ax.axis('equal') 
        
        # Tampilkan di Streamlit
        st.pyplot(fig)
        
        # Insight Teks
        terboros = data_pie.idxmax()
        nilai_terboros = data_pie.max()
        st.error(f"⚠️ Warning: Kamu paling boros di kategori **{terboros}** (Total: Rp {nilai_terboros:,.0f})")