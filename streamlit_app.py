import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="英國永居(ILR)日期計算器", page_icon="🇬🇧")

st.title("🇬🇧 英國永居 (ILR) 專業計算器")
st.write("支援手動輸入或上傳 CSV 檔案進行計算")

# --- 1. 基礎日期設定 ---
col1, col2 = st.columns(2)
with col1:
    visa_date = st.date_input("BNO 簽證批核日子", value=datetime(2021, 1, 31))
with col2:
    entry_date = st.date_input("首次入境英國日子", value=datetime(2021, 3, 1))

st.divider()

# --- 2. CSV 匯出/匯入功能 ---
st.subheader("📁 匯入離境紀錄 (CSV)")
st.caption("CSV 格式要求：需包含 'start_date' (離開) 和 'end_date' (返回) 兩欄，日期格式如 2023-01-01")

uploaded_file = st.file_uploader("選擇你的 CSV 檔案", type="csv")

trips = []

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    # 將文字轉為日期格式
    df['start_date'] = pd.to_datetime(df['start_date']).dt.date
    df['end_date'] = pd.to_datetime(df['end_date']).dt.date
    
    # 計算每一段的天數 (回程 - 去程 - 1)
    for index, row in df.iterrows():
        days = (row['end_date'] - row['start_date']).days - 1
        days = max(0, days)
        trips.append({"leave": row['start_date'], "return": row['end_date'], "days": days})
    st.success(f"成功匯入 {len(trips)} 段紀錄！")

# --- 3. 計算與顯示結果 ---
if trips:
    df_display = pd.DataFrame(trips)
    st.table(df_display) # 顯示表格
    
    total_days = sum(t['days'] for t in trips)
    
    st.divider()
    st.subheader("📊 審查結果")
    
    # 450日規則
    if total_days <= 450:
        st.success(f"✅ 5年總計：{total_days} 日 (符合 450 日要求)")
    else:
        st.error(f"❌ 5年總計：{total_days} 日 (超出 450 日限制！)")

    # 匯出功能：讓使用者也可以把網頁上的結果導出 CSV
    csv = df_display.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 下載計算結果為 CSV",
        data=csv,
        file_name='uk_ilr_calculation.csv',
        mime='text/csv',
    )
