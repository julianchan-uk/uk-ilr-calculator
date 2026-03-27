import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 網頁基本設定
st.set_page_config(page_title="英國 BNO 永居計算器", page_icon="🇬🇧")

st.title("🇬🇧 英國永居 (ILR) 居住要求檢查")
st.markdown("### 📅 重要日期與離境紀錄")

# --- 1. 基礎日期設定 ---
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        visa_grant_date = st.date_input("1. BNO 簽證批核日子", value=datetime(2021, 1, 31))
    with col2:
        entry_uk_date = st.date_input("2. 首次入境英國日子", value=datetime(2021, 3, 1))

st.divider()

# --- 2. 初始化儲存空間 ---
if 'my_records' not in st.session_state:
    st.session_state.my_records = []

# --- 3. 人手逐次輸入離境紀錄 ---
st.subheader("✈️ 離境紀錄 (人手逐次輸入)")
with st.expander("➕ 點擊此處新增一段離境紀錄", expanded=True):
    c1, c2 = st.columns(2)
    with c1:
        d_leave = st.date_input("離開英國日期", value=datetime.today(), key="d_leave")
    with c2:
        d_return = st.date_input("返回英國日期", value=datetime.today(), key="d_return")
    
    if st.button("確認加入這段紀錄"):
        if d_return > d_leave:
            # 英國計算規則：離境日及入境日當天不算缺勤
            days_out = (d_return - d_leave).days - 1
            days_out = max(0, days_out)
            
            st.session_state.my_records.append({
                "項目": f"第 {len(st.session_state.my_records) + 1} 段離境",
                "離開日期": d_leave,
                "返回日期": d_return,
                "離境天數": days_out
            })
            st.success(f"已加入：{days_out} 天")
            st.rerun()
        else:
            st.error("錯誤：返回日期必須在離開日期之後！")

# --- 4. 顯示結果與表格 ---
if st.session_state.my_records:
    df = pd.DataFrame(st.session_state.my_records)
    total_days = df["離境天數"].sum()
    
    st.divider()
    st.subheader("📊 統計結果")
    
    # 計算 5 年後的日期
    ilr_eligible_date = entry_uk_date + timedelta(days=365*5)
    
    st.info(f"💡 你的 5 年居住期預計由 **{entry_uk_date}** 開始計算，直到 **{ilr_eligible_date}**。")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("累計離境天數", f"{total_days} / 450 日")
    with col_b:
        status = "✅ 符合要求" if total_days <= 450 else "❌ 已超標"
        st.metric("狀態", status)

    st.write("### 📝 紀錄明細清單")
    st.dataframe(df, use_container_width=True)

    # --- 5. 匯出 CSV (包含所有資訊) ---
    # 準備匯出的資料：先加入基本資訊行
    base_info = pd.DataFrame([
        {"項目": "BNO 簽證批核日", "離開日期": visa_grant_date, "返回日期": "-", "離境天數": "-"},
        {"項目": "首次入境英國日", "離開日期": entry_uk_date, "返回日期": "-", "離境天數": "-"},
        {"項目": "---", "離開日期": "---", "返回日期": "---", "離境天數": "---"}
    ])
    export_df = pd.concat([base_info, df], ignore_index=True)
    
    csv = export_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 匯出完整紀錄與結果 (CSV)",
        data=csv,
        file_name='uk_ilr_full_report.csv',
        mime='text/csv',
    )
    
    if st.button("🗑️ 清空所有紀錄"):
        st.session_state.my_records = []
        st.rerun()
else:
    st.info("請開始輸入你的離境紀錄。")

st.divider()
st.caption("備註：本工具計算方式僅供參考，正式申請時請以英國內政部(Home Office)最新公佈之規則為準。")
