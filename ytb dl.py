import yt_dlp
import streamlit as st

def search_youtube(song_name: str):
    search_opts = {
        'extract_flat': True,
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(search_opts) as ydl:
        info = ydl.extract_info(f"ytsearch5:{song_name}", download=False)
        if not info or 'entries' not in info or not info['entries']:
            return []
        return info['entries']

def download_youtube(url: str, format_choice: str):
    ydl_opts = {
        'outtmpl': '%(title)s.%(ext)s',
        'noplaylist': True,
        'quiet': False, 
    }

    if format_choice == 'mp3':
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    else:
        ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# ===== GIAO DIỆN STREAMLIT =====
st.set_page_config(page_title="YouTube Downloader", page_icon="🎬")

st.title("🎬 Công Cụ Tải YouTube")
st.markdown("Nhập tên bài hát hoặc từ khóa để tìm kiếm và tải xuống Video/Âm thanh.")

# Khởi tạo session state để lưu kết quả tìm kiếm giữa các lần nhấn nút
if 'search_results' not in st.session_state:
    st.session_state.search_results = []

# Nhập từ khóa tìm kiếm
song_name = st.text_input("Nhập tên bài hát bạn muốn tải:")

if st.button("🔍 Tìm kiếm"):
    if song_name.strip():
        with st.spinner("Đang tìm kiếm 5 kết quả tốt nhất..."):
            results = search_youtube(song_name.strip())
            st.session_state.search_results = results
            if not results:
                st.warning("Không tìm thấy kết quả nào.")
    else:
        st.warning("Vui lòng nhập tên bài hát.")

# Hiển thị kết quả (nếu đã tìm kiếm xong và có kết quả)
if st.session_state.search_results:
    st.write("### 📋 Kết quả tìm kiếm")
    
    options = []
    for idx, entry in enumerate(st.session_state.search_results, start=1):
        title = entry.get('title', 'Không có tiêu đề')
        duration = entry.get('duration')
        
        if duration:
            m, s = divmod(duration, 60)
            h, m = divmod(m, 60)
            duration_str = f"{int(h):02d}:{int(m):02d}:{int(s):02d}" if h else f"{int(m):02d}:{int(s):02d}"
        else:
            duration_str = "N/A"
            
        options.append(f"{idx}. {title} (Thời lượng: {duration_str})")
        
    # Dropdown hoặc Radio cho phép người dùng chọn video
    selected_option = st.radio("Chọn video để tải:", options)
    selected_index = options.index(selected_option)
    selected_entry = st.session_state.search_results[selected_index]
    
    # Chọn định dạng
    format_choice = st.radio("Chọn định dạng tải xuống:", ["MP4 (Video)", "MP3 (Chỉ âm thanh)"])
    format_val = 'mp3' if 'MP3' in format_choice else 'mp4'
    
    # Nút tải xuống
    if st.button("⬇️ Tải xuống"):
        video_id = selected_entry.get('id')
        selected_url = f"https://www.youtube.com/watch?v={video_id}"
        
        with st.spinner(f"Đang tiến hành tải: {selected_entry.get('title')}..."):
            try:
                download_youtube(selected_url, format_val)
                st.success(f"✅ Tải xuống hoàn tất! File đã được lưu trong cùng thư mục chạy ứng dụng.")
            except yt_dlp.utils.DownloadError as e:
                st.error(f"Lỗi tải xuống từ yt-dlp: {e}")
            except Exception as e:
                st.error(f"Đã xảy ra lỗi hệ thống không mong muốn: {e}")
