# Updated: 2026-03-27 - Privacy & 28-day Rule Version
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. 網頁基本配置 (必須在最前)
st.set_page_config(page_title="英國 BNO 永居計算器", page_icon="🇬🇧")

# --- 強制清空機制 ---
# 只要用戶重新整理網頁，這段邏輯會偵測到並清空 session
if 'first_run' not in st.session_state:
    st.session_state.clear() # 徹底抹除所有舊資料
    st.session_state['first_run'] = True
    st.session_state.my_records = []

st.title("🇬🇧 英國永居 (ILR) 居住要求檢查")
st.info("🔒 隱私保護已啟動：每次重新整理網頁，所有紀錄將自動清空，不留存於伺服器。")

# --- 2. 基礎日期設定 ---
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        visa_grant_date = st.date_input("1. BNO 簽證批核日子", value=datetime(2022, 6, 27))
    with col2:
        entry_uk_date = st.date_input("2. 首次入境英國日子", value=datetime(2022, 9, 13))

# 初始化第一筆：入境前空白期 (由批核日計起)
if not st.session_state.my_records:
    gap_days = (entry_uk_date - visa_grant_date).days
    st.session_state.my_records = [{
        "項目": "入境前空白期",
        "離開日期": visa_grant_date,
        "返回日期": entry_uk_date,
        "離境天數": int(gap_days)
    }]

st.divider()

# --- 3. 新增紀錄介面 ---
st.subheader("✈️ 手動新增旅遊紀錄")
with st.expander("➕ 點擊此處新增一段離境紀錄"):
    c1, c2 = st.columns(2)
    with c1:
        d_leave = st.date_input("離開英國日期", value=datetime.today())
    with c2:
        d_return = st.date_input("返回英國日期", value=datetime.today())
    
    if st.button("確認加入這段紀錄"):
        if d_return > d_leave:
            # 英國計法：離境日及入境日不計，故為 (回程 - 去程 - 1)
            days_out = (d_return - d_leave).days - 1
            days_out = max(0, days_out)
            st.session_state.my_records.append({
                "項目": f"第 {len(st.session_state.my_records)} 段離境",
                "離開日期": d_leave,
                "返回日期": d_return,
                "離境天數": int(days_out)
            })
            st.rerun()
        else:
            st.error("錯誤：返回日期必須在離開日期之後！")

st.divider()

# --- 4. 顯示與編輯清單 ---
if st.session_state.my_records:
    st.subheader("📝 紀錄明細清單")
    st.caption("💡 可直接在表格中修改日期；選取整行按 Delete 即可取消該項。")
    
    df = pd.DataFrame(st.session_state.my_records)
    
    # 互動式表格：允許刪除行 (num_rows="dynamic")
    edited_df = st.data_editor(
        df, 
        use_container_width=True, 
        num_rows="dynamic",
        column_config={
            "離境天數": st.column_config.NumberColumn(disabled=True) # 鎖定由系統計算
        }
    )
    
    # 同步修改
    if not edited_df.equals(df):
        # 重新計算天數（以防用戶在表格改了日期）
        edited_df['離境天數'] = edited_df.apply(
            lambda row: max(0, (pd.to_datetime(row['返回日期']) - pd.to_datetime(row['離開日期'])).days - 1) 
            if pd.notnull(row['離開日期']) and pd.notnull(row['返回日期']) else row['離境天數'], axis=1
        )
        st.session_state.my_records = edited_df.to_dict('records')
        st.rerun()

    # --- 5. 關鍵日期與倒數 ---
    total_days = edited_df["離境天數"].astype(int).sum()
    ilr_full_date = visa_grant_date + timedelta(days=365*5) # 滿5年
    earliest_apply_date = ilr_full_date - timedelta(days=28) # 提早28天
    
    # 倒數計時 (以當前系統時間 2026-03-27 計算)
    today = datetime.now().date()
    days_to_go = (earliest_apply_date - today).days

    st.divider()
    st.subheader("📅 申請時間軸與倒數")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.info(f"📍 **5年居住屆滿日**：\n{ilr_full_date}")
    with col_b:
        st.success(f"🚀 **最早可申請日 (提早28天)**：\n{earliest_apply_date}")

    if days_to_go > 0:
        st.markdown(f"### ⏳ 距離最早申請日還有：**{days_to_go}** 天")
    else:
        st.balloons()
        st.success("🎉 你現在已經符合遞交申請的時間要求！")

    # --- 6. 統計結果 ---
    st.subheader("📊 總結審查")
    c1, c2 = st.columns(2)
    with c1:
        st.metric("累計離境天數 (含入境前)", f"{total_days} / 450 日")
    with c2:
        status = "✅ 符合要求" if total_days <= 450 else "❌ 已超標"
        st.metric("當前狀態", status)

    # 匯出與手動抹除
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        csv = edited_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 匯出並下載 CSV", data=csv, file_name='ilr_report.csv')
    with btn_col2:
        if st.button("🚨 立即抹除並登出"):
            st.session_state.clear()
            st.rerun()
else:
    st.info("請開始輸入資料。")
