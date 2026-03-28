import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io

# 1. 基本配置
st.set_page_config(page_title="英國 BNO 永居計算器", page_icon="🇬🇧", layout="centered")

# 初始化 Session State
if 'my_records' not in st.session_state:
    st.session_state.my_records = []

st.title("🇬🇧 英國永居 (ILR) 居住要求檢查")
st.caption("🔒 安全提示：為了保障隱私，每次重新整理或關閉網頁後，所有輸入資料將會自動清空。")

# --- 2. 基礎日期設定 ---
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        visa_date = st.date_input("1. BNO 簽證批核日子", value=datetime(2022, 6, 27))
    with col2:
        entry_date = st.date_input("2. 首次入境英國日子", value=datetime(2022, 9, 13))

# 自動處理「入境前空白期」邏輯
gap_days = (entry_date - visa_date).days
gap_record = {
    "項目": "入境前空白期 (簽證獲批至入境)",
    "離開日期": visa_date,
    "返回日期": entry_date,
    "離境天數": int(max(0, gap_days))
}

if gap_days > 0:
    if not st.session_state.my_records:
        st.session_state.my_records.insert(0, gap_record)
    elif "入境前空白期" in str(st.session_state.my_records[0].get("項目", "")):
        st.session_state.my_records[0] = gap_record

st.divider()

# --- 3. 手動新增紀錄 ---
st.subheader("✈️ 手動新增離境紀錄")
with st.expander("➕ 點擊此處新增一段旅遊紀錄", expanded=True):
    with st.form("add_trip", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            d_l = st.date_input("離開英國日期", value=datetime.today())
        with c2:
            d_r = st.date_input("返回英國日期", value=datetime.today())
        with c3:
            st.write("")
            if st.form_submit_button("加入紀錄"):
                if d_r > d_l:
                    diff = (d_r - d_l).days - 1
                    st.session_state.my_records.append({
                        "項目": f"旅遊紀錄 {len(st.session_state.my_records)}",
                        "離開日期": d_l,
                        "返回日期": d_r,
                        "離境天數": int(max(0, diff))
                    })
                    st.rerun()
                else:
                    st.error("日期無效")

st.divider()

# --- 4. 紀錄明細清單 ---
st.subheader("📝 紀錄明細清單")
if st.session_state.my_records:
    # 顯示表格
    h = st.columns([3, 2, 2, 1, 0.5])
    h[0].write("**項目**"); h[1].write("**離開日期**"); h[2].write("**返回日期**"); h[3].write("**天數**"); h[4].write("")
    
    for idx, r in enumerate(st.session_state.my_records):
        row = st.columns([3, 2, 2, 1, 0.5])
        row[0].write(r["項目"])
        row[1].write(str(r["離開日期"]))
        row[2].write(str(r["返回日期"]))
        row[3].write(str(r["離境天數"]))
        if row[4].button("❌", key=f"del_{idx}"):
            st.session_state.my_records.pop(idx)
            st.rerun()

    # --- 5. 統計與倒數 ---
    total = sum(int(item["離境天數"]) for item in st.session_state.my_records)
    ilr_date = visa_date + timedelta(days=365*5)
    apply_date = ilr_date - timedelta(days=28)
    
    # 使用當前系統時間 2026-03-28 計算倒數
    today_val = datetime(2026, 3, 28).date()
    days_to_go = (apply_date - today_val).days

    st.divider()
    res_c1, res_c2 = st.columns(2)
    with res_c1:
        st.metric("📊 總離境天數", f"{total} / 450 日")
        st.write(f"📍 **5年居住屆滿日：** {ilr_date}")
    with res_c2:
        st.metric("⏳ 距離可申請還有", f"{max(0, days_to_go)} 天")
        st.write(f"🚀 **最早申請日期：** {apply_date}")
else:
    st.info("💡 目前清單為空。您可以從下方「數據管理工具」匯入舊檔案，或手動新增紀錄。")

st.divider()

# --- 6. 數據管理工具格仔 (搬到最底) ---
st.subheader("💾 數據管理工具")
with st.container(border=True):
    m1, m2 = st.columns([1, 1])
    
    with m1:
        st.write("📤 **匯入舊紀錄**")
        uploaded_file = st.file_uploader("選擇之前的 CSV 檔案", type="csv", label_visibility="collapsed")
        if uploaded_file is not None:
            try:
                import_df = pd.read_csv(uploaded_file)
                import_df['離開日期'] = pd.to_datetime(import_df['離開日期']).dt.date
                import_df['返回日期'] = pd.to_datetime(import_df['返回日期']).dt.date
                st.session_state.my_records = import_df.to_dict('records')
                st.rerun()
            except:
                st.error("匯入檔案格式不符")
    
    with m2:
        st.write("📥 **備份目前紀錄**")
        if st.session_state.my_records:
            df_export = pd.DataFrame(st.session_state.my_records)
            df_export['離開日期'] = df_export['離開日期'].apply(lambda x: x.strftime('%Y-%m-%d') if hasattr(x, 'strftime') else str(x))
            df_export['返回日期'] = df_export['返回日期'].apply(lambda x: x.strftime('%Y-%m-%d') if hasattr(x, 'strftime') else str(x))
            csv = df_export.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="下載 CSV 檔案",
                data=csv,
                file_name=f"BNO_Records_{datetime.now().strftime('%Y%m%d')}.csv",
                mime='text/csv',
                use_container_width=True
            )
        else:
            st.info("暫無資料可供匯出")

    if st.button("🚨 清空所有畫面資料", use_container_width=True):
        st.session_state.my_records = []
        st.rerun()
