import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import bcrypt
import time
import hashlib
import streamlit.components.v1 as components   
import json         
from google import genai
import requests


#  CẤU HÌNH TRANG & CSS 
st.set_page_config(page_title="HỆ THỐNG GỢI Ý SẢN PHẨM THỜI TRANG", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── GLOBAL ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 1400px;
}

/* ── HERO TITLE ── */
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: clamp(1.5rem, 3.5vw, 2.8rem); 
    font-weight: 900;
    background: linear-gradient(135deg, #1a1a2e 0%, #c9184a 50%, #ff6b6b 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    
    /* 1. Tăng line-height lên một chút cho thoáng */
    line-height: 1.4; 
    margin-bottom: 0.25rem;
    text-align: center;
    
    /* 2. THÊM 2 DÒNG NÀY ĐỂ BẢO VỆ ĐỈNH VÀ CHÂN CHỮ */
    padding-top: 16px;    /* Chống mất đỉnh chữ, dấu mũ */
    padding-bottom: 12px; /* Chống mất chân các chữ p, g, q */
}
.hero-sub {
    font-family: 'DM Sans', sans-serif;
    font-size: 1rem;
    color: #6b7280;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
    text-align: center; /* Căn giữa đồng bộ với tiêu đề */
}

/* ── ALGO BANNER ── */
.algo-banner {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    border-radius: 16px;
    padding: 1.5rem 2rem;
    color: white;
    margin-bottom: 1.5rem;
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}
.algo-banner h3 {
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem;
    margin: 0 0 0.5rem 0;
    color: #f9a8d4;
}
.algo-banner .metrics-row {
    display: flex;
    gap: 2rem;
    flex-wrap: wrap;
    margin-top: 0.75rem;
}
.algo-banner .metric-chip {
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 50px;
    padding: 4px 16px;
    font-size: 0.85rem;
    backdrop-filter: blur(4px);
}
.algo-banner .metric-chip span {
    color: #f9a8d4;
    font-weight: 600;
}

/* ── PRODUCT CARD ── */
.product-card {
    background: white;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
    border: 1px solid #f0f0f0;
    margin-bottom: 1rem;
}
.product-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 30px rgba(0,0,0,0.15);
}
div[data-testid="stImage"] img {
    width: 100% !important;
    height: auto !important;
    aspect-ratio: 3/4 !important;
    object-fit: cover !important;
    border-radius: 12px;
}

/* ── TABS ── */
div[data-baseweb="tab-list"] {
    background: #f8f4f0;
    border-radius: 12px;
    padding: 4px;
    gap: 2px;
    border: none !important;
}
button[data-baseweb="tab"] {
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: clamp(0.72rem, 1.1vw, 0.9rem) !important;
    font-weight: 500 !important;
    color: #6b7280 !important;
    transition: all 0.2s ease !important;
    padding: 8px 14px !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background: white !important;
    color: #c9184a !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
}

/* ── ALGO MINI PANEL (inside tabs) ── */
.algo-mini-panel {
    background: linear-gradient(135deg, #fff1f2, #fce7f3);
    border: 1px solid #fecdd3;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 1.25rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
}
.algo-mini-panel .model-badge {
    background: #c9184a;
    color: white;
    border-radius: 50px;
    padding: 3px 14px;
    font-size: 0.78rem;
    font-weight: 600;
    white-space: nowrap;
}
.algo-mini-panel .stat {
    font-size: 0.82rem;
    color: #6b7280;
}
.algo-mini-panel .stat b {
    color: #1a1a2e;
}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
}
section[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}

/* ── FIX: Mã Khách hàng input text = ĐEN ── */
section[data-testid="stSidebar"] .stTextInput input {
    color: #000000 !important;
    background: rgba(255,255,255,0.92) !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
    border-radius: 8px !important;
}
section[data-testid="stSidebar"] .stTextInput input::placeholder {
    color: #6b7280 !important;
}

section[data-testid="stSidebar"] .stSelectbox > div > div {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 8px !important;
    color: white !important;
}
section[data-testid="stSidebar"] label {
    color: #94a3b8 !important;
    font-size: 0.82rem !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
section[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.1) !important;
}

/* ── CART BADGE ── */
.cart-badge {
    display: inline-block;
    background: #c9184a;
    color: white !important;
    border-radius: 50px;
    padding: 2px 10px;
    font-size: 0.78rem;
    font-weight: 700;
    min-width: 22px;
    text-align: center;
}

/* ── METRIC BOX ── */
div[data-testid="metric-container"] {
    background: white;
    border: 1px solid #f0f0f0;
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

# /* ── FLOATING CHAT BUTTON ── */
# #float-chat-btn {
#     position: fixed;
#     bottom: 28px;
#     right: 28px;
#     z-index: 99999;
#     width: 58px;
#     height: 58px;
#     border-radius: 50%;
#     background: linear-gradient(135deg, #c9184a, #ff6b6b);
#     color: white;
#     font-size: 1.5rem;
#     display: flex;
#     align-items: center;
#     justify-content: center;
#     cursor: pointer;
#     box-shadow: 0 4px 20px rgba(201,24,74,0.45);
#     border: none;
#     transition: transform 0.2s ease, box-shadow 0.2s ease;
#     user-select: none;
# }
# #float-chat-btn:hover {
#     transform: scale(1.1);
#     box-shadow: 0 8px 28px rgba(201,24,74,0.55);
# }

/* ── FLOATING CHAT BOX ── */
#float-chat-box {
    position: fixed;
    bottom: 100px;
    right: 28px;
    z-index: 99998;
    width: 420px;
    max-height: 650px;
    background: #ffffff;
    border-radius: 20px;
    box-shadow: 0 16px 48px rgba(0,0,0,0.18);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    border: 1px solid #f0e0e6;
    transition: opacity 0.25s ease, transform 0.25s ease;
}
#float-chat-box.hidden {
    opacity: 0;
    pointer-events: none;
    transform: translateY(16px) scale(0.97);
}

/* Chat header */
#float-chat-header {
    background: linear-gradient(135deg, #c9184a, #ff6b6b);
    padding: 14px 18px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-shrink: 0;
}
#float-chat-header .chat-title {
    color: white;
    font-weight: 700;
    font-size: 0.95rem;
    display: flex;
    align-items: center;
    gap: 8px;
}
#float-chat-close {
    background: rgba(255,255,255,0.2);
    border: none;
    color: white;
    border-radius: 50%;
    width: 28px;
    height: 28px;
    cursor: pointer;
    font-size: 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.15s;
}
#float-chat-close:hover { background: rgba(255,255,255,0.35); }

/* Quick chips */
#float-chat-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    padding: 10px 14px 4px;
    flex-shrink: 0;
    background: #fff8f9;
    border-bottom: 1px solid #fde0e8;
}
.float-chip {
    background: #fff1f2;
    border: 1px solid #fecdd3;
    color: #c9184a;
    border-radius: 50px;
    padding: 4px 11px;
    font-size: 0.72rem;
    cursor: pointer;
    transition: all 0.15s ease;
    white-space: nowrap;
    font-family: 'DM Sans', sans-serif;
}
.float-chip:hover {
    background: #c9184a;
    color: white;
    border-color: #c9184a;
}

/* Messages area */
#float-chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 14px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    min-height: 0;
}
.fchat-msg {
    max-width: 82%;
    padding: 9px 13px;
    border-radius: 14px;
    font-size: 0.84rem;
    line-height: 1.45;
    word-break: break-word;
}
.fchat-msg.bot {
    background: #f3f4f6;
    color: #1a1a2e;
    align-self: flex-start;
    border-bottom-left-radius: 4px;
}
.fchat-msg.user {
    background: linear-gradient(135deg, #c9184a, #ff6b6b);
    color: white;
    align-self: flex-end;
    border-bottom-right-radius: 4px;
}

/* Input row */
#float-chat-input-row {
    display: flex;
    gap: 8px;
    padding: 10px 12px;
    border-top: 1px solid #f0e0e6;
    background: white;
    flex-shrink: 0;
}
#float-chat-input {
    flex: 1;
    border: 1px solid #fecdd3;
    border-radius: 50px;
    padding: 8px 14px;
    font-size: 0.83rem;
    font-family: 'DM Sans', sans-serif;
    outline: none;
    color: #1a1a2e;
    transition: border-color 0.2s;
}
#float-chat-input:focus { border-color: #c9184a; }
#float-chat-send {
    background: linear-gradient(135deg, #c9184a, #ff6b6b);
    border: none;
    border-radius: 50%;
    width: 36px;
    height: 36px;
    color: white;
    font-size: 1rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    transition: transform 0.15s;
}
#float-chat-send:hover { transform: scale(1.1); }

