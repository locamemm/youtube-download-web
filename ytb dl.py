import yt_dlp
import streamlit as st
import os
import tempfile

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

def download_youtube(url: str, format_choice: str, cookie_path: str = None):
    temp_dir = tempfile.mkdtemp()
    ydl_opts = {
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'quiet': False,
        # Khắc phục lỗi 403: Dùng client ios/tv vì android hiện bị YouTube chặn gắt gao hơn
        'extractor_args': {'youtube': ['player_client=ios,tv,web']},
    }

    if cookie_path:
        ydl_opts['cookiefile'] = cookie_path

    if format_choice == 'mp3':
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    else:
        # Ưu tiên lấy MP4, nếu không có thì tự động dùng WebM/MKV tốt nhất thay vì báo lỗi
        ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/bestvideo+bestaudio/best'

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        
    downloaded_file = os.listdir(temp_dir)[0]
    full_path = os.path.join(temp_dir, downloaded_file)
    return full_path, downloaded_file

# ===== GIAO DIỆN STREAMLIT =====
st.set_page_config(page_title="YouTube Downloader", page_icon="🎬")

st.title("🎬 Công Cụ Tải YouTube")
st.markdown("Nhập tên bài hát hoặc từ khóa để tìm kiếm và tải xuống Video/Âm thanh.")

# Khu vực tải lên Cookies ở thanh bên (Sidebar) để vượt lỗi 403
st.sidebar.markdown("### 🍪 Vượt lỗi chặn IP (403)")
st.sidebar.markdown("Máy chủ Streamlit thường bị YouTube chặn. Vui lòng cài tiện ích **Get cookies.txt LOCALLY** trên trình duyệt, tải file cookies của YouTube và upload vào đây:")
uploaded_cookie = st.sidebar.file_uploader("Upload file cookies.txt", type=["txt"])

# Khởi tạo session state để lưu kết quả tìm kiếm giữa các lần nhấn nút
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'download_ready' not in st.session_state:
    st.session_state.download_ready = False
    st.session_state.file_path = ""
    st.session_state.file_name = ""
    st.session_state.mime_type = ""

# Nhập từ khóa tìm kiếm
song_name = st.text_input("Nhập tên bài hát bạn muốn tải:")

if st.button("🔍 Tìm kiếm"):
    st.session_state.download_ready = False  # Reset trạng thái tải xuống
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
    
    # Nút xử lý tải xuống (về server trước)
    if st.button("⬇️ Chuẩn bị tải xuống"):
        st.session_state.download_ready = False
        video_id = selected_entry.get('id')
        selected_url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Tạo file cookie tạm thời nếu người dùng đã tải lên
        cookie_path = None
        if uploaded_cookie is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as tmp:
                tmp.write(uploaded_cookie.getvalue())
                cookie_path = tmp.name

        with st.spinner(f"Đang xử lý tải video về máy chủ: {selected_entry.get('title')}..."):
            try:
                file_path, file_name = download_youtube(selected_url, format_val, cookie_path)
                st.session_state.file_path = file_path
                st.session_state.file_name = file_name
                
                # Cập nhật mime_type động theo đuôi file thực tế tải về
                file_ext = os.path.splitext(file_name)[1].lower()
                if file_ext == '.mp3':
                    st.session_state.mime_type = "audio/mpeg"
                elif file_ext == '.mp4':
                    st.session_state.mime_type = "video/mp4"
                elif file_ext == '.webm':
                    st.session_state.mime_type = "video/webm"
                else:
                    st.session_state.mime_type = "application/octet-stream"
                    
                st.session_state.download_ready = True
            except yt_dlp.utils.DownloadError as e:
                st.error(f"Lỗi tải xuống từ yt-dlp: {e}")
            except Exception as e:
                st.error(f"Đã xảy ra lỗi hệ thống không mong muốn: {e}")

    # Nút để người dùng tải file trực tiếp về thiết bị của họ
    if st.session_state.download_ready:
        st.success("✅ File đã sẵn sàng! Bấm nút bên dưới để tải về thiết bị của bạn.")
        with open(st.session_state.file_path, "rb") as f:
            st.download_button(
                label="💾 Lưu file về máy tính",
                data=f,
                file_name=st.session_state.file_name,
                mime=st.session_state.mime_type
            )
