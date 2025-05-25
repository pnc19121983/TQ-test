import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import socket
import google.generativeai as genai
import gdown
import os

# === THÔNG SỐ CẤU HÌNH ===
FILE_ID = '1fzUxf9l29TU8ZtQvjHui3cQ6slTNs2FF'  # 🔁 Google Drive file ID
FILE_NAME = 'du_lieu_mau.xlsx'
OWNER_HOSTNAME = 'TEN_MAY_CUA_BAN'  # 🛠️ Nhập đúng tên máy chủ tại đây

# === KIỂM TRA MÁY CHỦ ===
is_owner = socket.gethostname() == OWNER_HOSTNAME

# === GIAO DIỆN UPLOAD (CHỈ CHO MÁY CHỦ) ===
if is_owner:
    uploaded_file = st.file_uploader("📤 Tải file Excel", type=["xlsx", "xls"])
    if uploaded_file:
        with open(FILE_NAME, "wb") as f:
            f.write(uploaded_file.read())
        st.success("✅ Đã cập nhật dữ liệu thành công!")

# === TẢI FILE TỪ GOOGLE DRIVE NẾU CHƯA CÓ ===
if not os.path.exists(FILE_NAME):
    try:
        url = f"https://drive.google.com/uc?id={FILE_ID}"
        st.info("🔽 Đang tải dữ liệu từ Google Drive...")
        gdown.download(url, FILE_NAME, quiet=False)
        st.success("✅ Tải dữ liệu thành công!")
    except Exception as e:
        st.error(f"❌ Không thể tải file từ Google Drive: {e}")
        st.stop()

# === ĐỌC FILE EXCEL ===
try:
    df = pd.read_excel(FILE_NAME)
    st.success("✅ Dữ liệu đã được đọc thành công.")
except Exception as e:
    st.error(f"❌ Lỗi khi đọc file Excel: {e}")
    st.stop()

# === TIỀN XỬ LÝ DỮ LIỆU ===
df.columns = df.columns.str.strip()
score_columns = ['Toán', 'Văn', 'Anh', 'Lý', 'Hóa', 'Sinh', 'Sử', 'Địa', 'KTPL', 'Tin', 'CN (NN)', 'CN (CN)']
for col in score_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
df['Điểm TB'] = df[score_columns].mean(axis=1, skipna=True)

# === CẤU HÌNH AI ===
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

# === GIAO DIỆN STREAMLIT ===
st.set_page_config(page_title="Phân tích điểm theo lớp", layout="wide")
col1, col2 = st.columns([1, 15])
with col1:
    st.image("logo.png", width=80)
with col2:
    st.markdown("## TRƯỜNG ...")
st.title("📘 Phân tích điểm thi")

# === LỌC DỮ LIỆU THEO LỚP ===
st.sidebar.header("🔎 Bộ lọc dữ liệu")
school_options = ["Toàn trường"] + sorted(df['Lớp'].dropna().unique().tolist())
selected_school = st.sidebar.selectbox("Chọn phạm vi phân tích:", school_options)
df_filtered = df if selected_school == "Toàn trường" else df[df['Lớp'] == selected_school]

# === CÁC PHÂN TÍCH VÀ BIỂU ĐỒ ===
# Bạn có thể thêm lại toàn bộ các phần biểu đồ, thống kê, AI từ phiên bản app gốc tại đây.
# Vì nội dung quá dài, bạn có thể yêu cầu mình nối tiếp phần nào cụ thể (VD: phổ điểm, biểu đồ TB, đánh giá AI,...)

st.write("🎉 Dữ liệu đã sẵn sàng để phân tích. Hãy thêm biểu đồ và phần đánh giá AI như bạn muốn.")