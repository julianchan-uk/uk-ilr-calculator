import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="英國 BNO 永居計算器", page_icon="🇬🇧")
st.title(BNO 英國永居 (ILR) 居住要求檢查")

# --- 1. 基礎日期設定 ---
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        visa_grant_date = st.date_input("1. BNO 簽證批核日子", value=datetime(2022, 6, 27))
    with col2:
        entry_uk_date = st.date_input("2. 首次入境英國日子", value=datetime(2022, 9, 13))

st.divider()

# --- 2. 初始化儲存空間 ---
if 'my_records' not in st.session_state:
    # 自動加入第一段「入境前離境」紀錄
    initial_absence = (entry_uk_date - visa_grant_date).days
    st.session_state.my_records = [{
        "項目": "入境前空白期",
        "離開日期": visa_grant_date,
        "返回日期": entry_uk_date,
        "離境天數": initial_absence
    }]

# --- 3. 新增紀錄介面 ---
st.subheader("✈️ 手動新增離境紀錄")
with st.expander("➕ 點擊新增旅遊紀錄"):
    c1, c2 = st.columns(2)
    with c1:
        d_leave = st.date_input("離開英國日期", value=datetime.today())
    with c2:
        d_return = st.date_input("返回英國日期", value=datetime.today())
    
    if st.button("確認加入"):
        if d_return > d_leave:
            days_out = (d_return - d_leave).days - 1
            days_out = max(0, days_out)
            st.session_state.my_records.append({
                "項目": f"第 {len(st.session_state.my_records)} 段離境",
                "離開日期": d_leave,
                "返回日期": d_return,
                "離境天數": days_out
            })
            st.rerun()

st.divider()

# --- 4. 顯示與管理清單 ---
if st.session_state.my_records:
    df = pd.DataFrame(st.session_state.my_records)
    
    # 允許逐項修改與刪除
    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")
    
    # 同步回 session_state (若有手動刪除或修改)
    if not edited_df.equals(df):
        st.session_state.my_records = edited_df.to_dict('records')
        st.rerun()

    # --- 5. 最終統計 (以批核日計五年) ---
    total_days = edited_df["離境天數"].astype(int).sum()
    ilr_date = visa_grant_date + timedelta(days=365*5) # 由批核日加五年
    
    st.info(f"💡 你的 5 年資格期由 **{visa_grant_date}** 開始，預計於 **{ilr_date}** 屆滿。")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("總離境天數 (含入境前)", f"{total_days} / 450 日")
    with col_b:
        status = "✅ 符合要求" if total_days <= 450 else "❌ 已超標"
        st.metric("狀態", status)

    # 匯出按鈕
    csv = edited_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 匯出 CSV 紀錄", data=csv, file_name='uk_ilr_report.csv')
