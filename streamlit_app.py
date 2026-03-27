import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 網頁基本設定
st.set_page_config(page_title="英國 BNO 永居計算器", page_icon="🇬🇧")

st.title("🇬🇧 英國永居 (ILR) 居住要求檢查")

# --- 1. 基礎日期設定 ---
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        visa_grant_date = st.date_input("1. BNO 簽證批核日子", value=datetime(2021, 1, 31))
    with col2:
        entry_uk_date = st.date_input("2. 首次入境英國日子", value=datetime(2022, 9, 13))

st.divider()

# --- 2. 初始化儲存空間 ---
if 'my_records' not in st.session_state:
    st.session_state.my_records = []

# --- 3. 人手新增紀錄 ---
st.subheader("✈️ 新增離境紀錄")
with st.expander("➕ 點擊此處新增一段紀錄"):
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
                "離開日期": d_leave,
                "返回日期": d_return,
                "離境天數": days_out
            })
            st.rerun()
        else:
            st.error("返回日期必須在離開日期之後！")

st.divider()

# --- 4. 顯示與編輯紀錄 (關鍵更新：st.data_editor) ---
if st.session_state.my_records:
    st.subheader("📝 紀錄明細清單 (可直接在此刪除或修改)")
    st.caption("💡 提示：點擊行首可以選取，按鍵盤 Delete 可刪除；或直接修改日期。")
    
    # 將資料轉為 DataFrame
    df = pd.DataFrame(st.session_state.my_records)
    
    # 使用 data_editor，並開啟 num_rows="dynamic" 允許用戶刪除行
    edited_df = st.data_editor(
        df, 
        use_container_width=True, 
        num_rows="dynamic",
        column_config={
            "離境天數": st.column_config.NumberColumn(disabled=True) # 鎖定天數由系統計算
        }
    )
    
    # 如果用戶在表格內做了改動，同步回 session_state
    if not edited_df.equals(df):
        # 重新計算天數（以防用戶改了日期）
        edited_df['離境天數'] = edited_df.apply(
            lambda row: max(0, (pd.to_datetime(row['返回日期']) - pd.to_datetime(row['離開日期'])).days - 1) 
            if pd.notnull(row['離開日期']) and pd.notnull(row['返回日期']) else 0, axis=1
        )
        st.session_state.my_records = edited_df.to_dict('records')
        st.rerun()

    # --- 5. 統計結果 ---
    total_days = edited_df["離境天數"].sum()
    ilr_eligible_date = entry_uk_date + timedelta(days=365*5)
    
    st.info(f"💡 你的 5 年居住期預計由 **{entry_uk_date}** 開始，直到 **{ilr_eligible_date}**。")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("累計離境天數", f"{int(total_days)} / 450 日")
    with col_b:
        status = "✅ 符合要求" if total_days <= 450 else "❌ 已超標"
        st.metric("狀態", status)

    # --- 6. 匯出 CSV ---
    csv = edited_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 匯出當前清單 (CSV)",
        data=csv,
        file_name='uk_ilr_updated_records.csv',
        mime='text/csv',
    )
    
    if st.button("🗑️ 清空所有紀錄"):
        st.session_state.my_records = []
        st.rerun()
else:
    st.info("目前沒有紀錄。")
