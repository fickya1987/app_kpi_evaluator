import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="Evaluasi KPI per Posisi", layout="wide")
st.title("📊 Evaluasi Otomatis KPI berdasarkan Posisi Pekerja")

# Upload file CSV
uploaded_file = st.file_uploader("📥 Upload file `kpi_cleaned.csv`", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader("📋 Data KPI")
    st.dataframe(df)

    # Drop baris yang tidak lengkap
    df = df.dropna(subset=["BOBOT", "TARGET TW TERKAIT", "REALISASI TW TERKAIT", "POLARITAS", "NAMA KPI", "POSISI PEKERJA"]).copy()

    # Konversi angka
    df["TARGET TW TERKAIT"] = pd.to_numeric(df["TARGET TW TERKAIT"], errors="coerce")
    df["REALISASI TW TERKAIT"] = pd.to_numeric(df["REALISASI TW TERKAIT"], errors="coerce")
    df["BOBOT"] = pd.to_numeric(df["BOBOT"], errors="coerce")

    # Pilih posisi pekerja
    posisi_list = sorted(df["POSISI PEKERJA"].unique())
    selected_posisi = st.selectbox("👤 Pilih Posisi Pekerja", posisi_list)

    df_posisi = df[df["POSISI PEKERJA"] == selected_posisi].copy()

    # Hitung capaian berdasarkan polaritas (hindari ZeroDivisionError)
    def hitung_capaian(row):
        target = row["TARGET TW TERKAIT"]
        realisasi = row["REALISASI TW TERKAIT"]
        polaritas = str(row["POLARITAS"]).strip().lower()

        if target == 0 or (polaritas == "negatif" and realisasi == 0):
            return 0
        if polaritas == "positif":
            return (realisasi / target) * 100
        elif polaritas == "negatif":
            return (target / realisasi) * 100
        else:
            return 100  # netral

    df_posisi["CAPAIAN (%)"] = df_posisi.apply(hitung_capaian, axis=1)
    df_posisi["SKOR TERTIMBANG"] = df_posisi["CAPAIAN (%)"] * df_posisi["BOBOT"] / 100

    total_skor = df_posisi["SKOR TERTIMBANG"].sum()
    total_bobot = df_posisi["BOBOT"].sum()
    final_score = (total_skor / total_bobot) * 100 if total_bobot > 0 else 0

    # Penilaian akhir
    if final_score > 110:
        kategori = "ISTIMEWA"
    elif final_score > 105:
        kategori = "SANGAT BAIK"
    elif final_score >= 90:
        kategori = "BAIK"
    elif final_score >= 80:
        kategori = "CUKUP"
    else:
        kategori = "KURANG"

    st.subheader("📊 Hasil Evaluasi")
    st.metric("Final Skor", f"{final_score:.2f}")
    st.metric("Kategori", kategori)

    # Pie chart aman
    df_pie = df_posisi[df_posisi["SKOR TERTIMBANG"] > 0].copy()
    if not df_pie.empty:
        fig, ax = plt.subplots()
        ax.pie(df_pie["SKOR TERTIMBANG"], labels=df_pie["NAMA KPI"], autopct='%1.1f%%', startangle=90)
        ax.axis("equal")
        st.pyplot(fig)
    else:
        st.warning("⚠️ Tidak ada nilai SKOR TERTIMBANG positif untuk pie chart.")

    # Rincian hasil
    st.subheader("📑 Rincian Perhitungan")
    df_result = df_posisi[[
        "NAMA KPI", "BOBOT", "TARGET TW TERKAIT", "REALISASI TW TERKAIT", 
        "POLARITAS", "CAPAIAN (%)", "SKOR TERTIMBANG"
    ]]

    st.dataframe(df_result)

    # Unduh hasil
    output = BytesIO()
    df_result.loc[len(df_result.index)] = ["TOTAL", total_bobot, "", "", "", "", total_skor]
    df_result["FINAL SKOR"] = final_score
    df_result["KATEGORI"] = kategori

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_result.to_excel(writer, index=False, sheet_name="Evaluasi KPI")

    st.download_button(
        label="📥 Unduh Hasil Evaluasi (Excel)",
        data=output.getvalue(),
        file_name=f"hasil_evaluasi_{selected_posisi.replace(' ', '_')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


