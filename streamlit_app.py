import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 網頁基本設定
st.set_page_config(page_title="英國 BNO 永居計算器 (自動清空版)", page_icon="🇬🇧")

# --- 新增：自動清空機制 ---
# 使用一個「啟動標記」來判斷這是否為本次開啟後的第一次運行
if 'app_initialized' not in st.session_state:
    st.session_state.my_records = []  # 確保紀錄是空的
    st.session_state.app_initialized = True
    # 如果有需要，可以在這裡加入 st.rerun() 確保初始狀態乾淨

st.title("🇬🇧 英國永居 (ILR) 居住要求檢查")
st.caption("🔒 安全提示：為了保障隱私，每次重新整理或關閉網頁後，所有輸入資料將會自動清空。")

# --- 1. 基礎日期設定 ---
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        visa_grant_date = st.date_input("1. BNO 簽證批核日子", value=datetime(2022, 6, 27))
    with col2:
        entry_uk_date = st.date_input("2. 首次入境英國日子", value=datetime(2022, 9, 13))

st.divider()

# --- 2. 初始化儲存空間 (如果已經清空則重新建立入境前空白期) ---
if not st.session_state.my_records:
    initial_absence = (entry_uk_date - visa_grant_date).days
    st.session_state.my_records = [{
        "項目": "入境前空白期 (簽證獲批後至入境)",
        "離開日期": visa_grant_date,
        "返回日期": entry_uk_date,
        "離境天數": initial_absence
    }]

# --- 3. 新增紀錄介面 ---
st.subheader("✈️ 手動新增離境紀錄")
with st.expander("➕ 點擊此處新增一段旅遊紀錄"):
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
                "離境天數": days_out
            })
            st.rerun()

st.divider()

# --- 4. 顯示與編輯紀錄 ---
if st.session_state.my_records:
    st.subheader("📝 紀錄明細清單")
    df = pd.DataFrame(st.session_state.my_records)
    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")
    
    if not edited_df.equals(df):
        st.session_state.my_records = edited_df.to_dict('records')
        st.rerun()

    # --- 5. 關鍵日期計算 (5年與提早28天) ---
    total_days = edited_df["離境天數"].astype(int).sum()
    ilr_full_date = visa_grant_date + timedelta(days=365*5 + 1)
    earliest_apply_date = ilr_full_date - timedelta(days=28)
    
    # 使用當前時間進行倒數 (假設今天是 2026-03-27)
    today = datetime.now().date()
    days_to_go = (earliest_apply_date - today).days

    st.divider()
    st.subheader("📅 申請時間軸與倒數")
    
    c_a, c_b = st.columns(2)
    with c_a:
        st.info(f"📍 **5年居住屆滿日**：\n{ilr_full_date}")
    with c_b:
        st.success(f"🚀 **最早可申請日期 (提早28天)**：\n{earliest_apply_date}")

    if days_to_go > 0:
        st.markdown(f"### ⏳ 距離最早申請日還有：**{days_to_go}** 天")
    else:
        st.balloons()
        st.success("🎉 你現在已經進入申請範圍！")

    # --- 6. 統計結果 ---
    st.subheader("📊 資格審查結果")
    col_metric1, col_metric2 = st.columns(2)
    with col_metric1:
        st.metric("總離境天數", f"{total_days} / 450 日")
    with col_metric2:
        status = "✅ 符合要求" if total_days <= 450 else "❌ 已超標"
        st.metric("狀態", status)

    # 匯出與手動清空按鈕
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        csv = edited_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 匯出 CSV 紀錄", data=csv, file_name='uk_ilr_report.csv')
    with c_btn2:
        if st.button("🗑️ 立即清空所有資料並登出"):
            st.session_state.my_records = []
            st.rerun()
