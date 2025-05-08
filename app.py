import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="Evaluasi Kinerja KPI", layout="wide")
st.title("📊 Evaluasi Otomatis Penilaian Kinerja Individu")

st.markdown("""
Masukkan atau unggah data KPI pekerja dengan kolom **Nama KPI**, **Realisasi (%)**, dan **Bobot (%)**. 
Sistem akan menghitung skor tertimbang dan menentukan kategori kinerja:  
- >110 – 120 → **ISTIMEWA**  
- >105 – 110 → **SANGAT BAIK**  
- ≥90 – 105 → **BAIK**  
- ≥80 – <90 → **CUKUP**  
- <80 → **KURANG**
""")

# Bagian upload atau input manual
option = st.radio("📥 Pilih metode input data:", ("Input Manual", "Upload Excel"))

if option == "Upload Excel":
    uploaded_file = st.file_uploader("Unggah file Excel dengan kolom: Nama KPI, Realisasi (%), Bobot (%)", type=["xlsx"])
    if uploaded_file:
        df_input = pd.read_excel(uploaded_file)
        st.success("✅ Data berhasil dimuat dari Excel.")
    else:
        df_input = pd.DataFrame(columns=["Nama KPI", "Realisasi (%)", "Bobot (%)"])
else:
    df_input = pd.DataFrame({
        "Nama KPI": ["Efisiensi Operasional", "Customer Satisfaction", "Inovasi Proyek"],
        "Realisasi (%)": [110, 95, 80],
        "Bobot (%)": [40, 30, 30]
    })

df_input = st.data_editor(df_input, num_rows="dynamic", use_container_width=True, key="input_editor")

# Proses perhitungan
if st.button("🔍 Hitung & Evaluasi"):
    try:
        df_input["Skor Tertimbang"] = df_input["Realisasi (%)"] * df_input["Bobot (%)"] / 100
        total_skor = df_input["Skor Tertimbang"].sum()
        total_bobot = df_input["Bobot (%)"].sum()

        if total_bobot == 0:
            st.error("⚠️ Total bobot tidak boleh 0.")
        else:
            final_score = (total_skor / total_bobot) * 100

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

            st.success(f"✅ Final Skor: {final_score:.2f} | Kategori: **{kategori}**")

            st.subheader("📋 Rincian Perhitungan")
            st.dataframe(df_input)

            # Pie chart
            fig, ax = plt.subplots()
            ax.pie(df_input["Skor Tertimbang"], labels=df_input["Nama KPI"], autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            st.pyplot(fig)

            # Download Excel hasil
            output = BytesIO()
            result_df = df_input.copy()
            result_df.loc[len(result_df.index)] = ["TOTAL", "", total_bobot, total_skor]
            result_df["Final Skor"] = final_score
            result_df["Kategori"] = kategori

            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                result_df.to_excel(writer, index=False, sheet_name="Evaluasi KPI")

            st.download_button(
                label="📥 Unduh Hasil Evaluasi (Excel)",
                data=output.getvalue(),
                file_name="hasil_evaluasi_kpi.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"❌ Terjadi kesalahan: {e}")
