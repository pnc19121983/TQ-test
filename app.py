
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
