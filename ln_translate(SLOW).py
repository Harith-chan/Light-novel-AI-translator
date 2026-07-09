import os
import platform
import fitz  # PyMuPDF
import requests
import time

def get_vietnamese_font():
    if platform.system() == "Linux":
        paths = [
            "/usr/share/fonts/TTF/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
        ]
    else:
        paths = [r"C:\Windows\Fonts\Arial.ttf"]
    for path in paths:
        if os.path.exists(path):
            return path
    return None

def translate_pdf_lightnovel(input_pdf, output_pdf, api_key, model_name="llama-3.1-8b-instant"):
    # PHẦN PROMPT ĐÃ ĐƯỢC TINH CHỈNH ĐỂ VĂN PHONG MƯỢT MÀ, THOÁT Ý VĂN HỌC
    system_prompt = (
        "Bạn là một dịch giả xuất sắc, chuyên phóng tác và dịch thuật Light Novel Nhật Bản sang tiếng Việt.\n"
        "Nhiệm vụ của bạn là dịch đoạn văn bản được cung cấp với các tiêu chuẩn sau:\n"
        "1. Văn phong: Tự nhiên, mượt mà, giàu cảm xúc và mang đậm chất văn học truyện chữ Việt Nam. Tuyệt đối không dịch thô từng từ (word-by-word).\n"
        "2. Cấu trúc câu: Biến đổi linh hoạt các câu bị động khó hiểu sang câu chủ động thuần Việt. Thoát ý sao cho người Việt đọc cảm thấy trôi chảy.\n"
        "3. Đại từ nhân xưng: Phù hợp ngữ cảnh hội thoại giữa các nhân vật (ví dụ: anh - em, cậu - tớ, tôi - ông, ta - ngươi). Giữ nguyên các kính ngữ (-san, -kun, -sama) nếu đó là bối cảnh Nhật Bản đặc trưng.\n"
        "4. Định dạng: Tuyệt đối giữ nguyên cấu trúc ngắt dòng, ngắt đoạn, dấu ngoặc kép thoại của văn bản gốc.\n"
        "Chỉ trả về duy nhất bản dịch tiếng Việt, không thêm lời giải thích, không ghi chú gì thêm."
    )
    
    doc = fitz.open(input_pdf)
    out_doc = fitz.open()
    font_path = get_vietnamese_font()
    
    if font_path:
        font_name = "custom_font"
        with open(font_path, "rb") as f:
            font_buffer = f.read()
    else:
        font_name = "sans-serif"
        font_buffer = None

    print(f"[*] Bắt đầu dịch qua GROQ CLOUD (Bản dịch Văn học Mượt mà): {input_pdf} ({len(doc)} trang)...")
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        rect = page.rect
        
        # Sao chép trang gốc để giữ nguyên hình ảnh nền/minh họa
        out_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
        out_page = out_doc[-1]
        
        if font_buffer:
            out_page.insert_font(fontname=font_name, fontbuffer=font_buffer)
        
        text = page.get_text("text").strip()
        if text:
            print(f"[-] Đang dịch trang {page_num + 1}/{len(doc)}...")
            
            # Đặt lề trang (Margin)
            margin_x = 45
            margin_y = 45
            white_box = fitz.Rect(margin_x, margin_y, rect.width - margin_x, rect.height - margin_y)
            
            # Vẽ nền trắng xóa chữ cũ
            out_page.draw_rect(white_box, color=(1, 1, 1), fill=(1, 1, 1), overlay=True)
            
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Dịch đoạn văn bản này một cách mượt mà và tự nhiên:\n\n{text}"}
                ],
                "temperature": 0.6  # Tăng lên 0.6 để AI dịch bay bổng, mượt mà và thoát ý tốt hơn
            }
            
            translated_text = ""
            while True:
                try:
                    response = requests.post(url, json=payload, headers=headers)
                    res_json = response.json()
                    
                    if response.status_code == 200:
                        translated_text = res_json['choices'][0]['message']['content'].strip()
                        time.sleep(1.5)
                        break
                    elif "rate_limit_exceeded" in str(res_json) or response.status_code == 429:
                        print("    [!] Chạm giới hạn phút của Groq. Tự động đợi 5 giây...")
                        time.sleep(5)
                    else:
                        print(f" [!] Lỗi API Groq: {response.text}")
                        translated_text = f"[Lỗi dịch tại trang này: {response.status_code}]"
                        break
                except Exception as e:
                    print(f" [!] Lỗi kết nối: {e}. Thử lại sau 3 giây...")
                    time.sleep(3)
            
            # Tự động co giãn size chữ phù hợp với trang
            initial_fontsize = 11.0
            while initial_fontsize > 8.0:
                text_len = len(translated_text) * (initial_fontsize * 0.5)
                lines = (text_len / white_box.width) * 1.1
                height_needed = lines * (initial_fontsize * 1.6)
                if height_needed <= white_box.height:
                    break
                initial_fontsize -= 0.5

            # Biến đổi các dấu xuống dòng thành thẻ <br> để HTML hiển thị chính xác bố cục ngắt đoạn
            html_content_formatted = translated_text.replace("\n", "<br>")
            
            # Tạo chuỗi HTML với CSS hoàn chỉnh
            html_content = f"""
            <div style="font-family: '{font_name}'; 
                        font-size: {initial_fontsize}pt; 
                        line-height: 1.6; 
                        text-align: justify; 
                        color: #000000;">
                {html_content_formatted}
            </div>
            """
            
            # Ghi đè HTMLBox lên PDF
            out_page.insert_htmlbox(white_box, html_content)
        else:
            print(f"[-] Trang {page_num + 1}: Trang ảnh minh họa thuần (Giữ nguyên).")
            
    out_doc.save(output_pdf)
    out_doc.close()
    doc.close()
    print(f"[+] Hoàn thành! File dịch mượt mà đã lưu tại: {output_pdf}")

if __name__ == "__main__":
    API_KEY = "ĐIỀN_KEY_GSK_CỦA_BẠN_VÀO_ĐÂY" 
    INPUT_FILE = "truyen_goc.pdf"
    OUTPUT_FILE = "truyen_da_dich.pdf"
    
    # Model 8B chạy nhanh. Nếu muốn văn thơ đỉnh cao hơn nữa qua VPN, bạn có thể thử đổi thành "llama-3.3-70b-versatile"
    MODEL = "llama-3.1-8b-instant" 
    
    if API_KEY == "ĐIỀN_KEY_GSK_CỦA_BẠN_VÀO_ĐÂY":
        print("[!] Bạn chưa điền API Key của Groq vào code kìa.")
    else:
        translate_pdf_lightnovel(INPUT_FILE, OUTPUT_FILE, API_KEY, MODEL)
