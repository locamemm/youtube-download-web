import flet as ft
import yt_dlp

def main(page: ft.Page):
    page.title = "Công Cụ Tải YouTube"
    page.window_width = 500
    page.window_height = 800
    page.scroll = ft.ScrollMode.AUTO
    page.theme_mode = ft.ThemeMode.LIGHT

    # Các thành phần giao diện (UI)
    song_name_input = ft.TextField(label="Nhập tên bài hát", expand=True)
    format_dropdown = ft.Dropdown(
        label="Định dạng",
        options=[
            ft.dropdown.Option("mp4", "MP4 (Video)"),
            ft.dropdown.Option("mp3", "MP3 (Âm thanh)"),
        ],
        value="mp4",
        width=150,
    )
    status_text = ft.Text(value="", color="blue")
    results_view = ft.Column()

    def search_click(e):
        query = song_name_input.value.strip()
        if not query:
            status_text.value = "[-] Vui lòng nhập tên bài hát."
            status_text.color = "red"
            page.update()
            return

        status_text.value = f"[*] Đang tìm kiếm kết quả cho: '{query}'..."
        status_text.color = "blue"
        results_view.controls.clear()
        page.update()

        search_opts = {'extract_flat': True, 'quiet': True}
        try:
            with yt_dlp.YoutubeDL(search_opts) as ydl:
                info = ydl.extract_info(f"ytsearch5:{query}", download=False)
            
            if not info or 'entries' not in info or not info['entries']:
                status_text.value = "[-] Không tìm thấy kết quả nào."
                status_text.color = "red"
                page.update()
                return

            entries = info['entries']
            status_text.value = f"[+] Tìm thấy {len(entries)} kết quả. Vui lòng chọn để tải xuống."
            status_text.color = "green"
            
            for idx, entry in enumerate(entries, start=1):
                title = entry.get('title', 'Không có tiêu đề')
                duration = entry.get('duration')
                video_id = entry.get('id')
                
                if duration:
                    m, s = divmod(duration, 60)
                    h, m = divmod(m, 60)
                    duration_str = f"{int(h):02d}:{int(m):02d}:{int(s):02d}" if h else f"{int(m):02d}:{int(s):02d}"
                else:
                    duration_str = "N/A"
                
                # Khởi tạo Card chứa thông tin video và nút Tải xuống
                results_view.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text(f"{idx}. {title}", weight=ft.FontWeight.BOLD, size=16),
                                ft.Text(f"Thời lượng: {duration_str}", color="grey700"),
                                ft.ElevatedButton(
                                    "Tải xuống",
                                    icon="download",
                                    # Lưu lại giá trị video_id và title bằng tham số mặc định của lambda
                                    on_click=lambda e, vid=video_id, t=title: download_click(vid, t)
                                )
                            ]),
                            padding=15
                        )
                    )
                )
        except Exception as ex:
            status_text.value = f"[-] Lỗi tìm kiếm: {ex}"
            status_text.color = "red"
            
        page.update()

    def download_click(video_id, title):
        format_choice = format_dropdown.value
        selected_url = f"https://www.youtube.com/watch?v={video_id}"
        
        status_text.value = f"[*] Đang tải: {title} ({format_choice.upper()}). Vui lòng chờ..."
        status_text.color = "blue"
        page.update()

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
                'preferredquality': '320',
            }]
        else:
            ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([selected_url])
            status_text.value = f"[+] Đã tải xong: {title}"
            status_text.color = "green"
        except yt_dlp.utils.DownloadError as ex:
            status_text.value = f"[-] Lỗi tải xuống: {ex}"
            status_text.color = "red"
        except Exception as ex:
            status_text.value = f"[-] Lỗi hệ thống: {ex}"
            status_text.color = "red"
            
        page.update()

    # Thêm nút Enter để tìm kiếm luôn cho tiện
    song_name_input.on_submit = search_click

    # Xếp các thành phần lên màn hình
    page.add(
        ft.Text("Công Cụ Tải YouTube", size=24, weight=ft.FontWeight.BOLD),
        ft.Row([song_name_input, format_dropdown]),
        ft.ElevatedButton("Tìm kiếm", on_click=search_click, icon="search"),
        status_text,
        ft.Divider(),
        results_view
    )

if __name__ == "__main__":
    ft.app(target=main)
