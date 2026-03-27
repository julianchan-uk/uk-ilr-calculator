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
        # 根據用戶之前的輸入，預設為 2022-06-27
        visa_grant_date = st.date_input("1. BNO 簽證批核日子", value=datetime(2022, 6, 27))
    with col2:
        # 根據用戶之前的輸入，預設為 2022-09-13
        entry_uk_date = st.date_input("2. 首次入境英國日子", value=datetime(2022, 9, 13))

st.divider()

# --- 2. 初始化儲存空間 ---
if 'my_records' not in st.session_state:
    # 自動加入第一段「入境前空白期」
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
        else:
            st.error("返回日期必須在離開日期之後！")

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
    # 滿 5 年日期 (由批核日計)
    ilr_full_date = visa_grant_date + timedelta(days=365*5 + 1) # 加1天處理閏年或邊界
    # 提早 28 天日期
    earliest_apply_date = ilr_full_date - timedelta(days=28)
    
    # 倒數計時
    today = datetime.now().date()
    days_to_go = (earliest_apply_date - today).days

    st.divider()
    st.subheader("📅 申請時間軸與倒數")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.info(f"📍 **5年居住屆滿日**：\n{ilr_full_date}")
    with col_b:
        st.success(f"🚀 **最早可申請日期 (提早28天)**：\n{earliest_apply_date}")

    if days_to_go > 0:
        st.markdown(f"### ⏳ 距離最早申請日還有：**{days_to_go}** 天")
        st.progress(min(100, max(0, (1825 - days_to_go) / 1825)), text="5年長征進度")
    else:
        st.balloons()
        st.success("🎉 你現在已經進入「最早申請日」範圍！可以準備遞交申請了。")

    # --- 6. 統計結果 ---
    st.subheader("📊 資格審查結果")
    c1, c2 = st.columns(2)
    with c1:
        st.metric("總離境天數 (含入境前)", f"{total_days} / 450 日")
    with c2:
        status = "✅ 符合要求" if total_days <= 450 else "❌ 已超標"
        st.metric("狀態", status)

    # 匯出按鈕
    csv = edited_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 匯出完整 CSV 紀錄", data=csv, file_name='uk_ilr_final_report.csv')

else:
    st.info("目前沒有紀錄。")
