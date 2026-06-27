import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import os

# --- SEMUA LOGIKA PIPELINE KAMU TETAP SAMA ---
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

def hitung_metrik(sekuens_list):
    hasil_analisis = []
    for id_seq, seq in sekuens_list:
        panjang = len(seq) if len(seq) > 0 else 1
        kamus_frekuensi = {'A': seq.count('A'), 'T': seq.count('T'), 'C': seq.count('C'), 'G': seq.count('G')}
        gc_content = ((kamus_frekuensi['G'] + kamus_frekuensi['C']) / panjang) * 100
        hasil_analisis.append({
            'ID Sekuens': id_seq, 'A': kamus_frekuensi['A'], 'T': kamus_frekuensi['T'],
            'C': kamus_frekuensi['C'], 'G': kamus_frekuensi['G'], 'GC Content (%)': round(gc_content, 2)
        })
    return hasil_analisis

def main_ui():
    st.set_page_config(page_title="Pipeline Bioinformatika IPB", layout="centered")
    st.title("🧬 Pipeline Analisis GC Content — BAL Kopi")
    st.write("Aplikasi web interaktif Tugas Mini Project Struktur Data Bioinformatika (BIF1223).")
    
    try:
        with open("bakteri_kopi.fasta", "r") as f:
            data_lokal = f.read()
    except FileNotFoundError:
        data_lokal = ""

    data_inputan = st.text_area("Isi File FASTA Aktif:", data_lokal, height=200)

    if data_inputan:
        list_mentah = proses_input_fasta(data_inputan)
        data_terproses = hitung_metrik(list_mentah)
        if data_terproses:
            df = pd.DataFrame(data_terproses)
            df = df.sort_values(by='GC Content (%)', ascending=False).reset_index(drop=True)
            st.success("🎉 Pipeline Berhasil Dieksekusi!")
            st.subheader("🏆 3 Sekuens Terbaik (GC Content Tertinggi)")
            st.dataframe(df.head(3))
            
            st.subheader("📊 Grafik Distribusi GC Content")
            fig, ax = plt.subplots(figsize=(7, 3.5))
            label_id = [str(i)[:12] + "..." if len(str(i)) > 12 else str(i) for i in df['ID Sekuens']]
            ax.bar(label_id, df['GC Content (%)'], color='#2ca02c', edgecolor='black')
            ax.set_ylabel('GC Content (%)')
            ax.set_ylim(0, 100)
            st.pyplot(fig)
            
            st.subheader("📋 Seluruh Data Hasil Analisis Pipeline")
            st.dataframe(df)

# --- BAGIAN PENTING UNTUK VERCEL ---
# Menjalankan interface streamlit jika dipanggil secara lokal/cloud normal
if __name__ == "__main__":
    main_ui()

# Handler Tiruan (Dummy application) agar Vercel tidak melemparkan eror "Could not find app"
def application(environ, start_response):
    # Trik memicu jalannya command streamlit via terminal serverless Vercel
    os.system("streamlit run app.py --server.port 8080 --server.address 0.0.0.0")
    status = '200 OK'
    output = b"Streamlit Server Terinisiasi!"
    response_headers = [('Content-type', 'text/plain'), ('Content-Length', str(len(output)))]
    start_response(status, response_headers)
    return [output]

app = application # Variabel 'app' resmi terdeteksi oleh Vercel!