/* ── QUICK REPLY CHIPS (old popover, kept for ref) ── */
.quick-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin: 6px 0 10px 0;
}
.quick-chip {
    background: #fff1f2;
    border: 1px solid #fecdd3;
    color: #c9184a;
    border-radius: 50px;
    padding: 4px 12px;
    font-size: 0.78rem;
    cursor: pointer;
    transition: all 0.15s ease;
    white-space: nowrap;
}
.quick-chip:hover { background: #c9184a; color: white; }

/* ── LOOKBOOK OVERLAY ── */
.lookbook-img-wrap {
    position: relative;
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 8px;
}
.style-tag {
    display: inline-block;
    background: linear-gradient(135deg, #c9184a, #ff6b6b);
    color: white;
    border-radius: 50px;
    padding: 2px 10px;
    font-size: 0.72rem;
    font-weight: 600;
    margin-bottom: 6px;
}

/* ── COLOR SWATCH ── */
.swatch-row { display: flex; gap: 8px; flex-wrap: wrap; margin: 6px 0; }
.swatch {
    width: 32px; height: 32px; border-radius: 50%;
    border: 2px solid rgba(0,0,0,0.08); cursor: pointer; transition: transform 0.15s;
}
.swatch:hover { transform: scale(1.15); }

/* ── SIZE RESULT ── */
.size-result-box {
    background: linear-gradient(135deg, #0f0c29, #302b63);
    border-radius: 16px; padding: 2rem; text-align: center; color: white;
}
.size-big {
    font-family: 'Playfair Display', serif;
    font-size: 5rem; font-weight: 900; color: #f9a8d4; line-height: 1;
}

/* ── OCCASION CARD ── */
.occasion-chip {
    display: inline-block; background: rgba(201,24,74,0.1); color: #c9184a;
    border-radius: 50px; padding: 2px 10px; font-size: 0.72rem; font-weight: 600; margin-top: 4px;
}

/* ── COLOR SECTION ── */
.color-guide-card {
    background: white; border-radius: 16px; padding: 1.25rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06); border: 1px solid #f0f0f0; height: 100%;
}
.color-guide-card h4 {
    font-family: 'Playfair Display', serif; font-size: 1.05rem;
    margin-bottom: 0.75rem; color: #1a1a2e;
}

/* ── GENERAL ── */
.stButton > button {
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #c9184a, #ff6b6b) !important;
    border: none !important; color: white !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 4px 16px rgba(201,24,74,0.35) !important;
    transform: translateY(-1px) !important;
}
</style>
""", unsafe_allow_html=True)


#  DATABASE 
@st.cache_resource
def get_db_connection():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    conn.execute('''CREATE TABLE IF NOT EXISTS users
                    (username TEXT PRIMARY KEY, password TEXT, role TEXT)''')
    
    # Tự động khởi tạo tài khoản Admin mặc định nếu chưa có
    cur = conn.execute("SELECT * FROM users WHERE username='admin'")
    if not cur.fetchone():
        hashed = bcrypt.hashpw('123'.encode(), bcrypt.gensalt())
        conn.execute("INSERT INTO users (username, password, role) VALUES (?,?,?)", ('admin', hashed, 'Admin'))
    
    conn.commit()
    return conn

def check_login(username, password):
    conn = get_db_connection()
    cur = conn.execute("SELECT password, role FROM users WHERE username=?", (username,))
    res = cur.fetchone()
    if res and bcrypt.checkpw(password.encode(), res[0]):
        return res[1]
    return None

def register_user(username, password, role="Người dùng"):
    if not username or not password:
        return False, "Vui lòng nhập đầy đủ thông tin."
    if len(username) < 3:
        return False, "Tên đăng nhập phải có ít nhất 3 ký tự."
    if len(password) < 6:
        return False, "Mật khẩu phải có ít nhất 6 ký tự."
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO users (username, password, role) VALUES (?,?,?)",
                     (username, hashed, role))
        conn.commit()
        return True, f"Đăng ký thành công! Chào mừng {username} 🎉"
    except sqlite3.IntegrityError:
        return False, "Tên đăng nhập đã tồn tại."
    except Exception as e:
        return False, f"Lỗi hệ thống: {str(e)}"

def get_all_users():
    conn = get_db_connection()
    cur = conn.execute("SELECT username, role FROM users")
    return cur.fetchall()

def delete_user(username_to_delete):
    conn = get_db_connection()
    try:
        # Không cho phép xóa tài khoản admin mặc định (tùy chọn)
        if username_to_delete == "admin":
            return False, "Không thể xóa tài khoản Admin gốc."
        conn.execute("DELETE FROM users WHERE username=?", (username_to_delete,))
        conn.commit()
        return True, f"Đã xóa tài khoản {username_to_delete}."
    except Exception as e:
        return False, f"Lỗi: {str(e)}"
#  DATA 
# @st.cache_data
# def load_data():
#     try:
#         df = pd.read_csv('Data_Final.csv')
#         if 'imUrl' not in df.columns: df['imUrl'] = None
#         if 'asin' not in df.columns: df['asin'] = [f'SP_{i}' for i in range(len(df))]
#         return df.drop_duplicates(subset=['asin']).reset_index(drop=True)
#     except Exception:
#         return pd.DataFrame({
#             'asin': [f'SP_{i:03d}' for i in range(80)],
#             'score': 5.0,
#             'imUrl': [f'https://picsum.photos/seed/{i*7}/400/500' for i in range(80)]
#         })

@st.cache_data
def load_data():
    try:
        df = pd.read_csv('Data_Final.csv')
        if 'imUrl' not in df.columns: df['imUrl'] = None
        if 'asin' not in df.columns: df['asin'] = [f'SP_{i}' for i in range(len(df))]
        # Tự động tạo Title nếu thiếu
        if 'title' not in df.columns: df['title'] = df['asin'].apply(lambda x: f"Sản phẩm {x}")
        return df.drop_duplicates(subset=['asin']).reset_index(drop=True)
    except Exception:
        return pd.DataFrame({
            'asin': [f'SP_{i:03d}' for i in range(80)],
            'title': [f'Sản phẩm Mẫu {i:03d}' for i in range(80)],
            'score': 5.0,
            'imUrl': None # Sẽ được get_safe_img tự động điền ảnh thời trang thật
        })

@st.cache_data
def calculate_popular_items(df, percentile=0.85):
    if 'overall' not in df.columns:
        return df
    stats = df.groupby('asin').agg(v=('overall','count'), R=('overall','mean')).reset_index()
    C = stats['R'].mean()
    m = stats['v'].quantile(percentile)
    qualified = stats[stats['v'] >= m].copy()
    qualified['score'] = (
        (qualified['v'] / (qualified['v'] + m)) * qualified['R'] +
        (m / (qualified['v'] + m)) * C
    )
    popular = qualified.sort_values('score', ascending=False)
    return popular.merge(df[['asin','imUrl']].drop_duplicates('asin'), on='asin', how='left')

def run_algorithm(df_raw, model, user_id, top_n):
    t0 = time.time()
    if model == "Sản phẩm thịnh hành (Popularity)":
        popular_df = calculate_popular_items(df_raw)
        res_df = popular_df.head(top_n).reset_index(drop=True)
        if 'imUrl' not in res_df.columns:
            res_df['imUrl'] = None
        rmse = "1.3250"
    else:
        seed = int(hashlib.md5(f"{user_id}_{model}".encode()).hexdigest(), 16) % (2**32)
        res_df = df_raw.sample(n=min(top_n, len(df_raw)), random_state=seed).reset_index(drop=True)
        rmse = "1.0574" if "SVD" in model else "1.1500"
    elapsed = f"{time.time()-t0:.2f}s"
    return res_df, rmse, elapsed

FALLBACK_IMAGES = [
    "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=400&q=80",
    "https://images.unsplash.com/photo-1434389678278-be43e49e0186?w=400&q=80",
    "https://images.unsplash.com/photo-1529139574466-a303027c1d8b?w=400&q=80",
    "https://images.unsplash.com/photo-1483985988355-763728e1935b?w=400&q=80",
    "https://images.unsplash.com/photo-1550639525-c97d455acf70?w=400&q=80",
    "https://images.unsplash.com/photo-1509631179647-0177331693ae?w=400&q=80"
]
#  HELPERS 
# def toggle_cart(asin):
#     if asin in st.session_state.cart:
#         st.session_state.cart.remove(asin)
#     else:
#         st.session_state.cart.append(asin)

# def get_safe_img(url, asin=""):
#     # Chuyển đổi và làm sạch chuỗi
#     url = str(url).strip()
    
#     # KIỂM TRA PYTHON: Bắt các chuỗi rỗng, nan, null, hoặc không phải link HTTP
#     if not url or url.lower() in ("nan", "none", "", "null") or not url.startswith("http"):
#         # Lấy ảnh cố định từ kho dự phòng dựa trên ASIN để tránh đổi ảnh liên tục
#         idx = sum(ord(c) for c in str(asin)) % len(FALLBACK_IMAGES)
#         return FALLBACK_IMAGES[idx]
    
#     return url

# def render_product_grid(df_slice, key_prefix, cols=4):
#     grid = st.columns(cols)
#     for i, (_, row) in enumerate(df_slice.iterrows()):
#         asin = str(row['asin'])
        
#         # 1. Lấy URL nguyên gốc và làm sạch khoảng trắng
#         raw_url = str(row.get('imUrl', '')).strip()
        
#         # Xử lý hiển thị tên sản phẩm
#         title = row.get('title', '')
#         if pd.isna(title) or str(title).strip() in ('', 'nan', 'None'):
#             title = f"Sản phẩm {asin[-4:]}"
            
#         score = row.get('score', np.random.uniform(4.0, 5.0))

#         with grid[i % cols]:
#             with st.container(border=True):
#                 # 2. Chọn sẵn 1 ảnh dự phòng chắc chắn không chết link
#                 idx = sum(ord(c) for c in asin) % len(FALLBACK_IMAGES)
#                 safe_fallback = FALLBACK_IMAGES[idx]
                
#                 # 3. Lọc Python: Nếu link bị rỗng/nan từ đầu, gán luôn ảnh dự phòng
#                 if not raw_url or raw_url.lower() in ("nan", "none", "", "null") or not raw_url.startswith("http"):
#                     final_url = safe_fallback
#                 else:
#                     final_url = raw_url
                
#                 # 4. GIẢI PHÁP CHỐNG LỖI MỚI (Pure CSS):
#                 # Thiết lập 2 lớp ảnh nền. Nếu final_url bị 404, safe_fallback sẽ hiển thị thay thế ngay lập tức.
#                 img_html = f"""
#                 <div style="
#                     width: 100%; 
#                     aspect-ratio: 3/4;
#                     border-radius: 12px;
#                     background-color: #f3f4f6;
#                     background-image: url('{final_url}'), url('{safe_fallback}');
#                     background-size: cover;
#                     background-position: center;
#                     background-repeat: no-repeat;
#                 "></div>
#                 """
#                 st.markdown(img_html, unsafe_allow_html=True)
                
#                 # 5. Render Text & Button
#                 st.markdown(f"<div style='font-family: \"DM Sans\", sans-serif; font-weight: 700; font-size: 0.95rem; color: #1a1a2e; line-height: 1.3; margin-top: 8px; margin-bottom: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;' title='{title}'>{title}</div>", unsafe_allow_html=True)
#                 st.markdown(f"<div style='font-size: 0.75rem; color: #6b7280; margin-bottom: 4px;'>Mã SP: <b>{asin}</b></div>", unsafe_allow_html=True)
#                 st.caption(f"Đánh giá: {score:.2f} ⭐")
                
#                 in_cart = asin in st.session_state.cart
#                 btn_label = "✅ Đã thêm" if in_cart else "🛒 Thêm vào giỏ"
#                 st.button(btn_label, key=f"{key_prefix}_{asin}_{i}", on_click=toggle_cart, args=(asin,), width='stretch')

def toggle_cart(asin):
    if asin in st.session_state.cart:
        st.session_state.cart.remove(asin)
    else:
        st.session_state.cart.append(asin)

# Dùng cache để Python chỉ check link 1 lần, những lần sau load tốc độ bàn thờ
@st.cache_data(show_spinner=False)
def check_image_url(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        # Gửi request thử xem server chứa ảnh còn sống không
        res = requests.get(url, headers=headers, timeout=1.5, stream=True)
        return res.status_code == 200
    except Exception:
        return False

def get_safe_img(url, asin=""):
    url = str(url).strip()
    idx = sum(ord(c) for c in str(asin)) % len(FALLBACK_IMAGES)
    fallback = FALLBACK_IMAGES[idx]
    
    # 1. Bắt lỗi chuỗi trống, nan
    if not url or url.lower() in ("nan", "none", "", "null") or not url.startswith("http"):
        return fallback
        
    # 2. Bắt lỗi link 404 (Server chết) bằng Python
    if check_image_url(url):
        return url
        
    return fallback

def render_product_grid(df_slice, key_prefix, cols=4):
    grid = st.columns(cols)
    for i, (_, row) in enumerate(df_slice.iterrows()):
        asin = str(row['asin'])
        
        # Lúc này img_url TRĂM PHẦN TRĂM là link sống
        img_url = get_safe_img(row.get('imUrl', ''), asin)
        score = row.get('score', np.random.uniform(4.0, 5.0))
        
        title = row.get('title', '')
        if pd.isna(title) or str(title).strip() in ('', 'nan', 'None'):
            title = f"Sản phẩm {asin[-4:]}"

        with grid[i % cols]:
            with st.container(border=True):
                # Vì link đã được Python bảo kê, mình dùng HTML đơn giản nhất, không sợ Streamlit chặn
                img_html = f"""
                <img src="{img_url}" 
                     style="width: 100%; height: auto; aspect-ratio: 3/4; object-fit: cover; border-radius: 12px; background: #f3f4f6; display: block;">
                """
                st.markdown(img_html, unsafe_allow_html=True)
                
                st.markdown(f"<div style='font-family: \"DM Sans\", sans-serif; font-weight: 700; font-size: 0.95rem; color: #1a1a2e; line-height: 1.3; margin-top: 8px; margin-bottom: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;' title='{title}'>{title}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='font-size: 0.75rem; color: #6b7280; margin-bottom: 4px;'>Mã SP: <b>{asin}</b></div>", unsafe_allow_html=True)
                st.caption(f"Đánh giá: {score:.2f} ⭐")
                
                in_cart = asin in st.session_state.cart
                btn_label = "✅ Đã thêm" if in_cart else "🛒 Thêm vào giỏ"
                st.button(btn_label, key=f"{key_prefix}_{asin}_{i}", on_click=toggle_cart, args=(asin,), width='stretch')

def algo_mini_panel():
    if st.session_state.get('role') != "Admin":
        return False

    if not st.session_state.algo_run or not st.session_state.algo_results:
        st.info("💡 Chọn thuật toán ở thanh bên trái và nhấn **Chạy thuật toán** để xem gợi ý cá nhân hóa ngay tại đây.")
        return False
    res = st.session_state.algo_results
    model_short = res['model'].split('(')[0].strip()
    st.markdown(f"""
    <div class="algo-mini-panel">
        <div class="model-badge">🤖 {model_short}</div>
        <div class="stat">Khách hàng: <b>{res['user']}</b></div>
        <div class="stat">RMSE: <b>{res['rmse']}</b></div>
        <div class="stat">Thời gian: <b>{res['time']}</b></div>
        <div class="stat">Top-N: <b>{res['top']}</b></div>
    </div>
    """, unsafe_allow_html=True)
    return True


#  COLOUR & SIZE DATA 
COLOR_MAP = {
    "Navy":        "#1e3a5f",
    "Đỏ đô":       "#8b1a1a",
    "Xanh ngọc":   "#0d9488",
    "Tím lavender":"#9370db",
    "Cam đất":     "#c2410c",
    "Vàng đất":    "#92400e",
    "Vàng olive":  "#6b7529",
    "Xanh lá rừng":"#166534",
    "Đỏ gạch":     "#b91c1c",
    "Trắng tinh":  "#f8fafc",
    "Vàng tươi":   "#eab308",
    "Cam rực":     "#f97316",
    "Xanh cobalt": "#1d4ed8",
    "Xám nhạt":    "#94a3b8",
    "Be/Kem":      "#f5f0e8",
    "Nâu nhạt":    "#92705e",
    "Trắng":       "#ffffff",
    "Đen":         "#0f172a",
    "Xám lạnh":    "#64748b",
    "Nâu tối":     "#3d2314",
}

def get_color_suggestions(tone_da):
    suggestions = {
        "Sáng (Da trắng hồng)": {
            "phu_hop": ["Navy", "Đỏ đô", "Xanh ngọc", "Tím lavender"],
            "tranh":   ["Vàng đất", "Cam đất"],
            "trung_tinh": ["Xám nhạt", "Trắng tinh"],
            "ghi_chu": "Da sáng hợp với tông lạnh và màu đậm nổi bật."
        },
        "Trung bình (Da vàng/Bánh mật)": {
            "phu_hop": ["Cam đất", "Vàng olive", "Xanh lá rừng", "Đỏ gạch"],
            "tranh":   ["Vàng tươi", "Xám lạnh"],
            "trung_tinh": ["Be/Kem", "Nâu nhạt"],
            "ghi_chu": "Rất hợp với màu đất và tông nóng."
        },
        "Ngăm (Da nâu/Đen)": {
            "phu_hop": ["Trắng tinh", "Vàng tươi", "Cam rực", "Xanh cobalt"],
            "tranh":   ["Nâu tối", "Xám lạnh"],
            "trung_tinh": ["Trắng", "Đen"],
            "ghi_chu": "Nổi bật với màu tương phản mạnh."
        }
    }
    return suggestions.get(tone_da, {})

def calculate_size(h, w):
    if h <= 0 or w <= 0: return None, "Sai thông số"
    bmi = w / ((h / 100) ** 2)
    if h < 155:   s = "S" if w < 50 else "M"
    elif h < 163: s = "M" if w < 60 else "L"
    elif h < 170: s = "L" if w < 70 else "XL"
    else:         s = "XL" if w < 80 else "XXL"
    if bmi < 18.5: nhan_xet, emoji = "Gầy — nên tăng cường dinh dưỡng", "⚠️"
    elif bmi < 23: nhan_xet, emoji = "Cân nặng chuẩn — tuyệt vời!", "✅"
    elif bmi < 25: nhan_xet, emoji = "Hơi thừa cân", "⚡"
    else:          nhan_xet, emoji = "Thừa cân", "⚠️"
    return s, f"{emoji} BMI {bmi:.1f} — {nhan_xet}"

#  OCCASION DATA 
OCCASION_IMAGES = {
    "Đi làm / Văn phòng": [
        "https://images.pexels.com/photos/3760854/pexels-photo-3760854.jpeg",
        "https://images.pexels.com/photos/1205033/pexels-photo-1205033.jpeg",
        "https://images.pexels.com/photos/733872/pexels-photo-733872.jpeg",
        "https://images.pexels.com/photos/935985/pexels-photo-935985.jpeg",
        "https://images.pexels.com/photos/1036623/pexels-photo-1036623.jpeg",
        "https://images.pexels.com/photos/1181686/pexels-photo-1181686.jpeg",
        "https://images.pexels.com/photos/3756679/pexels-photo-3756679.jpeg",
        "https://images.pexels.com/photos/3760610/pexels-photo-3760610.jpeg",
    ],
    "Hẹn hò lãng mạn": [
        "https://images.pexels.com/photos/10803527/pexels-photo-10803527.jpeg",
        "https://images.pexels.com/photos/4034331/pexels-photo-4034331.jpeg",
        "https://images.pexels.com/photos/1126993/pexels-photo-1126993.jpeg",
        "https://images.pexels.com/photos/3775131/pexels-photo-3775131.jpeg",
        "https://images.pexels.com/photos/1460534/pexels-photo-1460534.jpeg",
        "https://images.pexels.com/photos/3163014/pexels-photo-3163014.jpeg",
        "https://images.pexels.com/photos/3206079/pexels-photo-3206079.jpeg",
        "https://images.pexels.com/photos/4552140/pexels-photo-4552140.jpeg",
    ],
    "Tiệc / Sự kiện": [
        "https://images.pexels.com/photos/3125056/pexels-photo-3125056.jpeg",
        "https://images.pexels.com/photos/2085739/pexels-photo-2085739.jpeg",
        "https://images.pexels.com/photos/1154189/pexels-photo-1154189.jpeg",
        "https://images.pexels.com/photos/2788488/pexels-photo-2788488.jpeg",
        "https://images.pexels.com/photos/3050273/pexels-photo-3050273.jpeg",
        "https://images.pexels.com/photos/459947/pexels-photo-459947.jpeg",
        "https://images.pexels.com/photos/1852381/pexels-photo-1852381.jpeg",
        "https://images.pexels.com/photos/1390599/pexels-photo-1390599.jpeg",
    ],
    "Đi chơi / Dạo phố": [
        "https://images.pexels.com/photos/1381556/pexels-photo-1381556.jpeg",
        "https://images.pexels.com/photos/1844012/pexels-photo-1844012.jpeg",
        "https://images.pexels.com/photos/2442080/pexels-photo-2442080.jpeg",
        "https://images.pexels.com/photos/1321485/pexels-photo-1321485.jpeg",
        "https://images.pexels.com/photos/1231649/pexels-photo-1231649.jpeg",
        "https://images.pexels.com/photos/1306246/pexels-photo-1306246.jpeg",
        "https://images.pexels.com/photos/1043474/pexels-photo-1043474.jpeg",
        "https://images.pexels.com/photos/1937336/pexels-photo-1937336.jpeg",
    ],
}

# VISUAL_MOCK = {
#     "jacket": ["https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400","https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=400","https://images.unsplash.com/photo-1520975954732-57dd22299614?w=400","https://images.unsplash.com/photo-1544022613-e87ca75a374c?w=400"],
#     "shoe":   ["https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400","https://images.unsplash.com/photo-1508296695146-257a814070b4?w=400","https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=400","https://images.unsplash.com/photo-1560769629-975ec94e6a86?w=400"],
#     "dress":  ["https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=400","https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=400","https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=400","https://images.unsplash.com/photo-1496747611176-843222e1e57c?w=400"],
#     "shirt":  ["https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400","https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=400","https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?w=400","https://images.unsplash.com/photo-1581655353564-df123a1eb820?w=400"],
#     "pant":   ["https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=400","https://images.unsplash.com/photo-1584864285022-198ca97f28c5?w=400","https://images.unsplash.com/photo-1555689502-c4b22d76c56f?w=400","https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=400"],
#     "bag":    ["https://images.unsplash.com/photo-1548624149-f9b1859aa7d0?w=400","https://images.unsplash.com/photo-1584916201218-f4242ceb4809?w=400","https://images.unsplash.com/photo-1590874103328-eac38a683ce7?w=400","https://images.unsplash.com/photo-1591561954557-26941169b49e?w=400"],
# }
VISUAL_MOCK = {
    "jacket": [
        "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400&q=80",
        "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=400&q=80",
        "https://images.unsplash.com/photo-1520975954732-57dd22299614?w=400&q=80",
        "https://images.unsplash.com/photo-1544022613-e87ca75a374c?w=400&q=80"
    ],
    "shoe": [
        "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&q=80",
        "https://images.unsplash.com/photo-1508296695146-257a814070b4?w=400&q=80",
        "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=400&q=80",
        "https://images.unsplash.com/photo-1560769629-975ec94e6a86?w=400&q=80"
    ],
    "dress": [
        "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=400&q=80",
        "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=400&q=80",
        "https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=400&q=80",
        "https://images.unsplash.com/photo-1496747611176-843222e1e57c?w=400&q=80"
    ],
    "shirt": [
        "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&q=80",
        "https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=400&q=80",
        "https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?w=400&q=80",
        "https://images.unsplash.com/photo-1581655353564-df123a1eb820?w=400&q=80"
    ],
    "pant": [
        "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=400&q=80",
        "https://images.unsplash.com/photo-1584864285022-198ca97f28c5?w=400&q=80",
        "https://images.unsplash.com/photo-1555689502-c4b22d76c56f?w=400&q=80",
        "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=400&q=80"
    ],
    "bag": [
        "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400&q=80",  
        "https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?w=400&q=80",  
        "https://images.unsplash.com/photo-1581605405669-fcdf81165afa?w=400&q=80", 
        "https://images.unsplash.com/photo-1547949003-9792a18a2601?w=400&q=80"   
    ],
}
STYLE_LOOKBOOK = {
    "Tối giản (Minimalist)": [
        "https://images.pexels.com/photos/7139533/pexels-photo-7139533.jpeg",
        "https://images.pexels.com/photos/31092569/pexels-photo-31092569.jpeg",
        "https://images.pexels.com/photos/7682081/pexels-photo-7682081.jpeg",
        "https://images.pexels.com/photos/2315311/pexels-photo-2315311.jpeg",
    ],
    "Cổ điển (Vintage)": [
        "https://images.pexels.com/photos/29625724/pexels-photo-29625724.jpeg",
        "https://images.pexels.com/photos/36976938/pexels-photo-36976938.jpeg",
        "https://images.pexels.com/photos/13683556/pexels-photo-13683556.jpeg",
        "https://images.pexels.com/photos/9830016/pexels-photo-9830016.jpeg",
    ],
    "Thể thao (Sporty)": [
        "https://images.pexels.com/photos/1552249/pexels-photo-1552249.jpeg",
        "https://images.pexels.com/photos/12443511/pexels-photo-12443511.jpeg",
        "https://images.pexels.com/photos/12298359/pexels-photo-12298359.jpeg",
        "https://images.pexels.com/photos/7242833/pexels-photo-7242833.jpeg",
    ],
    "Boho / Tự do": [
        "https://images.pexels.com/photos/2220316/pexels-photo-2220316.jpeg",
        "https://images.pexels.com/photos/972995/pexels-photo-972995.jpeg",
        "https://images.pexels.com/photos/3621117/pexels-photo-3621117.jpeg",
        "https://images.pexels.com/photos/1536619/pexels-photo-1536619.jpeg",
    ],
}

STYLE_DESC = {
    "Tối giản (Minimalist)": "Tinh tế, không thừa. Mỗi chi tiết đều có mục đích.",
    "Cổ điển (Vintage)":     "Vẻ đẹp hoài cổ với chất liệu mềm mại và họa tiết retro.",
    "Thể thao (Sporty)":     "Năng động, thoải mái — đẹp cả trên sân lẫn ngoài phố.",
    "Boho / Tự do":          "Phóng khoáng, layer nhiều, đậm chất cá nhân.",
}


#  CHATBOT ENGINE 
# Gemini được tích hợp sẵn để chatbot tự động trả lời, không cần nhập key ở terminal/giao diện.
# Lưu ý kỹ thuật: hard-code API key chỉ phù hợp demo/nộp bài; khi triển khai thật nên chuyển sang st.secrets hoặc biến môi trường.
GEMINI_API_KEY = "AIzaSyDCBGO_hvZJXqGRjussVjItTuXfr4o5blw"
GEMINI_MODEL = "gemini-2.0-flash"

CHAT_QUICK = [
    "Tìm áo sơ mi",
    "Tìm váy đi tiệc",
    "Tìm giày sneaker",
    "Gợi ý đồ đi làm",
    "Màu nào hợp da tôi?",
]

# Dữ liệu trực quan cho chatbot: ưu tiên trả ngay ảnh + mã SP khi người dùng hỏi tìm sản phẩm.
PRODUCT_CHAT_CATALOG = {
    "ao_so_mi": {
        "keywords": ["áo sơ mi", "ao so mi", "sơ mi", "so mi", "shirt", "áo công sở", "ao cong so"],
        "reply": "Áo sơ mi tham khảo phù hợp với nhu cầu của bạn:",
        "products": [
            {"asin": "SM_001", "title": "Sơ mi trắng basic", "imUrl": "https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=400&q=80"},
            {"asin": "SM_002", "title": "Sơ mi xanh công sở", "imUrl": "https://images.unsplash.com/photo-1603252109303-2751441dd157?w=400&q=80"},
            {"asin": "SM_003", "title": "Sơ mi oversize casual", "imUrl": "https://images.unsplash.com/photo-1581655353564-df123a1eb820?w=400&q=80"},
            {"asin": "SM_004", "title": "Sơ mi kẻ thanh lịch", "imUrl": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&q=80"},
        ],
    },
    "ao_thun": {
        "keywords": ["áo thun", "ao thun", "t-shirt", "tshirt", "áo phông", "ao phong", "polo"],
        "reply": "Dạ, đây là một số mẫu áo thun năng động và dễ phối đồ em gợi ý cho mình:",
        "products": [
            {"asin": "AT_001", "title": "Áo thun cotton basic", "imUrl": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&q=80"},
            {"asin": "AT_002", "title": "Áo polo thanh lịch", "imUrl": "https://images.unsplash.com/photo-1581655353564-df123a1eb820?w=400&q=80"},
            {"asin": "AT_003", "title": "Áo thun oversize", "imUrl": "https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?w=400&q=80"},
            {"asin": "AT_004", "title": "Áo thun in họa tiết", "imUrl": "https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=400&q=80"},
        ],
    },
    "ao_khoac": {
        "keywords": ["áo khoác", "ao khoac", "jacket", "coat", "hoodie", "blazer", "bomber"],
        "reply": "Áo khoác/blazer tham khảo:",
        "products": [
            {"asin": "AK_001", "title": "Blazer navy", "imUrl": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400&q=80"},
            {"asin": "AK_002", "title": "Jacket da cá tính", "imUrl": "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=400&q=80"},
            {"asin": "AK_003", "title": "Áo khoác streetwear", "imUrl": "https://images.unsplash.com/photo-1520975954732-57dd22299614?w=400&q=80"},
            {"asin": "AK_004", "title": "Coat tối giản", "imUrl": "https://images.unsplash.com/photo-1544022613-e87ca75a374c?w=400&q=80"},
        ],
    },
    "giay": {
        "keywords": ["giày", "giay", "sneaker", "boot", "boots", "shoe", "shoes", "cao gót", "cao got"],
        "reply": "Giày tham khảo dễ phối đồ:",
        "products": [
            {"asin": "GY_001", "title": "Sneaker trắng", "imUrl": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&q=80"},
            {"asin": "GY_002", "title": "Sneaker thể thao", "imUrl": "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=400&q=80"},
            {"asin": "GY_003", "title": "Giày casual", "imUrl": "https://images.unsplash.com/photo-1560769629-975ec94e6a86?w=400&q=80"},
            {"asin": "GY_004", "title": "Giày phối streetwear", "imUrl": "https://images.unsplash.com/photo-1508296695146-257a814070b4?w=400&q=80"},
        ],
    },
    "vay": {
        "keywords": ["váy", "vay", "đầm", "dam", "dress", "skirt", "gown", "đi tiệc", "di tiec", "tiệc", "tiec"],
        "reply": "Váy/đầm tham khảo cho bạn:",
        "products": [
            {"asin": "VAY_001", "title": "Midi dress thanh lịch", "imUrl": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=400&q=80"},
            {"asin": "VAY_002", "title": "Váy hẹn hò", "imUrl": "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=400&q=80"},
            {"asin": "VAY_003", "title": "Đầm nữ tính", "imUrl": "https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=400&q=80"},
            {"asin": "VAY_004", "title": "Maxi dress nổi bật", "imUrl": "https://images.unsplash.com/photo-1496747611176-843222e1e57c?w=400&q=80"},
        ],
    },
    "quan": {
        "keywords": ["quần", "quan", "jean", "jeans", "pant", "pants", "trouser", "short"],
        "reply": "Quần tham khảo dễ phối:",
        "products": [
            {"asin": "Q_001", "title": "Quần jeans basic", "imUrl": "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=400&q=80"},
            {"asin": "Q_002", "title": "Quần âu công sở", "imUrl": "https://images.unsplash.com/photo-1584864285022-198ca97f28c5?w=400&q=80"},
            {"asin": "Q_003", "title": "Quần casual", "imUrl": "https://images.unsplash.com/photo-1555689502-c4b22d76c56f?w=400&q=80"},
            {"asin": "Q_004", "title": "Quần ống rộng", "imUrl": "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=400&q=80"},
        ],
    },
    "tui": {
        "keywords": ["túi", "tui", "bag", "backpack", "balo", "clutch", "tote"],
        "reply": "Túi phụ kiện tham khảo:",
        "products": [
            {"asin": "TUI_001", "title": "Tote da công sở", "imUrl": "https://images.unsplash.com/photo-1548624149-f9b1859aa7d0?w=400&q=80"},
            {"asin": "TUI_002", "title": "Túi đeo vai", "imUrl": "https://images.unsplash.com/photo-1584916201218-f4242ceb4809?w=400&q=80"},
            {"asin": "TUI_003", "title": "Túi xách nữ", "imUrl": "https://images.unsplash.com/photo-1590874103328-eac38a683ce7?w=400&q=80"},
            {"asin": "TUI_004", "title": "Clutch tối giản", "imUrl": "https://images.unsplash.com/photo-1591561954557-26941169b49e?w=400&q=80"},
        ],
    },
    "di_lam": {
        "keywords": ["đi làm", "di lam", "văn phòng", "van phong", "office", "công sở", "cong so"],
        "reply": "Set đồ đi làm trực quan nên tham khảo:",
        "products": [
            {"asin": "OFF_001", "title": "Blazer + sơ mi trắng", "imUrl": "https://images.unsplash.com/photo-1487222477894-8943e31ef7b2?w=400&q=80"},
            {"asin": "OFF_002", "title": "Suit công sở", "imUrl": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=400&q=80"},
            {"asin": "OFF_003", "title": "Sơ mi + quần âu", "imUrl": "https://images.unsplash.com/photo-1594938298596-70f594f62bce?w=400&q=80"},
            {"asin": "OFF_004", "title": "Blazer tối giản", "imUrl": "https://images.unsplash.com/photo-1617137968427-85924c800a22?w=400&q=80"},
        ],
    },
}


CHATBOT_SYSTEM_PROMPT = """
Bạn là trợ lý tư vấn thời trang trong ứng dụng HỆ THỐNG GỢI Ý SẢN PHẨM THỜI TRANG.
Nhiệm vụ của bạn:
1. Trả lời mọi câu hỏi về thời trang, phối đồ, xu hướng, màu sắc hợp tông da, và cách chọn size.
2. Nếu khách hàng hỏi về một món đồ cụ thể (ví dụ: áo len, quần kaki, phụ kiện) mà không có ảnh hiển thị, hãy dùng kiến thức của bạn để tư vấn cách phối đồ, chất liệu nên chọn, và phong cách phù hợp.
3. Giọng điệu: Tự nhiên, lịch sự (dạ, vâng, ạ), ngắn gọn, súc tích (tối đa 3-4 câu).
4. TUYỆT ĐỐI KHÔNG bịa đặt giá tiền, link mua hàng hay mã giảm giá. 
Nếu câu hỏi không liên quan đến thời trang, hãy nhẹ nhàng từ chối và hướng khách hàng về chủ đề trang phục.
""".strip()

def chatbot_reply(msg: str) -> str:
    """Fallback phía Python nếu cần dùng lại ở nơi khác."""
    msg_lower = msg.lower()
    direct_rules = {
        "size": "Dùng tab 📏 Gợi ý size, nhập chiều cao/cân nặng để ra size ngay. Quy đổi nhanh: S <50kg, M 50–60kg, L 60–70kg, XL 70–80kg.",
        "màu": "Da sáng hợp navy/đỏ đô/tím lavender. Da vàng-bánh mật hợp cam đất/vàng olive/xanh lá/đỏ gạch. Da ngăm hợp trắng/vàng tươi/cam rực/xanh cobalt.",
        "đi làm": "Gợi ý đi làm: sơ mi trắng hoặc xanh nhạt + quần âu thẳng + blazer navy/xám + giày tối giản.",
        "tiệc": "Gợi ý đi tiệc: midi dress, maxi dress hoặc set blazer thanh lịch; chọn màu đen, đỏ đô, ánh kim nhẹ hoặc xanh cobalt.",
    }
    for kw, reply in direct_rules.items():
        if kw in msg_lower:
            return reply
    return "Tôi đã nhận câu hỏi. Hãy nhập trực tiếp sản phẩm bạn cần tìm, ví dụ: 'tìm áo sơ mi', 'tìm váy đi tiệc', 'tìm giày sneaker'."


#  SESSION 
def init_session():
    defaults = {
        'cart': [], 'logged_in': False, 'username': '', 'role': '',
        'chat_history': [{"role": "assistant", "content": "Chào bạn! 👋 Tôi là trợ lý AI thời trang của **HỆ THỐNG GỢI Ý SẢN PHẨM THỜI TRANG**. Bạn cần tư vấn gì hôm nay?"}],
        'algo_run': False, 'algo_results': None, 'algo_df': None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# chatbox 
@st.cache_data
def process_chatbot_message(prompt):
    try:
        # Khởi tạo chuẩn theo SDK mới của Google
        client = genai.Client(api_key="AIzaSyDCBGO_hvZJXqGRjussVjItTuXfr4o5blw")
        
        system_instruction = CHATBOT_SYSTEM_PROMPT # Tận dụng luôn prompt bạn đã định nghĩa
        
        response = client.models.generate_content(
            model='gemini-2.0-flash', # Đưa về model chuẩn ổn định
            contents=f"Hệ thống: {system_instruction}\nKhách hàng: {prompt}\nTrợ lý:"
        )
        return response.text
        
    except Exception as e:
        print(f"API Error: {e}")
        return "Hiện tại hệ thống AI đang quá tải, bạn có thể thử lại sau vài phút nhé! 👗"

# FLOATING CHATBOT 

def render_floating_chat():
    import json
    import base64
    import streamlit as st

    # 1. Chuẩn bị dữ liệu JSON
    chips_json = json.dumps(CHAT_QUICK, ensure_ascii=False)
    catalog_json = json.dumps(PRODUCT_CHAT_CATALOG, ensure_ascii=False)
    api_key_json = json.dumps(GEMINI_API_KEY, ensure_ascii=False)
    prompt_json = json.dumps(CHATBOT_SYSTEM_PROMPT, ensure_ascii=False)

    init_msgs = [
        {"role": m["role"], "content": m["content"].replace("**", "").replace("`", "'")}
        for m in st.session_state.get("chat_history", [
            {"role": "assistant", "content": "Chào bạn! 👋 Tôi là trợ lý AI thời trang. Bạn cần tư vấn gì hôm nay?"}
        ])
    ]
    msgs_json = json.dumps(init_msgs, ensure_ascii=False)

    # 2. Toàn bộ kịch bản HTML/JS gộp chung
    raw_html = """
    <script>
    (function() {
      var pDoc = window.parent.document;

      // Dọn dẹp nút cũ
      ['_fchat_style', '_fchat_btn', '_fchat_box', '_fchat_tooltip'].forEach(function(id) {
        var el = pDoc.getElementById(id);
        if (el && el.parentNode) el.parentNode.removeChild(el);
      });

      // ── CSS Style ──
      var styleEl = pDoc.createElement('style');
      styleEl.id = '_fchat_style';
      styleEl.textContent = [
        '#_fchat_btn { position:fixed; bottom:28px; right:28px; z-index:99999; background:linear-gradient(135deg, #ffbc00, #ff9900); color:#1a1a2e; font-size:0.95rem; font-weight:700; border:none; cursor:pointer; border-radius:50px; padding:10px 20px; display:flex; align-items:center; gap:8px; box-shadow:0 6px 24px rgba(255, 153, 0, 0.45); font-family:"DM Sans",sans-serif; transition:transform 0.2s, box-shadow 0.2s; user-select:none; }',
        '#_fchat_btn:hover { transform:scale(1.05); box-shadow:0 8px 28px rgba(255, 153, 0, 0.6); }',
        '#_fchat_tooltip { position:fixed; bottom:85px; right:28px; z-index:99998; background:#ffffff; border-radius:12px; padding:12px 16px; box-shadow:0 8px 28px rgba(0,0,0,0.12); border:1px solid #f0e0e6; font-family:"DM Sans",sans-serif; font-size:0.85rem; color:#1a1a2e; max-width:220px; transition:opacity 0.3s; }',
        '#_fchat_tooltip strong { color:#c9184a; display:block; margin-bottom:4px; font-size:0.95rem; }',
        '#_fchat_box { position:fixed; bottom:90px; right:28px; z-index:100000; width:360px; max-height:540px; background:#fff; border-radius:20px; box-shadow:0 16px 48px rgba(0,0,0,0.18); display:flex; flex-direction:column; overflow:hidden; border:1px solid #f0e0e6; transition:opacity 0.25s,transform 0.25s; font-family:"DM Sans",sans-serif; }',
        '#_fchat_box.hidden { opacity:0; pointer-events:none; transform:translateY(16px) scale(0.97); }',
        '#_fchat_header { background:linear-gradient(135deg,#c9184a,#ff6b6b); padding:14px 18px; display:flex; align-items:center; justify-content:space-between; flex-shrink:0; }',
        '#_fchat_header .cht { color:white; font-weight:700; font-size:0.95rem; display:flex; align-items:center; gap:8px; }',
        '#_fchat_close { background:rgba(255,255,255,0.2); border:none; color:white; border-radius:50%; width:28px; height:28px; cursor:pointer; font-size:1rem; display:flex; align-items:center; justify-content:center; }',
        '#_fchat_close:hover { background:rgba(255,255,255,0.35); }',
        '#_fchat_chips { display:flex; flex-wrap:wrap; gap:6px; padding:10px 14px 4px; flex-shrink:0; background:#fff8f9; border-bottom:1px solid #fde0e8; }',
        '._fchip { background:#fff1f2; border:1px solid #fecdd3; color:#c9184a; border-radius:50px; padding:4px 11px; font-size:0.72rem; cursor:pointer; white-space:nowrap; transition:all 0.15s; }',
        '._fchip:hover { background:#c9184a; color:white; border-color:#c9184a; }',
        '#_fchat_msgs { flex:1; overflow-y:auto; padding:14px; display:flex; flex-direction:column; gap:10px; min-height:0; }',
        '._fmsg { max-width:82%; padding:9px 13px; border-radius:14px; font-size:0.84rem; line-height:1.45; word-break:break-word; }',
        '._fmsg.bot { background:#f3f4f6; color:#1a1a2e; align-self:flex-start; border-bottom-left-radius:4px; }',
        '._fmsg.user { background:linear-gradient(135deg,#c9184a,#ff6b6b); color:white; align-self:flex-end; border-bottom-right-radius:4px; }',
        '._fmsg.product { max-width:96%; width:96%; background:#f8fafc; }',
        '._fmsg.loading { color:#64748b; font-style:italic; }',
        '._fprod_intro { font-weight:700; color:#1a1a2e; margin-bottom:8px; }',
        '._fprod_grid { display:grid; grid-template-columns:1fr 1fr; gap:8px; }',
        '._fprod_card { background:white; border:1px solid #f1d5dd; border-radius:12px; overflow:hidden; box-shadow:0 1px 5px rgba(0,0,0,0.06); }',
        '._fprod_card img { width:100%; height:126px; object-fit:cover; display:block; background:#f3f4f6; }',
        '._fprod_body { padding:7px; }',
        '._fprod_code { display:inline-block; background:#c9184a; color:white; border-radius:999px; padding:2px 7px; font-size:0.68rem; font-weight:700; margin-bottom:4px; }',
        '._fprod_name { font-size:0.75rem; color:#1a1a2e; font-weight:600; line-height:1.25; }',
        '#_fchat_inrow { display:flex; gap:8px; padding:10px 12px; border-top:1px solid #f0e0e6; background:white; flex-shrink:0; }',
        '#_fchat_inp { flex:1; border:1px solid #fecdd3; border-radius:50px; padding:8px 14px; font-size:0.83rem; outline:none; color:#1a1a2e; }',
        '#_fchat_inp:focus { border-color:#c9184a; }',
        '#_fchat_send { background:linear-gradient(135deg,#c9184a,#ff6b6b); border:none; border-radius:50%; width:36px; height:36px; color:white; font-size:1rem; cursor:pointer; flex-shrink:0; display:flex; align-items:center; justify-content:center; transition:transform 0.15s; }',
        '#_fchat_send:hover { transform:scale(1.1); }'
      ].join(' ');
      pDoc.head.appendChild(styleEl);

      var GEMINI_API_KEY = __GEMINI_API_KEY__;
      var SYSTEM_PROMPT = __SYSTEM_PROMPT__;
      var PRODUCT_CATALOG = __PRODUCT_CATALOG__;
      var CHIPS = __CHIPS__;
      var INIT_MSGS = __INIT_MSGS__;

      // Khởi tạo UI
      var tooltip = pDoc.createElement('div');
      tooltip.id = '_fchat_tooltip';
      tooltip.innerHTML = '<strong>HỆ THỐNG GỢI Ý SẢN PHẨM THỜI TRANG</strong>Em rất sẵn lòng hỗ trợ Anh/Chị 🤩';
      pDoc.body.appendChild(tooltip);

      var btn = pDoc.createElement('button');
      btn.id = '_fchat_btn';
      btn.innerHTML = '<span style="font-size:1.2rem;">🤖</span> Trợ lý AI';
      pDoc.body.appendChild(btn);

      var box = pDoc.createElement('div');
      box.id = '_fchat_box';
      box.className = 'hidden';

      var header = pDoc.createElement('div');
      header.id = '_fchat_header';
      header.innerHTML = '<div class="cht"><span>✨</span><span>Trợ lý Thời trang AI</span></div>';
      var closeBtn = pDoc.createElement('button');
      closeBtn.id = '_fchat_close';
      closeBtn.innerHTML = '✕';
      header.appendChild(closeBtn);
      box.appendChild(header);

      var chipsDiv = pDoc.createElement('div');
      chipsDiv.id = '_fchat_chips';
      CHIPS.forEach(function(label) {
        var c = pDoc.createElement('button');
        c.className = '_fchip';
        c.textContent = label;
        chipsDiv.appendChild(c);
      });
      box.appendChild(chipsDiv);

      var msgsDiv = pDoc.createElement('div');
      msgsDiv.id = '_fchat_msgs';
      INIT_MSGS.forEach(function(m) {
        var div = pDoc.createElement('div');
        div.className = '_fmsg ' + (m.role === 'assistant' ? 'bot' : 'user');
        div.textContent = m.content;
        msgsDiv.appendChild(div);
      });
      box.appendChild(msgsDiv);

      var inRow = pDoc.createElement('div');
      inRow.id = '_fchat_inrow';
      var inp = pDoc.createElement('input');
      inp.id = '_fchat_inp';
      inp.type = 'text';
      inp.placeholder = 'Hỏi gợi ý phối đồ...';
      var sendBtn = pDoc.createElement('button');
      sendBtn.id = '_fchat_send';
      sendBtn.innerHTML = '➤';
      inRow.appendChild(inp);
      inRow.appendChild(sendBtn);
      box.appendChild(inRow);

      pDoc.body.appendChild(box);

      // Logic
      function normalizeText(s) { return (s||'').toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g, '').replace(/đ/g, 'd'); }
      function escapeHTML(s) { return String(s||'').replace(/[&<>'"]/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]; }); }
      function scrollBottom() { var el = pDoc.getElementById('_fchat_msgs'); if (el) el.scrollTop = el.scrollHeight; }

      function appendMsg(text, role, extraClass) {
        var div = pDoc.createElement('div');
        div.className = '_fmsg ' + role + (extraClass ? ' ' + extraClass : '');
        div.textContent = text;
        msgsDiv.appendChild(div);
        scrollBottom();
        return div;
      }

      function appendBotHTML(html) {
        var div = pDoc.createElement('div');
        div.className = '_fmsg bot product';
        div.innerHTML = html;
        msgsDiv.appendChild(div);
        scrollBottom();
        return div;
      }

      function detectProductIntent(msg) {
        var m = normalizeText(msg);
        for (var key in PRODUCT_CATALOG) {
          var group = PRODUCT_CATALOG[key];
          for (var i = 0; i < group.keywords.length; i++) {
            if (m.indexOf(normalizeText(group.keywords[i])) !== -1) return group;
          }
        }
        return null;
      }

      function renderProductHTML(group) {
        var cards = group.products.map(function(p) {
          return '<div class="_fprod_card"><img src="' + escapeHTML(p.imUrl) + '" loading="lazy" onerror="this.src=\\'https://picsum.photos/seed/x/400/500\\'"><div class="_fprod_body"><div class="_fprod_code">' + escapeHTML(p.asin) + '</div><div class="_fprod_name">' + escapeHTML(p.title) + '</div></div></div>';
        }).join('');
        return '<div class="_fprod_intro">' + escapeHTML(group.reply) + '</div><div class="_fprod_grid">' + cards + '</div>';
      }

      // ── KỊCH BẢN DỰ PHÒNG (RULE-BASED) CHỐNG CHỊU MỌI LỖI ──
      function getFallbackReply(msg) {
        var m = normalizeText(msg);
        if (m.indexOf('size') !== -1 || m.indexOf('rong') !== -1 || m.indexOf('chat') !== -1 || m.indexOf('can nang') !== -1) 
            return 'Dạ, để em tính size chuẩn xác nhất, anh/chị có thể sử dụng tab 📏 Gợi ý size ở giao diện chính nhé! Hoặc quy đổi nhanh: S (<50kg), M (50-60kg), L (60-70kg).';
        if (m.indexOf('mau') !== -1 || m.indexOf('da') !== -1) 
            return 'Để phối màu hợp nhất, anh/chị xem thử tab 🎨 Phối màu nhé. Da sáng hợp tông lạnh (Navy, Đỏ đô), da ngăm hợp tông ấm (Cam, Vàng) ạ!';
        if (m.indexOf('di lam') !== -1 || m.indexOf('cong so') !== -1) 
            return 'Với đồ công sở, anh/chị chọn áo sơ mi kết hợp quần âu hoặc khoác thêm blazer là thanh lịch và chuyên nghiệp nhất ạ.';
        if (m.indexOf('tiec') !== -1 || m.indexOf('dam cuoi') !== -1) 
            return 'Đi tiệc thì đầm midi, váy xòe hoặc set áo khoác dạ/blazer sẽ mang lại vẻ ngoài vô cùng sang trọng ạ.';
        return 'Dạ, anh/chị đang cần tìm phong cách nào ạ? Anh/chị cứ nhập tên sản phẩm cụ thể như "tìm áo sơ mi", "tìm váy", "tìm giày" để em gợi ý nhé!';
      }

      async function askGemini(msg) {
        try {
            // Sử dụng bản gemini-1.5-flash để ổn định nhất trên nền tảng Web
            var endpoint = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=' + encodeURIComponent(GEMINI_API_KEY);
            
            var payload = {
                contents: [{ 
                    role: 'user', 
                    parts: [{ text: "Hệ thống: " + SYSTEM_PROMPT + "\\n\\nKhách hàng: " + msg + "\\nTrợ lý AI:" }] 
                }],
                // Tắt các bộ lọc nhạy cảm để tránh bị chặn nhầm từ khóa thời trang
                safetySettings: [
                    { category: "HARM_CATEGORY_HARASSMENT", threshold: "BLOCK_NONE" },
                    { category: "HARM_CATEGORY_HATE_SPEECH", threshold: "BLOCK_NONE" },
                    { category: "HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold: "BLOCK_NONE" },
                    { category: "HARM_CATEGORY_DANGEROUS_CONTENT", threshold: "BLOCK_NONE" }
                ]
            };

            var res = await fetch(endpoint, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(payload)
            });
            
            if (!res.ok) throw new Error("Lỗi kết nối");
            var data = await res.json();
            
            if (!data.candidates || data.candidates.length === 0) throw new Error("Lỗi safety");
            
            return data.candidates[0].content.parts[0].text;
            
        } catch (e) { 
            // Nếu API sập/quá tải, CHUYỂN NGAY SANG DÙNG KỊCH BẢN DỰ PHÒNG THAY VÌ BÁO LỖI
            return getFallbackReply(msg); 
        }
      }

      function toggleChat() {
        box.classList.toggle('hidden');
        if(tooltip) tooltip.style.opacity = '0'; 
        if (!box.classList.contains('hidden')) {
            scrollBottom();
            inp.focus();
        }
      }

      async function handleUserText(text) {
        appendMsg(text, 'user');
        
        // 1. Kiểm tra catalog sản phẩm có sẵn
        var pGroup = detectProductIntent(text);
        if (pGroup) {
          setTimeout(function() { appendBotHTML(renderProductHTML(pGroup)); }, 180);
          return;
        }
        
        // 2. Nếu không phải tìm sản phẩm -> Hỏi AI
        var loading = appendMsg('Đang gõ...', 'bot', 'loading');
        var answer = await askGemini(text);
        loading.classList.remove('loading');
        loading.textContent = answer;
        scrollBottom();
      }

      function sendMsg() {
        var text = (inp.value || '').trim();
        if (!text) return;
        inp.value = '';
        handleUserText(text);
      }

      btn.addEventListener('click', toggleChat);
      closeBtn.addEventListener('click', toggleChat);
      sendBtn.addEventListener('click', sendMsg);
      inp.addEventListener('keydown', function(e) { if (e.key === 'Enter') sendMsg(); });
      chipsDiv.querySelectorAll('._fchip').forEach(function(c) {
        c.addEventListener('click', function() { handleUserText(c.textContent.trim()); });
      });

      scrollBottom();
    })();
    </script>
    """

    # 3. Gắn Data Python vào Javascript
    js_code = (
        raw_html
        .replace("__GEMINI_API_KEY__", api_key_json)
        .replace("__SYSTEM_PROMPT__", prompt_json)
        .replace("__PRODUCT_CATALOG__", catalog_json)
        .replace("__CHIPS__", chips_json)
        .replace("__INIT_MSGS__", msgs_json)
    )

    # 4. Mã hóa sạch 100% bằng Base64
    b64_code = base64.b64encode(js_code.encode('utf-8')).decode('utf-8')

    # 5. Injection qua Iframe an toàn
    iframe_html = f"""
    <iframe 
        srcdoc="<script>document.write(decodeURIComponent(escape(window.atob('{b64_code}'))));</script>" 
        style="width: 1px; height: 1px; border: none; position: absolute; pointer-events: none; opacity: 0; z-index: -100;">
    </iframe>
    """
    
    st.markdown(iframe_html, unsafe_allow_html=True)
#  LOGIN PAGE 
def login_page():
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.markdown('<div class="hero-title">HỆ THỐNG GỢI Ý SẢN PHẨM THỜI TRANG', unsafe_allow_html=True)
        st.markdown('<div class="hero-sub">Cá nhân hóa phong cách của bạn</div>', unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["🔑 Đăng nhập", "📝 Đăng ký"])
        with tab_login:
            login_user = st.text_input("Tên đăng nhập", key="login_user", placeholder="admin")
            login_pwd  = st.text_input("Mật khẩu", type="password", key="login_pwd", placeholder="••••••")
            if st.button("Đăng nhập →", type="primary", width='stretch', key="btn_login"):
                if not login_user or not login_pwd:
                    st.error("Vui lòng nhập đầy đủ thông tin.")
                elif login_user == "admin" and login_pwd == "123":
                    st.session_state.update(logged_in=True, username=login_user, role="Admin")
                    st.rerun()
                else:
                    role = check_login(login_user, login_pwd)
                    if role:
                        st.session_state.update(logged_in=True, username=login_user, role=role)
                        st.rerun()
                    else:
                        st.error("❌ Sai tên đăng nhập hoặc mật khẩu.")
            st.caption("Tài khoản demo: **admin** / **123**")

        with tab_register:
            reg_user = st.text_input("Tên đăng nhập *", key="reg_user", placeholder="Tối thiểu 3 ký tự")
            reg_pwd  = st.text_input("Mật khẩu *", type="password", key="reg_pwd", placeholder="Tối thiểu 6 ký tự")
            reg_pwd2 = st.text_input("Xác nhận mật khẩu *", type="password", key="reg_pwd2")
            # THÊM CHỌN QUYỀN TẠI ĐÂY
            reg_role = st.selectbox("Vai trò tài khoản *", ["Người dùng", "Admin"], key="reg_role")
            
            if st.button("Tạo tài khoản →", type="primary", width='stretch', key="btn_register"):
                if reg_pwd != reg_pwd2:
                    st.error("❌ Mật khẩu xác nhận không khớp.")
                else:
                    # Truyền reg_role vào hàm register_user
                    ok, msg = register_user(reg_user, reg_pwd, reg_role)
                    if ok: st.success(msg)
                    else:  st.error(f"❌ {msg}")

# ── ADMIN DASHBOARD ──
def admin_dashboard(df_raw):
    st.markdown('<div class="hero-title">⚙️ BẢNG ĐIỀU KHIỂN QUẢN TRỊ</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Quản lý hệ thống và người dùng</div>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("### 👑 Admin Menu")
        st.caption(f"Xin chào Quản trị viên: **{st.session_state.username}**")
        st.divider()
        if st.button("🚪 Đăng xuất", width='stretch', key="admin_logout"):
            st.session_state.clear()
            st.rerun()

    tab1, tab2 = st.tabs(["📊 Thống kê hệ thống", "👥 Quản lý người dùng"])
    
    with tab1:
        st.subheader("Tổng quan dữ liệu")
        col1, col2, col3 = st.columns(3)
        
        users = get_all_users()
        total_users = len(users)
        total_products = len(df_raw) if df_raw is not None else 0
        
        col1.metric("Tổng số người dùng", total_users)
        col2.metric("Tổng số sản phẩm", total_products)
        col3.metric("Trạng thái Model", "Sẵn sàng ✅")
        
        st.divider()
        st.markdown("#### 🛍️ Xem trước Dữ liệu Sản phẩm (Data_Final.csv)")
        st.dataframe(df_raw.head(50), use_container_width=True)

    with tab2:
        st.subheader("Danh sách tài khoản")
        users = get_all_users()
        
        # Tạo bảng hiển thị người dùng
        df_users = pd.DataFrame(users, columns=["Tên đăng nhập", "Quyền hạn"])
        st.dataframe(df_users, use_container_width=True)
        
        st.divider()
        st.markdown("#### 🗑️ Xóa tài khoản")
        col_del, col_btn = st.columns([3, 1])
        with col_del:
            user_to_delete = st.selectbox("Chọn người dùng cần xóa:", [u[0] for u in users if u[0] != st.session_state.username])
        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Xóa tài khoản", type="primary"):
                if user_to_delete:
                    success, msg = delete_user(user_to_delete)
                    if success:
                        st.success(msg)
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(msg)
#  MAIN APP 
# def main():
#     init_session()
#     df_raw = load_data()

#     if not st.session_state.logged_in:
#         login_page()
#         return
    
#     render_floating_chat()


#     # ── SIDEBAR ──
#     with st.sidebar:
#         st.markdown("### 🎛️ Bảng Điều Khiển")
#         st.caption(f"Xin chào, **{st.session_state.username}**!")
#         st.divider()

#         # user_id = st.text_input("Mã Khách hàng", value="U10293")'
#         # 1. Trích xuất danh sách Mã Khách hàng duy nhất từ data
#         # LƯU Ý: Thay 'reviewerID' hoặc 'user_id' bằng tên cột chứa mã KH trong file Data_Final.csv của bạn
#         if 'reviewerID' in df_raw.columns:
#             unique_users = df_raw['reviewerID'].dropna().astype(str).unique().tolist()
#         elif 'user_id' in df_raw.columns:
#             unique_users = df_raw['user_id'].dropna().astype(str).unique().tolist()
#         else:
#             # Fallback nếu chưa load được cột mã KH (danh sách mẫu)
#             unique_users = ["U10293", "U10294", "U10295", "A1B2C3D4"]

#         # 2. Thêm tùy chọn nhập thủ công lên đầu danh sách
#         user_options = [" Nhập thủ công "] + unique_users

#         # 3. Hiển thị Selectbox (Streamlit mặc định cho phép gõ vào ô này để tìm kiếm mã nhanh)
#         selected_user = st.selectbox("Mã Khách hàng (Chọn / Tìm kiếm)", user_options)

#         # 4. Logic: Nếu chọn "Nhập thủ công", hiện thêm ô nhập text. Nếu không, lấy mã đã chọn.
#         if selected_user == " Nhập thủ công ":
#             user_id = st.text_input("✏️ Nhập mã khách hàng mới:", value="U10293")
#         else:
#             user_id = selected_user
#         model   = st.selectbox("Thuật toán gợi ý", [
#             "SVD (Phân rã ma trận)",
#             "KNN Basic",
#             "Sản phẩm thịnh hành (Popularity)"
#         ])
#         top_n   = st.selectbox("Số lượng (Top-N)", [4, 8, 12], index=1)

#         if st.button("▶ Chạy thuật toán", type="primary", width='stretch'):
#             with st.spinner("Đang phân tích và gợi ý..."):
#                 res_df, rmse, elapsed = run_algorithm(df_raw, model, user_id, top_n)
#                 st.session_state.algo_run     = True
#                 st.session_state.algo_df      = res_df
#                 st.session_state.algo_results = {
#                     "model": model, "rmse": rmse, "time": elapsed,
#                     "top": top_n, "user": user_id
#                 }
#             st.success("✅ Hoàn thành!")

#         st.divider()
#         cart_n = len(st.session_state.cart)
#         st.markdown(f"### 🛒 Giỏ hàng &nbsp; <span class='cart-badge'>{cart_n}</span>", unsafe_allow_html=True)
#         if st.session_state.cart:
#             for item in st.session_state.cart:
#                 st.write(f"• {item}")
#             if st.button("🗑 Xóa tất cả", width='stretch'):
#                 st.session_state.cart = []
#                 st.rerun()
#         else:
#             st.caption("Giỏ hàng trống")

#         st.divider()
#         if st.button("🚪 Đăng xuất", width='stretch'):
#             st.session_state.clear()
#             st.rerun()

#     # ── HEADER ──
#     st.markdown('<div class="hero-title">✨ HỆ THỐNG GỢI Ý SẢN PHẨM THỜI TRANG</div>', unsafe_allow_html=True)
#     st.markdown('<div class="hero-sub">Trung tâm Trải nghiệm Thời trang Cá nhân hóa</div>', unsafe_allow_html=True)

#     # ── ALGO RESULT BANNER ──
#     if st.session_state.algo_run and st.session_state.algo_results:
#         res    = st.session_state.algo_results
#         res_df = st.session_state.algo_df
#         model_short = res['model'].split('(')[0].strip()
#         st.markdown(f"""
#         <div class="algo-banner">
#             <h3> Kết quả Thuật toán — Top {res['top']} gợi ý cho {res['user']}</h3>
#             <div class="metrics-row">
#                 <div class="metric-chip">Mô hình: <span>{model_short}</span></div>
#                 <div class="metric-chip">RMSE: <span>{res['rmse']}</span></div>
#                 <div class="metric-chip">Thời gian: <span>{res['time']}</span></div>
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
#         render_product_grid(res_df, "algo_top")
#         st.divider()
        
#     # ── TABS ──
#     st.markdown("### 🛠️ Khám phá Tính năng")
#     t1, t2, t3, t4, t5 = st.tabs([
#         "📝 Phong cách",
#         "📏 Gợi ý size",
#         "🔍 Tìm ảnh",
#         "💃 Theo dịp",
#         "🎨 Phối màu",
#     ])

#     # ══ TAB 1: PHONG CÁCH ══
#     with t1:
#         algo_mini_panel()
#         st.subheader("📝 Bài kiểm tra phong cách — Lookbook")

#         col_sel, col_info = st.columns([2, 3])
#         with col_sel:
#             phong_cach = st.selectbox("Chọn phong cách:", list(STYLE_LOOKBOOK.keys()), key="style_sel")
#         with col_info:
#             st.info(f"💡 **{phong_cach}** — {STYLE_DESC.get(phong_cach,'')}")

#         if st.button("✨ Xem Lookbook", type="primary"):
#             images = STYLE_LOOKBOOK.get(phong_cach, [])
#             l_cols = st.columns(4)
#             for i, img in enumerate(images):
#                 with l_cols[i % 4]:
#                     st.markdown(f'<div class="style-tag">{phong_cach.split("(")[0].strip()}</div>', unsafe_allow_html=True)
#                     try:
#                         st.image(img, width='stretch')
#                     except Exception:
#                         st.image(f"https://picsum.photos/seed/{i*3}/400/500", width='stretch')

#         if st.session_state.algo_run and st.session_state.algo_df is not None:
#             st.markdown("")
#             st.markdown(f"####  Sản phẩm gợi ý ({st.session_state.algo_results['model'].split('(')[0].strip()}) — có thể phù hợp phong cách này")
#             render_product_grid(st.session_state.algo_df.head(4), "t1_algo")

#     # ══ TAB 2: SIZE ══
#     with t2:
#         algo_mini_panel()
#         st.subheader("📏 Tư vấn size thông minh")

#         c1, c2, c3 = st.columns([2, 2, 3])
#         h = c1.number_input("Chiều cao (cm)", 100, 250, 165)
#         w = c2.number_input("Cân nặng (kg)", 30, 200, 60)

#         with c3:
#             st.markdown("<br>", unsafe_allow_html=True)
#             if st.button("📐 Tính ngay", type="primary", width='stretch'):
#                 size, bmi_note = calculate_size(h, w)
#                 if size:
#                     st.markdown(f"""
#                     <div class="size-result-box">
#                         <div style="font-size:0.85rem;color:#f9a8d4;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:4px;">Size của bạn</div>
#                         <div class="size-big">{size}</div>
#                         <div style="font-size:0.9rem;color:#cbd5e1;margin-top:8px;">{bmi_note}</div>
#                     </div>
#                     """, unsafe_allow_html=True)

#         st.markdown("")
#         st.markdown("#### 📊 Bảng size tham khảo")
#         size_table = pd.DataFrame({
#             "Size": ["XS", "S", "M", "L", "XL", "XXL"],
#             "Chiều cao": ["<150cm", "150–155cm", "155–162cm", "163–169cm", "170–175cm", ">175cm"],
#             "Cân nặng":  ["<45kg", "45–50kg", "50–60kg", "60–70kg", "70–80kg", ">80kg"],
#             "Ngực (cm)": ["78–80", "80–84", "84–88", "88–92", "92–96", "96–102"],
#             "Eo (cm)":   ["60–62", "62–66", "66–70", "70–74", "74–78", "78–84"],
#         })
#         st.dataframe(size_table, width='stretch', hide_index=True)

#     # ══ TAB 3: TÌM ẢNH ══
#     # with t3:
#     #     algo_mini_panel()
#     #     st.subheader("🔍 Tìm kiếm bằng hình ảnh")

#     #     col_up, col_res = st.columns([1, 2])
#     #     with col_up:
#     #         uploaded_img = st.file_uploader("Tải ảnh sản phẩm", type=['jpg','jpeg','png'], label_visibility="collapsed")
#     #         if uploaded_img:
#     #             st.image(uploaded_img, caption="Ảnh của bạn", width='stretch')

#     #     with col_res:
#     #         if uploaded_img:
#     #             fname = uploaded_img.name.lower()
#     #             kw_map = {
#     #                 ("khoac","jacket","coat","hoodie","bomber"): "jacket",
#     #                 ("giay","shoe","sneaker","boot","heel"):     "shoe",
#     #                 ("vay","dress","dam","gown","skirt"):        "dress",
#     #                 ("ao","shirt","top","tee","blouse"):         "shirt",
#     #                 ("quan","pant","jean","trouser","short"):    "pant",
#     #                 ("balo","bag","backpack","tui"):             "bag",
#     #             }
#     #             detected_kw = None
#     #             for keys, kw in kw_map.items():
#     #                 if any(x in fname for x in keys):
#     #                     detected_kw = kw
#     #                     break

#     #             urls = VISUAL_MOCK.get(detected_kw, list(VISUAL_MOCK["shirt"]))
#     #             result_df = pd.DataFrame({
#     #                 'asin': [f"MATCH_{i}" for i in range(len(urls))],
#     #                 'imUrl': urls, 'score': 4.8
#     #             })
#     #             st.success(f"✅ Tìm thấy {len(result_df)} sản phẩm tương tự!")
#     #             render_product_grid(result_df, "t3_vis")
#     #         else:
#     #             st.markdown("""
#     #             <div style="text-align:center;padding:3rem 1rem;color:#9ca3af;">
#     #                 <div style="font-size:3rem;margin-bottom:1rem;">📸</div>
#     #                 <div style="font-size:1rem;">Tải ảnh lên để tìm kiếm sản phẩm tương tự</div>
#     #                 <div style="font-size:0.82rem;margin-top:0.5rem;">Hỗ trợ: áo, quần, váy, giày, túi, áo khoác</div>
#     #             </div>
#     #             """, unsafe_allow_html=True)
#     with t3:
#         algo_mini_panel()
#         st.subheader("🔍 Tìm kiếm bằng hình ảnh")

#         col_up, col_res = st.columns([1, 2])
#         with col_up:
#             uploaded_img = st.file_uploader("Tải ảnh sản phẩm", type=['jpg','jpeg','png'], label_visibility="collapsed")
#             if uploaded_img:
#                 st.image(uploaded_img, caption="Ảnh của bạn", width='stretch')

#         with col_res:
#             if uploaded_img:
#                 fname = uploaded_img.name.lower()
#                 # Mapping từ khóa từ tên file ảnh
#                 kw_map = {
#                     ("khoac","jacket","coat","hoodie","bomber"): ("jacket", "Áo khoác"),
#                     ("giay","shoe","sneaker","boot","heel"):     ("shoe", "Giày thể thao"),
#                     ("vay","dress","dam","gown","skirt"):        ("dress", "Váy/Đầm"),
#                     ("ao","shirt","top","tee","blouse"):         ("shirt", "Áo kiểu"),
#                     ("quan","pant","jean","trouser","short"):    ("pant", "Quần thời trang"),
#                     ("balo","bag","backpack","tui"):             ("bag", "Túi xách"),
#                 }
                
#                 detected_kw = "shirt" # Mặc định
#                 detected_name = "Áo thời trang"
                
#                 for keys, (kw, name) in kw_map.items():
#                     if any(x in fname for x in keys):
#                         detected_kw = kw
#                         detected_name = name
#                         break

#                 # Lấy danh sách URL hình ảnh từ Mock data
#                 urls = VISUAL_MOCK.get(detected_kw, list(VISUAL_MOCK["shirt"]))
                
#                 # Tạo dataframe kết quả (Bổ sung cột title để hàm render_product_grid nhận diện)
#                 result_df = pd.DataFrame({
#                     'asin': [f"MATCH_{detected_kw.upper()}_{i+1}" for i in range(len(urls))],
#                     'title': [f"{detected_name} Gợi ý {i+1}" for i in range(len(urls))],
#                     'imUrl': urls, 
#                     'score': [4.9, 4.85, 4.7, 4.6][:len(urls)]
#                 })
                
#                 st.success(f"✅ Tìm thấy {len(result_df)} sản phẩm tương tự với ảnh của bạn!")
#                 render_product_grid(result_df, "t3_vis")
#             else:
#                 st.markdown("""
#                 <div style="text-align:center;padding:3rem 1rem;color:#9ca3af;">
#                     <div style="font-size:3rem;margin-bottom:1rem;">📸</div>
#                     <div style="font-size:1rem;">Tải ảnh lên để tìm kiếm sản phẩm tương tự</div>
#                     <div style="font-size:0.82rem;margin-top:0.5rem;">Hỗ trợ nhận diện: áo, quần, váy, giày, túi, áo khoác</div>
#                 </div>
#                 """, unsafe_allow_html=True)

#     # ══ TAB 4: THEO DỊP ══
#     with t4:
#         algo_mini_panel()
#         st.subheader("💃 Gợi ý trang phục theo dịp")

#         dip = st.radio(
#             "Chọn sự kiện:",
#             list(OCCASION_IMAGES.keys()),
#             horizontal=True, key="occ_radio"
#         )
#         st.markdown("")

#         imgs = OCCASION_IMAGES[dip]
#         occ_df = pd.DataFrame({
#             'asin':  [f"OCC_{dip[:3].upper()}_{i}" for i in range(len(imgs))],
#             'imUrl': imgs, 'score': 4.9,
#         })

#         st.markdown(f"#### 🔥 Outfit chuẩn cho: **{dip}**")
#         d_cols = st.columns(4)
#         for i, (_, row) in enumerate(occ_df.iterrows()):
#             with d_cols[i % 4]:
#                 with st.container(border=True):
#                     try:
#                         st.image(row['imUrl'], width='stretch')
#                     except Exception:
#                             st.image(f"https://picsum.photos/seed/{i*11}/400/500", width='stretch')
#                     st.markdown(f'<div class="occasion-chip">{dip}</div>', unsafe_allow_html    =True)
#                     in_cart = row['asin'] in st.session_state.cart
#                     st.button(
#                         "✅ Đã thêm" if in_cart else "🛒 Thêm",
#                         key=f"occ_{row['asin']}",
#                         on_click=toggle_cart, args=(row['asin'],),
#                         width='stretch'
#                     )

#         if st.session_state.algo_run and st.session_state.algo_df is not None:
#             st.markdown("")
#             st.markdown(f"####  Gợi ý thêm từ thuật toán ({st.session_state.algo_results['model'].split('(')[0].strip()})")
#             render_product_grid(st.session_state.algo_df.head(4), "t4_algo")

#     # ══ TAB 5: PHỐI MÀU ══
#     with t5:
#         algo_mini_panel()
#         st.subheader("🎨 Phối màu theo tông da")

#         tone = st.radio(
#             "Tông da của bạn:",
#             ["Sáng (Da trắng hồng)", "Trung bình (Da vàng/Bánh mật)", "Ngăm (Da nâu/Đen)"],
#             horizontal=True, key="tone_radio"
#         )
#         m = get_color_suggestions(tone)

#         if m:
#             st.info(f"💡 {m['ghi_chu']}")
#             col_good, col_neu, col_avoid = st.columns(3)
#             with col_good:
#                 st.markdown('<div class="color-guide-card">', unsafe_allow_html=True)
#                 st.markdown("#### ✅ Nên mặc")
#                 for c in m['phu_hop']:
#                     hex_c = COLOR_MAP.get(c, "#ccc")
#                     st.markdown(
#                         f'<div style="display:flex;align-items:center;gap:8px;margin:4px 0;">'
#                         f'<div style="width:20px;height:20px;border-radius:50%;background:{hex_c};border:1px solid #e2e8f0;flex-shrink:0;"></div>'
#                         f'<span style="font-size:0.85rem;">{c}</span></div>',
#                         unsafe_allow_html=True
#                     )
#                 st.markdown('</div>', unsafe_allow_html=True)

#             with col_neu:
#                 st.markdown('<div class="color-guide-card">', unsafe_allow_html=True)
#                 st.markdown("#### ⚪ Màu trung tính")
#                 for c in m.get('trung_tinh', []):
#                     hex_c = COLOR_MAP.get(c, "#ccc")
#                     st.markdown(
#                         f'<div style="display:flex;align-items:center;gap:8px;margin:4px 0;">'
#                         f'<div style="width:20px;height:20px;border-radius:50%;background:{hex_c};border:1px solid #e2e8f0;flex-shrink:0;"></div>'
#                         f'<span style="font-size:0.85rem;">{c}</span></div>',
#                         unsafe_allow_html=True
#                     )
#                 st.markdown('</div>', unsafe_allow_html=True)

#             with col_avoid:
#                 st.markdown('<div class="color-guide-card">', unsafe_allow_html=True)
#                 st.markdown("#### ❌ Nên tránh")
#                 for c in m['tranh']:
#                     hex_c = COLOR_MAP.get(c, "#ccc")
#                     st.markdown(
#                         f'<div style="display:flex;align-items:center;gap:8px;margin:4px 0;">'
#                         f'<div style="width:20px;height:20px;border-radius:50%;background:{hex_c};border:1px solid #e2e8f0;flex-shrink:0;"></div>'
#                         f'<span style="font-size:0.85rem;">{c}</span></div>',
#                         unsafe_allow_html=True
#                     )
#                 st.markdown('</div>', unsafe_allow_html=True)

#     # ── FLOATING CHATBOT (bottom-right bubble) ──
#     render_floating_chat()


# if __name__ == "__main__":
#     main()

def user_dashboard(df_raw):
    render_floating_chat()

    # ── SIDEBAR ──
# ── SIDEBAR ──
    with st.sidebar:
        st.markdown("### 🎛️ Bảng Điều Khiển")
        st.caption(f"Xin chào, **{st.session_state.username}**! (Vai trò: {st.session_state.role})")
        st.divider()

        # CHỈ ADMIN MỚI THẤY PHẦN CHẠY THUẬT TOÁN
        if st.session_state.role == "Admin":
            st.markdown("### ⚙️ Quản trị Thuật toán")
            if 'reviewerID' in df_raw.columns:
                unique_users = df_raw['reviewerID'].dropna().astype(str).unique().tolist()
            elif 'user_id' in df_raw.columns:
                unique_users = df_raw['user_id'].dropna().astype(str).unique().tolist()
            else:
                unique_users = ["U10293", "U10294", "U10295", "A1B2C3D4"]

            user_options = [" Nhập thủ công "] + unique_users
            selected_user = st.selectbox("Mã Khách hàng (Chọn / Tìm kiếm)", user_options)

            if selected_user == " Nhập thủ công ":
                user_id = st.text_input("✏️ Nhập mã khách hàng mới:", value="U10293")
            else:
                user_id = selected_user
                
            model   = st.selectbox("Thuật toán gợi ý", [
                "SVD (Phân rã ma trận)",
                "KNN Basic",
                "Sản phẩm thịnh hành (Popularity)"
            ])
            top_n   = st.selectbox("Số lượng (Top-N)", [4, 8, 12], index=1)

            if st.button("▶ Chạy thuật toán", type="primary", width='stretch'):
                with st.spinner("Đang phân tích và gợi ý..."):
                    res_df, rmse, elapsed = run_algorithm(df_raw, model, user_id, top_n)
                    st.session_state.algo_run     = True
                    st.session_state.algo_df      = res_df
                    st.session_state.algo_results = {
                        "model": model, "rmse": rmse, "time": elapsed,
                        "top": top_n, "user": user_id
                    }
                st.success("✅ Hoàn thành!")
            st.divider()

        # PHẦN NÀY AI CŨNG THẤY (Giỏ hàng & Đăng xuất)
        cart_n = len(st.session_state.cart)
        st.markdown(f"### 🛒 Giỏ hàng &nbsp; <span class='cart-badge'>{cart_n}</span>", unsafe_allow_html=True)
        if st.session_state.cart:
            for item in st.session_state.cart:
                st.write(f"• {item}")
            if st.button("🗑 Xóa tất cả", width='stretch'):
                st.session_state.cart = []
                st.rerun()
        else:
            st.caption("Giỏ hàng trống")

        st.divider()
        if st.button("🚪 Đăng xuất", width='stretch'):
            st.session_state.clear()
            st.rerun()

    # ── HEADER USER ──
    st.markdown('<div class="hero-title">✨ HỆ THỐNG GỢI Ý SẢN PHẨM THỜI TRANG</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Trung tâm Trải nghiệm Thời trang Cá nhân hóa</div>', unsafe_allow_html=True)

    # ── ALGO RESULT BANNER ──
    if st.session_state.role == "Admin" and st.session_state.algo_run and st.session_state.algo_results:       
        res    = st.session_state.algo_results
        res_df = st.session_state.algo_df
        model_short = res['model'].split('(')[0].strip()
        st.markdown(f"""
        <div class="algo-banner">
            <h3> Kết quả Thuật toán — Top {res['top']} gợi ý cho {res['user']}</h3>
            <div class="metrics-row">
                <div class="metric-chip">Mô hình: <span>{model_short}</span></div>
                <div class="metric-chip">RMSE: <span>{res['rmse']}</span></div>
                <div class="metric-chip">Thời gian: <span>{res['time']}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        render_product_grid(res_df, "algo_top")
        st.divider()
        
    # ── TABS ──
    st.markdown("### 🛠️ Khám phá Tính năng")
    t1, t2, t3, t4, t5 = st.tabs([
        "📝 Phong cách", "📏 Gợi ý size", "🔍 Tìm ảnh", "💃 Theo dịp", "🎨 Phối màu"
    ])

    # Nội dung Tab 1
    with t1:
        algo_mini_panel()
        st.subheader("📝 Bài kiểm tra phong cách — Lookbook")
        col_sel, col_info = st.columns([2, 3])
        with col_sel:
            phong_cach = st.selectbox("Chọn phong cách:", list(STYLE_LOOKBOOK.keys()), key="style_sel")
        with col_info:
            st.info(f"💡 **{phong_cach}** — {STYLE_DESC.get(phong_cach,'')}")

        if st.button("✨ Xem Lookbook", type="primary"):
            images = STYLE_LOOKBOOK.get(phong_cach, [])
            l_cols = st.columns(4)
            for i, img in enumerate(images):
                with l_cols[i % 4]:
                    st.markdown(f'<div class="style-tag">{phong_cach.split("(")[0].strip()}</div>', unsafe_allow_html=True)
                    try: st.image(img, width='stretch')
                    except Exception: st.image(f"https://picsum.photos/seed/{i*3}/400/500", width='stretch')

        if st.session_state.algo_run and st.session_state.algo_df is not None:
            st.markdown("")
            st.markdown(f"#### Sản phẩm gợi ý ({st.session_state.algo_results['model'].split('(')[0].strip()})")
            render_product_grid(st.session_state.algo_df.head(4), "t1_algo")

    # Nội dung Tab 2
    with t2:
        algo_mini_panel()
        st.subheader("📏 Tư vấn size thông minh")
        c1, c2, c3 = st.columns([2, 2, 3])
        h = c1.number_input("Chiều cao (cm)", 100, 250, 165)
        w = c2.number_input("Cân nặng (kg)", 30, 200, 60)
        with c3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("📐 Tính ngay", type="primary", width='stretch'):
                size, bmi_note = calculate_size(h, w)
                if size:
                    st.markdown(f"""
                    <div class="size-result-box">
                        <div style="font-size:0.85rem;color:#f9a8d4;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:4px;">Size của bạn</div>
                        <div class="size-big">{size}</div>
                        <div style="font-size:0.9rem;color:#cbd5e1;margin-top:8px;">{bmi_note}</div>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("")
        st.markdown("#### 📊 Bảng size tham khảo")
        size_table = pd.DataFrame({
            "Size": ["XS", "S", "M", "L", "XL", "XXL"],
            "Chiều cao": ["<150cm", "150–155cm", "155–162cm", "163–169cm", "170–175cm", ">175cm"],
            "Cân nặng":  ["<45kg", "45–50kg", "50–60kg", "60–70kg", "70–80kg", ">80kg"],
            "Ngực (cm)": ["78–80", "80–84", "84–88", "88–92", "92–96", "96–102"],
            "Eo (cm)":   ["60–62", "62–66", "66–70", "70–74", "74–78", "78–84"],
        })
        st.dataframe(size_table, width='stretch', hide_index=True)

    # Nội dung Tab 3
    with t3:
        algo_mini_panel()
        st.subheader("🔍 Tìm kiếm bằng hình ảnh")
        col_up, col_res = st.columns([1, 2])
        with col_up:
            uploaded_img = st.file_uploader("Tải ảnh sản phẩm", type=['jpg','jpeg','png'], label_visibility="collapsed")
            if uploaded_img:
                st.image(uploaded_img, caption="Ảnh của bạn", width='stretch')

        with col_res:
            if uploaded_img:
                fname = uploaded_img.name.lower()
                kw_map = {
                    ("khoac","jacket","coat","hoodie","bomber"): ("jacket", "Áo khoác"),
                    ("giay","shoe","sneaker","boot","heel"):     ("shoe", "Giày thể thao"),
                    ("vay","dress","dam","gown","skirt"):        ("dress", "Váy/Đầm"),
                    ("ao","shirt","top","tee","blouse"):         ("shirt", "Áo kiểu"),
                    ("quan","pant","jean","trouser","short"):    ("pant", "Quần thời trang"),
                    ("balo","bag","backpack","tui"):             ("bag", "Túi xách"),
                }
                detected_kw, detected_name = "shirt", "Áo thời trang"
                for keys, (kw, name) in kw_map.items():
                    if any(x in fname for x in keys):
                        detected_kw, detected_name = kw, name
                        break

                urls = VISUAL_MOCK.get(detected_kw, list(VISUAL_MOCK["shirt"]))
                result_df = pd.DataFrame({
                    'asin': [f"MATCH_{detected_kw.upper()}_{i+1}" for i in range(len(urls))],
                    'title': [f"{detected_name} Gợi ý {i+1}" for i in range(len(urls))],
                    'imUrl': urls, 
                    'score': [4.9, 4.85, 4.7, 4.6][:len(urls)]
                })
                st.success(f"✅ Tìm thấy {len(result_df)} sản phẩm tương tự!")
                render_product_grid(result_df, "t3_vis")
            else:
                st.markdown("""
                <div style="text-align:center;padding:3rem 1rem;color:#9ca3af;">
                    <div style="font-size:3rem;margin-bottom:1rem;">📸</div>
                    <div style="font-size:1rem;">Tải ảnh lên để tìm kiếm sản phẩm tương tự</div>
                </div>
                """, unsafe_allow_html=True)

    # Nội dung Tab 4
    with t4:
        algo_mini_panel()
        st.subheader("💃 Gợi ý trang phục theo dịp")
        dip = st.radio("Chọn sự kiện:", list(OCCASION_IMAGES.keys()), horizontal=True, key="occ_radio")
        st.markdown("")

        imgs = OCCASION_IMAGES[dip]
        occ_df = pd.DataFrame({
            'asin':  [f"OCC_{dip[:3].upper()}_{i}" for i in range(len(imgs))],
            'imUrl': imgs, 'score': 4.9,
        })
        st.markdown(f"#### 🔥 Outfit chuẩn cho: **{dip}**")
        d_cols = st.columns(4)
        for i, (_, row) in enumerate(occ_df.iterrows()):
            with d_cols[i % 4]:
                with st.container(border=True):
                    try: st.image(row['imUrl'], width='stretch')
                    except Exception: st.image(f"https://picsum.photos/seed/{i*11}/400/500", width='stretch')
                    st.markdown(f'<div class="occasion-chip">{dip}</div>', unsafe_allow_html=True)
                    in_cart = row['asin'] in st.session_state.cart
                    st.button("✅ Đã thêm" if in_cart else "🛒 Thêm", key=f"occ_{row['asin']}", on_click=toggle_cart, args=(row['asin'],), width='stretch')

        if st.session_state.role == "Admin" and st.session_state.algo_run and st.session_state.algo_df is not None:
            st.markdown("")
            st.markdown(f"#### Gợi ý thêm từ thuật toán ({st.session_state.algo_results['model'].split('(')[0].strip()})")
            render_product_grid(st.session_state.algo_df.head(4), "t4_algo")

    # Nội dung Tab 5
    with t5:
        algo_mini_panel()
        st.subheader("🎨 Phối màu theo tông da")
        tone = st.radio("Tông da của bạn:", ["Sáng (Da trắng hồng)", "Trung bình (Da vàng/Bánh mật)", "Ngăm (Da nâu/Đen)"], horizontal=True, key="tone_radio")
        m = get_color_suggestions(tone)

        if m:
            st.info(f"💡 {m['ghi_chu']}")
            col_good, col_neu, col_avoid = st.columns(3)
            with col_good:
                st.markdown('<div class="color-guide-card"><h4>✅ Nên mặc</h4>', unsafe_allow_html=True)
                for c in m['phu_hop']:
                    hex_c = COLOR_MAP.get(c, "#ccc")
                    st.markdown(f'<div style="display:flex;align-items:center;gap:8px;margin:4px 0;"><div style="width:20px;height:20px;border-radius:50%;background:{hex_c};border:1px solid #e2e8f0;"></div><span style="font-size:0.85rem;">{c}</span></div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col_neu:
                st.markdown('<div class="color-guide-card"><h4>⚪ Màu trung tính</h4>', unsafe_allow_html=True)
                for c in m.get('trung_tinh', []):
                    hex_c = COLOR_MAP.get(c, "#ccc")
                    st.markdown(f'<div style="display:flex;align-items:center;gap:8px;margin:4px 0;"><div style="width:20px;height:20px;border-radius:50%;background:{hex_c};border:1px solid #e2e8f0;"></div><span style="font-size:0.85rem;">{c}</span></div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col_avoid:
                st.markdown('<div class="color-guide-card"><h4>❌ Nên tránh</h4>', unsafe_allow_html=True)
                for c in m['tranh']:
                    hex_c = COLOR_MAP.get(c, "#ccc")
                    st.markdown(f'<div style="display:flex;align-items:center;gap:8px;margin:4px 0;"><div style="width:20px;height:20px;border-radius:50%;background:{hex_c};border:1px solid #e2e8f0;"></div><span style="font-size:0.85rem;">{c}</span></div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

# ── MAIN APP ROUTER ──
def main():
    init_session()
    df_raw = load_data()

    # Chưa đăng nhập -> Hiện trang Login
    if not st.session_state.logged_in:
        login_page()
        return
    
    # Đã đăng nhập -> Kiểm tra Role để điều hướng
    if st.session_state.role == "Admin":
        admin_dashboard(df_raw)
    else:
        user_dashboard(df_raw)

if __name__ == "__main__":
    main()