import streamlit as st
import yt_dlp
import os

st.set_page_config(page_title="YouTube 下載器", page_icon="🎥")
st.title("🎥 YouTube 影片下載工具")
st.caption("輸入 YouTube 網址，解析後即可下載影片。")

url = st.text_input("請貼上 YouTube 影片網址 (例如 https://www.youtube.com/watch?v=...):")

if url:
    try:
        # 設定下載選項
        save_path = "downloaded_video.mp4"
        ydl_opts = {
            'format': 'best', 
            'outtmpl': save_path,
            'quiet': True
        }

        with st.spinner('正在讀取影片資訊...'):
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'video')
                
        # 提供預覽與下載
        if os.path.exists(save_path):
            with open(save_path, "rb") as file:
                st.video(file)
                st.download_button(
                    label="📥 點擊下載影片",
                    data=file,
                    file_name=f"{title}.mp4",
                    mime="video/mp4"
                )
            # 刪除伺服器上的暫存檔
            os.remove(save_path)

    except Exception as e:
        st.error(f"下載失敗。原因：{e}")
        st.info("小提示：Streamlit Cloud 的 IP 有時會被 YouTube 封鎖，如果多次失敗請稍後再試。")
