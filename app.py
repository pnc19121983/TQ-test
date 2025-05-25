import streamlit as st
st.set_page_config(page_title="Phân tích điểm theo lớp", layout="wide")

import pandas as pd
import matplotlib.pyplot as plt
import socket
import google.generativeai as genai
import gdown
import os

# === THÔNG SỐ CẤU HÌNH ===
FILE_ID = '1fzUxf9l29TU8ZtQvjHui3cQ6slTNs2FF'
FILE_NAME = 'du_lieu_mau.xlsx'
OWNER_HOSTNAME = 'TEN_MAY_CUA_BAN'

is_owner = socket.gethostname() == OWNER_HOSTNAME

if is_owner:
    uploaded_file = st.file_uploader("📤 Tải file Excel", type=["xlsx", "xls"])
    if uploaded_file:
        with open(FILE_NAME, "wb") as f:
            f.write(uploaded_file.read())
        st.success("✅ Đã cập nhật dữ liệu thành công!")

if not os.path.exists(FILE_NAME):
    try:
        url = f"https://drive.google.com/uc?id={FILE_ID}"
        st.info("🔽 Đang tải dữ liệu từ Google Drive...")
        gdown.download(url, FILE_NAME, quiet=False)
        st.success("✅ Tải dữ liệu thành công!")
    except Exception as e:
        st.error(f"❌ Không thể tải file từ Google Drive: {e}")
        st.stop()

try:
    df = pd.read_excel(FILE_NAME)
    st.success("✅ Dữ liệu đã được đọc thành công.")
except Exception as e:
    st.error(f"❌ Lỗi khi đọc file Excel: {e}")
    st.stop()

# === TIỀN XỬ LÝ ===
df.columns = df.columns.str.strip()
score_columns = ['Toán', 'Văn', 'Anh', 'Lý', 'Hóa', 'Sinh', 'Sử', 'Địa', 'KTPL', 'Tin', 'CN (NN)', 'CN (CN)']
for col in score_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
df['Điểm TB'] = df[score_columns].mean(axis=1, skipna=True)

# === AI CẤU HÌNH ===
genai.configure(api_key="AIzaSyAWXS7wjLXSUQVWa8e9k2MD1hjrL6rEkYU")

def generate_analysis(prompt_text):
    try:
        with st.spinner("🔍 Đang phân tích và đánh giá"):
            model = genai.GenerativeModel("gemini-1.5-flash")
            default_instruction = (
                "Hãy phân tích dữ liệu dưới đây theo cấu trúc:\n"
                "- Đơn vị nào có kết quả tốt, đơn vị nào có kết quả yếu kém?\n"
                "- Nguyên nhân của chất lượng yếu kém là gì?\n"
                "- Đề xuất hướng khắc phục cho các yếu kém đó.\n\n"
            )
            full_prompt = default_instruction + str(prompt_text)
            response = model.generate_content(full_prompt)
            return response.text
    except Exception as e:
        return f"❌ Lỗi khi gọi Google AI: {e}"

# === GIAO DIỆN ===
col1, col2 = st.columns([1, 15])
with col1:
    st.image("logo.png", width=80)
with col2:
    st.markdown("## TRƯỜNG ...")
st.title("📘 Phân tích điểm thi")

st.sidebar.header("🔎 Bộ lọc dữ liệu")
school_options = ["Toàn trường"] + sorted(df['Lớp'].dropna().unique().tolist())
selected_school = st.sidebar.selectbox("Chọn phạm vi phân tích:", school_options)
df_filtered = df if selected_school == "Toàn trường" else df[df['Lớp'] == selected_school]

# === BIỂU ĐỒ: ĐIỂM TB THEO LỚP ===
st.subheader("🏫 Biểu đồ điểm trung bình theo Lớp")

avg_by_school = df_filtered.groupby("Lớp")['Điểm TB'].mean()
avg_all = df_filtered['Điểm TB'].mean()
avg_by_school["Điểm TB toàn bộ"] = avg_all
avg_by_school = avg_by_school.sort_values(ascending=False)

ranked_labels = []
rank = 1
for name in avg_by_school.index:
    if name == "Điểm TB toàn bộ":
        ranked_labels.append("Trung bình")
    else:
        ranked_labels.append(f"{rank}. {name}")
        rank += 1

colors = ['orange' if name == "Điểm TB toàn bộ" else 'skyblue' for name in avg_by_school.index]

fig1, ax1 = plt.subplots(figsize=(12, 6))
bars = ax1.bar(ranked_labels, avg_by_school.values, color=colors)

for bar in bars:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2, height + 0.2, f"{height:.2f}", ha='center', va='bottom', fontsize=9, rotation=90)

ax1.set_ylabel("Điểm trung bình")
ax1.set_title("Biểu đồ điểm trung bình theo Lớp")
ax1.set_ylim(0, 10)
plt.xticks(rotation=45, ha='right')

xtick_labels = ax1.get_xticklabels()
for label in xtick_labels:
    if label.get_text() == "Trung bình":
        label.set_color("orange")

plt.tight_layout()
st.pyplot(fig1)

if st.checkbox("📌 Đánh giá bằng AI", key="ai1"):
    st.markdown("### 🧠 Nhận định & đề xuất từ AI:")
    st.markdown(generate_analysis(f"Dữ liệu điểm trung bình các lớp: {avg_by_school.to_dict()}"))

# === PHỔ ĐIỂM MÔN ===
st.subheader("📉 Phổ điểm từng môn")
available_subjects = [col for col in score_columns if col in df.columns]
selected_subject_hist = st.selectbox("🧪 Chọn môn để xem phổ điểm:", options=available_subjects, key="hist")
bins = st.slider("🎯 Số cột trong phổ điểm:", min_value=5, max_value=30, value=30)

if selected_subject_hist:
    data = df_filtered[selected_subject_hist].dropna()
    fig_hist, ax_hist = plt.subplots(figsize=(10, 5))
    counts, bin_edges, patches = ax_hist.hist(data, bins=bins, color='steelblue', edgecolor='black')

    for count, patch in zip(counts, patches):
        bar_x = patch.get_x() + patch.get_width() / 2
        bar_height = patch.get_height()
        ax_hist.text(bar_x, bar_height + 0.5, f"{int(count)}", ha='center', va='bottom', fontsize=9)

    ax_hist.set_title(f"Phổ điểm môn {selected_subject_hist}")
    ax_hist.set_xlabel("Điểm số")
    ax_hist.set_ylabel("Số học sinh")
    ax_hist.set_xlim(0, 10)
    ax_hist.set_ylim(bottom=0)
    plt.tight_layout()
    st.pyplot(fig_hist)
    st.info(f"🔍 Có {len(data)} học sinh có điểm môn {selected_subject_hist}")

    if st.checkbox("📌 Đánh giá bằng AI", key="ai3"):
        st.markdown("### 🧠 Nhận định & đề xuất từ AI:")
        st.markdown(generate_analysis(f"Phổ điểm môn {selected_subject_hist}: {counts.tolist()}"))