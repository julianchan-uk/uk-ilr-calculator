import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. 基本配置
st.set_page_config(page_title="英國 BNO 永居計算器", page_icon="🇬🇧")

# --- 初始化 Session State ---
if 'my_records' not in st.session_state:
    st.session_state.my_records = []

# 側欄清空按鈕
if st.sidebar.button("🚨 重新開始 (清空所有資料)"):
    st.session_state.my_records = []
    st.rerun()

st.title("🇬🇧 英國永居 (ILR) 居住要求檢查")

# --- 2. 基礎日期設定 ---
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        # 預設為今天，方便你手動輸入
        visa_date = st.date_input("1. BNO 簽證批核日子", value=datetime.today())
    with col2:
        entry_date = st.date_input("2. 首次入境英國日子", value=datetime.today())

# --- 自動更新「入境前空白期」邏輯 ---
# 計算批核到入境的天數
gap_days = (entry_date - visa_date).days
gap_record = {
    "項目": "入境前空白期 (簽證獲批至入境)",
    "離開日期": visa_date,
    "返回日期": entry_date,
    "離境天數": int(max(0, gap_days))
}

# 確保清單第一項永遠是這段空白期
if gap_days > 0:
    if not st.session_state.my_records:
        st.session_state.my_records.insert(0, gap_record)
    else:
        # 如果第一項已經是空白期，則更新它
        if "入境前空白期" in st.session_state.my_records[0]["項目"]:
            st.session_state.my_records[0] = gap_record
        else:
            st.session_state.my_records.insert(0, gap_record)
elif gap_days <= 0 and st.session_state.my_records:
    # 如果日期重疊，移除空白期
    if "入境前空白期" in st.session_state.my_records[0]["項目"]:
        st.session_state.my_records.pop(0)

st.divider()

# --- 3. 手動新增紀錄 ---
st.subheader("✈️ 新增旅遊紀錄")
with st.form("add_form", clear_on_submit=True):
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        d_l = st.date_input("離開英國日期", value=datetime.today())
    with c2:
        d_r = st.date_input("返回英國日期", value=datetime.today())
    with c3:
        st.write("") 
        submitted = st.form_submit_button("➕ 加入")
    
    if submitted:
        if d_r > d_l:
            # 英國計法：去程回程當天不算
            diff = (d_r - d_l).days - 1
            st.session_state.my_records.append({
                "項目": f"旅遊紀錄 {len(st.session_state.my_records)}",
                "離開日期": d_l,
                "返回日期": d_r,
                "離境天數": int(max(0, diff))
            })
            st.rerun()

st.divider()

# --- 4. 紀錄明細清單 (含個別刪除) ---
st.subheader("📝 紀錄明細清單")

if st.session_state.my_records:
    # 表頭
    h_col = st.columns([3, 2, 2, 1, 1])
    h_col[0].write("**項目**")
    h_col[1].write("**離開日期**")
    h_col[2].write("**返回日期**")
    h_col[3].write("**天數**")
    h_col[4].write("**操作**")

    for idx, record in enumerate(st.session_state.my_records):
        row_cols = st.columns([3, 2, 2, 1, 1])
        row_cols[0].write(record["項目"])
        row_cols[1].write(record["離開日期"].strftime('%Y-%m-%d'))
        row_cols[2].write(record["返回日期"].strftime('%Y-%m-%d'))
        row_cols[3].write(f"{record['離境天數']}")
        
        # 個別刪除按鈕 (入境前空白期不建議刪除，但如果你想，這裡也保留按鈕)
        if row_cols[4].button("❌", key=f"del_{idx}"):
            st.session_state.my_records.pop(idx)
            st.rerun()

    # --- 5. 數據統計與倒數 ---
    total_days = sum(r["離境天數"] for r in st.session_state.my_records)
    ilr_date = visa_date + timedelta(days=365*5)
    apply_date = ilr_date - timedelta(days=28)
    
    # 使用當前系統時間 2026-03-28
    today_now = datetime.now().date()
    days_left = (apply_date - today_now).days

    st.divider()
    st.subheader("📊 統計結果")
    
    res1, res2 = st.columns(2)
    res1.metric("總離境天數 (含入境前)", f"{total_days} / 450 日")
    res2.metric("狀態", "✅ 符合要求" if total_days <= 450 else "❌ 已超標")

    st.success(f"📅 滿 5 年日期：**{ilr_date}**")
    st.warning(f"🚀 最早申請日期 (提早 28 天)：**{apply_date}** (還有 **{max(0, days_left)}** 天)")

    # 匯出 CSV
    df_export = pd.DataFrame(st.session_state.my_records)
    csv = df_export.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 匯出完整 CSV 紀錄", data=csv, file_name='uk_ilr_report.csv')
else:
    st.info("💡 請輸入資料。")
