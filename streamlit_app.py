import streamlit as st
import pandas as pd
from datetime import datetime

# 網頁基本設定
st.set_page_config(page_title="英國永居(ILR)離境計算器", page_icon="🇬🇧")

st.title("🇬🇧 英國永居 (ILR) 居住要求檢查")
st.markdown("### ✈️ 人手輸入離境紀錄")
st.write("請逐次輸入你離開英國及返回英國的日期。系統會自動扣除首尾兩天（不計入缺勤）。")

# --- 1. 初始化儲存空間 (Session State) ---
if 'my_records' not in st.session_state:
    st.session_state.my_records = []

# --- 2. 人手輸入區 ---
with st.expander("➕ 點擊此處新增一段離境紀錄", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        d_leave = st.date_input("離開英國日期", value=datetime.today(), key="d_leave")
    with col2:
        d_return = st.date_input("返回英國日期", value=datetime.today(), key="d_return")
    
    if st.button("確認加入這段紀錄"):
        if d_return > d_leave:
            # 英國計算規則：離境日及入境日當天不算缺勤
            # 公式：(返回日期 - 離開日期) - 1
            days_out = (d_return - d_leave).days - 1
            days_out = max(0, days_out)
            
            # 存入列表
            st.session_state.my_records.append({
                "離開日期": d_leave,
                "返回日期": d_return,
                "離境天數": days_out
            })
            st.success(f"已成功加入：{days_out} 天")
            st.rerun() # 重新整理頁面以顯示新數據
        else:
            st.error("錯誤：返回日期必須在離開日期之後！")

st.divider()

# --- 3. 顯示結果與表格 ---
if st.session_state.my_records:
    # 轉換成表格
    df = pd.DataFrame(st.session_state.my_records)
    
    # 計算總天數
    total_days = df["離境天數"].sum()
    
    # 顯示統計數據
    st.subheader("📊 當前統計結果")
    
    c1, c2 = st.columns(2)
    with c1:
        st.metric("已登記段數", f"{len(df)} 段")
    with c2:
        if total_days <= 450:
            st.metric("總離境天數", f"{total_days} / 450 日", delta="符合規定", delta_color="normal")
        else:
            st.metric("總離境天數", f"{total_days} / 450 日", delta="已超標！", delta_color="inverse")

    # 顯示明細表格
    st.write("### 📝 離境明細清單")
    st.dataframe(df, use_container_width=True)

    # --- 4. 匯出 CSV 按鈕 ---
    st.write("---")
    # 使用 utf-8-sig 讓 Excel 開啟中文不會亂碼
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 匯出並下載我的紀錄 (CSV)",
        data=csv,
        file_name='uk_ilr_records.csv',
        mime='text/csv',
    )
    
    if st.button("🗑️ 清空所有數據"):
        st.session_state.my_records = []
        st.rerun()
else:
    st.info("💡 目前還沒有任何紀錄。請點擊上方「新增」按鈕開始手動輸入。")

st.divider()
st.caption("提示：根據英國政府規定，申請永居(ILR)時，5年內總離境天數不得超過450日，且任何連續12個月內不得超過180日。")
