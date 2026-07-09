Đây là app dịch truyện được tôi (Harith-chan) vibecode bằng Gemini. Nhấn mạnh là tôi không biết một cái gì về code, chỉ là 1 thằng rảnh rỗi vừa thi THPTQG xong, rảnh rỗi và ngại đọc tiếng anh.
. Tôi cũng không biết cách viết cái README này thế nào, đại đại thôi.
. Hệ điều hành tôi sử dụng là ArchLinux nên tôi sẽ viết hướng dẫn cho Arch nói riêng, theo cách mà tôi đã sử dụng nó thành công.
HDSD:
-Clone 
- cd trong thư mục mà bạn đã clone
- python -m venv venv
- source venv/bin/activate
- Đổi tên file truyện gốc thành truyen_goc.pdf

* Đó là những cái cơ bản, cái chính ở đây là bạn phải chọn cho mình một nhà cung cấp AI, 2 file FAST và SLOW trong bài của tôi là dùng nền tảng Groq. (console.groq.com)
- Tạo tài khoản, tạo cho mình một cái API Key và thêm nó vào trong file .py trong thư mục mà bạn đã clone.(Thêm vào đoạn này nè 
if __name__ == "__main__":
    API_KEY = "ĐIỀN_KEY_GSK_CỦA_BẠN_VÀO_ĐÂY" 
    INPUT_FILE = "truyen_goc.pdf"
    OUTPUT_FILE = "truyen_da_dich.pdf"
    MODEL = "llama-3.1-8b-instant"                    )

- Về model AI thì tuỳ chỉnh, mặc định sẽ là llama-3.1-8b-instant , cả 2 bản FAST và SLOW đều dùng chung 1 model, SLOW sẽ nâng "temperature" lên thành 0.6, cho kết quả dịch mượt mà, đúng văn phong hơn.
- Do nền tảng Groq có giới hạn số token trên mỗi phút, nên cứ mỗi khi quá số tokens thì sẽ có khoảng chờ là 5s trước khi thử lại :D (miễn phí thì chịu thôi)
