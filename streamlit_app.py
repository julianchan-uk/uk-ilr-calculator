import streamlit as st

st.set_page_config(page_title="英國永居(ILR)計算器", page_icon="🇬🇧")

st.title("🇬🇧 英國永居 (ILR) 離境天數計算")
st.write("這是一個幫助你檢查是否符合居住要求的工具。")

# 輸入框
total_days = st.number_input("5年內總共離境天數 (上限450日):", min_value=0, value=0)
max_single_year = st.number_input("任何連續12個月內最高離境天數 (上限180日):", min_value=0, value=0)

if st.button("立即檢查"):
    # 邏輯判斷
    if total_days <= 450 and max_single_year <= 180:
        st.success(f"✅ 符合要求！總離境 {total_days} 日，單年最高 {max_single_year} 日。")
        st.balloons() # 撒花特效，增加互動感
    else:
        st.error("❌ 不符合要求。請檢查你的離境紀錄是否超出上限。")

st.info("參考來源：[GOV.UK Indefinite leave to remain](https://www.gov.uk/indefinite-leave-to-remain)")
