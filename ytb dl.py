import yt_dlp

def download_video_by_song_name(song_name: str, format_choice: str = 'mp4') -> None:
    """
    Tìm kiếm và tải xuống video/âm thanh YouTube dựa trên tên bài hát.
    
    Args:
        song_name (str): Tên bài hát (hoặc từ khóa) cần tìm kiếm.
        format_choice (str): Định dạng tải về ('mp4' hoặc 'mp3'). Mặc định là 'mp4'.
    """
    print(f"[*] Đang tìm kiếm 5 kết quả cho: '{song_name}'...")
    
    # Bước 1: Tìm kiếm 5 kết quả (không tải xuống)
    search_opts = {
        'extract_flat': True,
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(search_opts) as ydl:
            info = ydl.extract_info(f"ytsearch5:{song_name}", download=False)
            
        if not info or 'entries' not in info or not info['entries']:
            print("[-] Không tìm thấy kết quả nào.")
            return
            
        entries = info['entries']
        
        print("\n=== KẾT QUẢ TÌM KIẾM ===")
        for idx, entry in enumerate(entries, start=1):
            title = entry.get('title', 'Không có tiêu đề')
            duration = entry.get('duration')
            
            # Định dạng thời lượng (giây) sang dạng mm:ss hoặc hh:mm:ss
            if duration:
                m, s = divmod(duration, 60)
                h, m = divmod(m, 60)
                duration_str = f"{int(h):02d}:{int(m):02d}:{int(s):02d}" if h else f"{int(m):02d}:{int(s):02d}"
            else:
                duration_str = "N/A"
                
            print(f"{idx}. {title} (Thời lượng: {duration_str})")
            
        # Bước 2: Người dùng chọn video để tải
        while True:
            try:
                choice = int(input("\nNhập số thứ tự video bạn muốn tải (1-5) hoặc 0 để hủy: "))
                if choice == 0:
                    print("Đã hủy tải xuống.")
                    return
                if 1 <= choice <= len(entries):
                    selected_entry = entries[choice - 1]
                    break
                else:
                    print("[-] Lựa chọn không hợp lệ, vui lòng nhập lại.")
            except ValueError:
                print("[-] Vui lòng nhập một số hợp lệ.")
                
        # Xây dựng link hoàn chỉnh dựa vào ID video
        video_id = selected_entry.get('id')
        selected_url = f"https://www.youtube.com/watch?v={video_id}"
            
        print(f"\n[*] Đang chuẩn bị tải: {selected_entry.get('title')}")
        
        # Bước 3: Cấu hình và tải xuống video đã chọn
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
            ydl.download([selected_url])
            
        print("\n[+] Tải xuống hoàn tất thành công!")
        
    except yt_dlp.utils.DownloadError as e:
        print(f"\n[-] Lỗi tải xuống từ yt-dlp: {e}")
    except Exception as e:
        print(f"\n[-] Đã xảy ra lỗi hệ thống không mong muốn: {e}")

if __name__ == "__main__":
    print("=== CÔNG CỤ TẢI YOUTUBE BẰNG TÊN BÀI HÁT ===")
    user_input = input("Nhập tên bài hát bạn muốn tải: ")
    
    if user_input.strip():
        print("\nChọn định dạng tải xuống:")
        print("1. MP4 (Video)")
        print("2. MP3 (Chỉ âm thanh)")
        choice = input("Nhập lựa chọn của bạn (1 hoặc 2): ")
        
        format_choice = 'mp3' if choice.strip() == '2' else 'mp4'
        download_video_by_song_name(user_input.strip(), format_choice)
    else:
        print("[-] Tên bài hát không được để trống.")
