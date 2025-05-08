import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="Evaluasi KPI CSV", layout="wide")
st.title("📊 Evaluasi Otomatis KPI dari File CSV")

# Upload file
uploaded_file = st.file_uploader("📥 Upload file `kpi_cleaned.csv`", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader("📋 Data KPI")
    st.dataframe(df)

    # Filter data yang lengkap dan valid
    df = df.dropna(subset=["BOBOT", "TARGET TW TERKAIT", "REALISASI TW TERKAIT", "POLARITAS", "NAMA KPI"])
    df = df.copy()
    
    # Pastikan numeric
    df["TARGET TW TERKAIT"] = pd.to_numeric(df["TARGET TW TERKAIT"], errors="coerce")
    df["REALISASI TW TERKAIT"] = pd.to_numeric(df["REALISASI TW TERKAIT"], errors="coerce")
    df["BOBOT"] = pd.to_numeric(df["BOBOT"], errors="coerce")

    # Hitung capaian berdasarkan polaritas
    def hitung_capaian(row):
        if row["POLARITAS"].strip().lower() == "positif":
            return (row["REALISASI TW TERKAIT"] / row["TARGET TW TERKAIT"]) * 100
        elif row["POLARITAS"].strip().lower() == "negatif":
            return (row["TARGET TW TERKAIT"] / row["REALISASI TW TERKAIT"]) * 100
        else:
            return 100  # default netral

    df["CAPAIAN (%)"] = df.apply(hitung_capaian, axis=1)
    df["SKOR TERTIMBANG"] = df["CAPAIAN (%)"] * df["BOBOT"] / 100

    total_skor = df["SKOR TERTIMBANG"].sum()
    total_bobot = df["BOBOT"].sum()
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

    # Pie Chart
    fig, ax = plt.subplots()
    ax.pie(df["SKOR TERTIMBANG"], labels=df["NAMA KPI"], autopct='%1.1f%%', startangle=90)
    ax.axis("equal")
    st.pyplot(fig)

    # Tampilkan detail
    st.subheader("📑 Rincian Perhitungan")
    df_result = df[["NAMA KPI", "BOBOT", "TARGET TW TERKAIT", "REALISASI TW TERKAIT", "POLARITAS", "CAPAIAN (%)", "SKOR TERTIMBANG"]]
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
        file_name="hasil_evaluasi_kpi.csv",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

