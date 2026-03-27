import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. 必須放在最前面：設定網頁並嘗試清空緩存
st.set_page_config(page_title="英國 BNO 永居計算器", page_icon="🇬🇧")

# 強制清除舊有的 session 資料
if 'init' not in st.session_state:
    for key in st.session_state.keys():
        del st.session_state[key]
    st.session_state['init'] = True
    st.session_state.my_records = []

st.title("🇬🇧 英國永居 (ILR) 居住要求檢查")
st.warning("🔒 已啟動隱私保護：每次重新整理或關閉分頁，紀錄將會徹底抹除。")

# --- 2. 基礎日期設定 ---
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        visa_grant_date = st.date_input("1. BNO 簽證批核日子", value=datetime(2022, 6, 27))
    with col2:
        entry_uk_date = st.date_input("2. 首次入境英國日子", value=datetime(2022, 9, 13))

# 如果紀錄是空的，自動初始化第一筆（入境前空白期）
if not st.session_state.my_records:
    initial_absence = (entry_uk_date - visa_grant_date).days
    st.session_state.my_records = [{
        "項目": "入境前空白期 (簽證獲批後至入境)",
        "離開日期": visa_grant_date,
        "返回日期": entry_uk_date,
        "離境天數": initial_absence
    }]

st.divider()

# --- 3. 新增紀錄介面 ---
with st.expander("➕ 點擊新增旅遊紀錄"):
    c1, c2 = st.columns(2)
    with c1:
        d_leave = st.date_input("離開英國日期", value=datetime.today())
    with c2:
        d_return = st.date_input("返回英國日期", value=datetime.today())
    
    if st.button("確認加入紀錄"):
        if d_return > d_leave:
            days_out = (d_return - d_leave).days - 1
            days_out = max(0, days_out)
            st.session_state.my_records.append({
                "項目": f"第 {len(st.session_state.my_records)} 段離境",
                "離開日期": d_leave,
                "返回日期": d_return,
                "離境天數": int(days_out)
            })
            st.rerun()

# --- 4. 顯示與管理清單 ---
if st.session_state.my_records:
    df = pd.DataFrame(st.session_state.my_records)
    
    # 這裡顯示表格
    st.subheader("📝 紀錄明細清單")
    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")

    # 同步數據
    if not edited_df.equals(df):
        st.session_state.my_records = edited_df.to_dict('records')
        st.rerun()

    # --- 5. 倒數器與結果 ---
    total_days = edited_df["離境天數"].astype(int).sum()
    ilr_full_date = visa_grant_date + timedelta(days=365*5 + 1)
    earliest_apply_date = ilr_full_date - timedelta(days=28)
    
    # 獲取 2026-03-27 當前日期
    today_date = datetime(2026, 3, 27).date()
    days_to_go = (earliest_apply_date - today_date).days

    st.divider()
    st.subheader("📅 申請倒數")
    
    ca, cb = st.columns(2)
    with ca:
        st.info(f"📍 5年屆滿日：\n{ilr_full_date}")
    with cb:
        st.success(f"🚀 最早申請日：\n{earliest_apply_date}")

    if days_to_go > 0:
        st.metric("⏳ 距離最早申請日剩餘", f"{days_to_go} 天")
    else:
        st.success("🎉 你已經可以申請了！")

    st.metric("📊 總離境天數", f"{total_days} / 450 日")

    # 徹底清除按鈕
    if st.button("🚨 立即抹除所有數據"):
        st.session_state.clear()
        st.rerun()
