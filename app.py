import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="Pipeline Bioinformatika IPB", layout="centered")

st.title("🧬 Pipeline Analisis GC Content — BAL Kopi")
st.write("Aplikasi web interaktif Tugas Mini Project Struktur Data Bioinformatika (BIF1223).")

# 1. FUNGSI MEMBACA DATA FASTA (MENYIMPAN DALAM LIST)
def proses_input_fasta(teks_data):
    sekuens_list = []
    id_sekuens = None
    basa_sekuens = []
    
    string_io = io.StringIO(teks_data)
    for baris in string_io:
        baris = baris.strip()
        if baris.startswith(">"):
            if id_sekuens:
                sekuens_list.append((id_sekuens, "".join(basa_sekuens)))
            id_sekuens = baris[1:]
            basa_sekuens = []
        else:
            basa_sekuens.append(baris.upper())
    if id_sekuens:
        sekuens_list.append((id_sekuens, "".join(basa_sekuens)))
        
    return sekuens_list

# 2. FUNGSI HITUNG METRIK (MENGGUNAKAN DICTIONARY) & GC CONTENT
def hitung_metrik(sekuens_list):
    hasil_analisis = []
    for id_seq, seq in sekuens_list:
        panjang = len(seq) if len(seq) > 0 else 1
        
        # Ketentuan: Menghitung frekuensi nukleotida menggunakan Dictionary
        kamus_frekuensi = {
            'A': seq.count('A'), 
            'T': seq.count('T'), 
            'C': seq.count('C'), 
            'G': seq.count('G')
        }
        
        # Menghitung Persentase GC Content
        gc_content = ((kamus_frekuensi['G'] + kamus_frekuensi['C']) / panjang) * 100
        
        hasil_analisis.append({
            'ID Sekuens': id_seq,
            'A': kamus_frekuensi['A'],
            'T': kamus_frekuensi['T'],
            'C': kamus_frekuensi['C'],
            'G': kamus_frekuensi['G'],
            'GC Content (%)': round(gc_content, 2)
        })
    return hasil_analisis

# INTERFACE DASHBOARD WEB
st.subheader("📥 Input Data Sekuens FASTA")

# Membaca data langsung dari file lokal bakteri_kopi.fasta
try:
    with open("bakteri_kopi.fasta", "r") as f:
        data_lokal = f.read()
except FileNotFoundError:
    data_lokal = ""

data_inputan = st.text_area("Isi File FASTA Aktif saat ini (Bisa diedit/tempel baru dari NCBI):", data_lokal, height=200)

if data_inputan:
    # Eksekusi Pipeline Struktur Data
    list_mentah = proses_input_fasta(data_inputan)
    data_terproses = hitung_metrik(list_mentah)
    
    if data_terproses:
        df = pd.DataFrame(data_terproses)
        
        # 3. MENGURUTKAN SEKUENS BERDASARKAN GC CONTENT (DESCENDING)
        df = df.sort_values(by='GC Content (%)', ascending=False).reset_index(drop=True)
        
        st.success("🎉 Pipeline Berhasil Dieksekusi!")
        
        # 4. MENAMPILKAN 3 SEKUEN TERBAIK
        st.subheader("🏆 3 Sekuens Terbaik (GC Content Tertinggi)")
        st.dataframe(df.head(3))
        
        # 5. VISUALISASI GRAFIK HASIL
        st.subheader("📊 Grafik Distribusi GC Content")
        fig, ax = plt.subplots(figsize=(7, 3.5))
        label_id = [str(i)[:12] + "..." if len(str(i)) > 12 else str(i) for i in df['ID Sekuens']]
        ax.bar(label_id, df['GC Content (%)'], color='#2ca02c', edgecolor='black')
        ax.set_ylabel('GC Content (%)')
        ax.set_xlabel('ID Sekuens')
        ax.set_ylim(0, 100)
        plt.xticks(rotation=15)
        st.tight_layout()
        st.pyplot(fig)
        
        # 6. MENULIS HASIL KE FILE CSV (Ekspor via Download Button)
        st.subheader("📋 Seluruh Data Hasil Analisis Pipeline")
        st.dataframe(df)
        
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Hasil Analisis (.CSV)",
            data=csv_data,
            file_name="hasil_analisis_pipeline.csv",
            mime="text/csv"
        )
    else:
        st.warning("Format teks FASTA tidak valid. Pastikan diawali dengan karakter '>'")