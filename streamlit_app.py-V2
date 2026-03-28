import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="英國 BNO 永居計算器", page_icon="🇬🇧")

# 初始化數據
if 'my_records' not in st.session_state:
    st.session_state.my_records = []

# 側欄清空功能
if st.sidebar.button("🚨 重新開始 (清空所有資料)"):
    st.session_state.my_records = []
    st.rerun()

st.title("🇬🇧 英國永居 (ILR) 居住要求檢查")
st.warning("🔒 每次重新整理網頁，所有輸入資料將會自動清空。")

# --- 1. 基礎日期設定 ---
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        visa_date = st.date_input("1. BNO 簽證批核日子", value=datetime.today())
    with col2:
        entry_date = st.date_input("2. 首次入境英國日子", value=datetime.today())

# --- 自動處理「入境前空白期」 ---
gap_days = (entry_date - visa_date).days
gap_record = {
    "項目": "入境前空白期 (簽證獲批至入境)",
    "離開日期": visa_date,
    "返回日期": entry_date,
    "離境天數": int(max(0, gap_days))
}

# 確保空白期永遠在清單第一項
if gap_days > 0:
    if not st.session_state.my_records:
        st.session_state.my_records.insert(0, gap_record)
    elif "入境前空白期" in st.session_state.my_records[0]["項目"]:
        st.session_state.my_records[0] = gap_record
    else:
        st.session_state.my_records.insert(0, gap_record)

st.divider()

# --- 2. 新增旅遊紀錄表單 ---
st.subheader("✈️ 新增旅遊紀錄")
with st.form("add_trip", clear_on_submit=True):
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        d_l = st.date_input("離開英國日期", value=datetime.today())
    with c2:
        d_r = st.date_input("返回英國日期", value=datetime.today())
    with c3:
        st.write("")
        if st.form_submit_button("➕ 加入"):
            if d_r > d_l:
                diff = (d_r - d_l).days - 1
                st.session_state.my_records.append({
                    "項目": f"旅遊紀錄 {len(st.session_state.my_records)}",
                    "離開日期": d_l,
                    "返回日期": d_r,
                    "離境天數": int(max(0, diff))
                })
                st.rerun()

# --- 3. 顯示紀錄清單 (帶有刪除按鈕) ---
st.subheader("📝 紀錄明細清單")
if st.session_state.my_records:
    # 建立表頭
    h = st.columns([3, 2, 2, 1, 1])
    h[0].write("**項目**"); h[1].write("**離開**"); h[2].write("**返回**"); h[3].write("**天數**"); h[4].write("**操作**")
    
    for idx, r in enumerate(st.session_state.my_records):
        cols = st.columns([3, 2, 2, 1, 1])
        cols[0].write(r["項目"])
        cols[1].write(r["離開日期"].strftime('%Y-%m-%d'))
        cols[2].write(r["返回日期"].strftime('%Y-%m-%d'))
        cols[3].write(f"{r['離境天數']}")
        if cols[4].button("❌", key=f"btn_{idx}"):
            st.session_state.my_records.pop(idx)
            st.rerun()

    # --- 4. 統計與計算 ---
    total = sum(item["離境天數"] for item in st.session_state.my_records)
    ilr_date = visa_date + timedelta(days=365*5)
    apply_date = ilr_date - timedelta(days=28)
    
    # 使用今日日期 2026-03-28 計算倒數
    today_val = datetime(2026, 3, 28).date()
    days_to_go = (apply_date - today_val).days

    st.divider()
    st.metric("📊 總離境天數", f"{total} / 450 日")
    st.info(f"📍 5年屆滿日：{ilr_date}")
    st.success(f"🚀 最早可申請日 (提早28天)：{apply_date} (還有 {max(0, days_to_go)} 天)")
else:
    st.info("目前尚無資料。")
