import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. 基本配置
st.set_page_config(page_title="英國 BNO 永居計算器", page_icon="🇬🇧")

# --- 強制重置邏輯 (確保每次重新整理都清空) ---
if 'my_records' not in st.session_state or st.sidebar.button("🚨 重新開始 (清空所有)"):
    st.session_state.my_records = []
    st.session_state.initialized = True

st.title("🇬🇧 英國永居 (ILR) 居住要求檢查")

# --- 2. 基礎日期設定 ---
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        visa_date = st.date_input("1. BNO 簽證批核日子", value=datetime(2022, 6, 27))
    with col2:
        entry_date = st.date_input("2. 首次入境英國日子", value=datetime(2022, 9, 13))

# 初始化「入境前空白期」
if not st.session_state.my_records:
    gap = (entry_date - visa_date).days
    st.session_state.my_records.append({
        "項目": "入境前空白期",
        "離開日期": visa_date,
        "返回日期": entry_date,
        "離境天數": int(gap)
    })

st.divider()

# --- 3. 手動新增紀錄 ---
st.subheader("✈️ 新增旅遊紀錄")
with st.form("add_form", clear_on_submit=True):
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        d_l = st.date_input("離開英國日期")
    with c2:
        d_r = st.date_input("返回英國日期")
    with c3:
        st.write("") # 為了對齊
        submitted = st.form_submit_button("➕ 加入")
    
    if submitted:
        if d_r > d_l:
            # 英國算法：去程回程當天不算，故減1
            diff = (d_r - d_l).days - 1
            st.session_state.my_records.append({
                "項目": f"旅遊紀錄 {len(st.session_state.my_records)}",
                "離開日期": d_l,
                "返回日期": d_r,
                "離境天數": int(max(0, diff))
            })
            st.rerun()

st.divider()

# --- 4. 紀錄明細與「個別刪除」功能 ---
st.subheader("📝 紀錄明細清單")

if st.session_state.my_records:
    # 建立一個有刪除按鈕的列表
    for idx, record in enumerate(st.session_state.my_records):
        cols = st.columns([3, 2, 2, 1, 1])
        cols[0].write(record["項目"])
        cols[1].write(record["離開日期"])
        cols[2].write(record["返回日期"])
        cols[3].write(f"{record['離境天數']}天")
        
        # 個別取消按鈕
        if cols[4].button("❌", key=f"del_{idx}"):
            st.session_state.my_records.pop(idx)
            st.rerun()

    # --- 5. 數據總計 ---
    total_days = sum(r["離境天數"] for r in st.session_state.my_records)
    
    # 28天規定計算
    ilr_date = visa_date + timedelta(days=365*5)
    apply_date = ilr_date - timedelta(days=28)
    # 以今天日期 2026-03-27 計算倒數
    today = datetime(2026, 3, 27).date()
    days_left = (apply_date - today).days

    st.divider()
    st.subheader("📊 統計結果")
    
    res1, res2 = st.columns(2)
    res1.metric("總離境天數", f"{total_days} / 450 日")
    res2.metric("狀態", "✅ 符合" if total_days <= 450 else "❌ 超標")

    st.success(f"📅 最早申請日期 (提早28天)：**{apply_date}** (還有 {days_left} 天)")

    # 匯出 CSV
    df_export = pd.DataFrame(st.session_state.my_records)
    csv = df_export.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 匯出 CSV", data=csv, file_name='uk_records.csv')
else:
    st.info("目前無紀錄。")
