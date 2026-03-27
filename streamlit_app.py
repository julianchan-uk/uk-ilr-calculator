import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. 網頁配置
st.set_page_config(page_title="英國 BNO 永居計算器", page_icon="🇬🇧")

# --- 終極重置邏輯 ---
# 檢查 URL 參數或使用一個手動開關來強制重置
if 'kill_switch' not in st.session_state:
    st.session_state.clear()
    st.session_state['kill_switch'] = True
    st.session_state.my_records = []

st.title("🇬🇧 英國永居 (ILR) 居住要求檢查")
st.markdown("---")

# --- 2. 基礎日期設定 ---
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        visa_grant_date = st.date_input("1. BNO 簽證批核日子", value=datetime(2022, 6, 27))
    with col2:
        entry_uk_date = st.date_input("2. 首次入境英國日子", value=datetime(2022, 9, 13))

# 初始化第一筆：入境前空白期
if not st.session_state.my_records:
    gap_days = (entry_uk_date - visa_grant_date).days
    st.session_state.my_records = [{
        "項目": "入境前空白期",
        "離開日期": visa_grant_date,
        "返回日期": entry_uk_date,
        "離境天數": int(gap_days)
    }]

# --- 3. 新增紀錄介面 ---
st.subheader("✈️ 手動新增旅遊紀錄")
with st.expander("➕ 點擊此處新增紀錄"):
    c1, c2 = st.columns(2)
    with c1:
        d_leave = st.date_input("離開英國日期", value=datetime.today())
    with c2:
        d_return = st.date_input("返回英國日期", value=datetime.today())
    
    if st.button("確認加入"):
        if d_return > d_leave:
            days_out = (d_return - d_leave).days - 1
            st.session_state.my_records.append({
                "項目": f"第 {len(st.session_state.my_records)} 段離境",
                "離開日期": d_leave, "返回日期": d_return, "離境天數": int(max(0, days_out))
            })
            st.rerun()

# --- 4. 顯示與管理清單 ---
if st.session_state.my_records:
    df = pd.DataFrame(st.session_state.my_records)
    st.subheader("📝 紀錄明細")
    
    # 使用 data_editor
    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")
    
    if not edited_df.equals(df):
        st.session_state.my_records = edited_df.to_dict('records')
        st.rerun()

    # --- 5. 計算與倒數 ---
    total_days = edited_df["離境天數"].astype(int).sum()
    ilr_date = visa_grant_date + timedelta(days=365*5)
    apply_date = ilr_date - timedelta(days=28)
    
    # 強制使用 2026-03-27 作為今天進行倒數
    today = datetime(2026, 3, 27).date()
    days_to_go = (apply_date - today).days

    st.info(f"📍 5年屆滿：{ilr_date} | 🚀 最早申請：{apply_date}")
    
    if days_to_go > 0:
        st.metric("⏳ 距離最早申請日", f"{days_to_go} 天")
    else:
        st.success("🎉 已可申請！")

    st.metric("📊 總離境天數", f"{total_days} / 450 日")

    # --- 6. 徹底清空按鈕 (暴力清除) ---
    st.write("---")
    if st.button("🚨 徹底清空所有舊資料 (強制重置)", type="primary"):
        st.session_state.clear()
        st.cache_data.clear() # 清除所有緩存
        st.rerun()
