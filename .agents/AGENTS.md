# Custom Workspace Rules

## Git Branching Workflow
- Tự động áp dụng chiến lược phân nhánh Git Flow cho tất cả các thay đổi.
- **KHÔNG BAO GIỜ** commit trực tiếp lên nhánh `main`. Nhánh `main` chỉ chứa code đã hoàn thiện và chạy ổn định.
- Luôn tạo và làm việc trên các nhánh con tương ứng với từng mục đích cụ thể:
  - `dev`: Nhánh trung gian để tích hợp code trước khi lên `main`.
  - `feature/frontend`: Dành riêng cho các thay đổi giao diện, UI/UX.
  - `feature/backend`: Dành riêng cho các thay đổi API, Database, Logic.
  - `bugfix/...`: Dành riêng cho việc sửa các lỗi phát sinh.
- Sau khi hoàn thành trên nhánh con, mới tiến hành gộp (merge) vào `dev` (và cuối cùng là `main`).
- **TỰ ĐỘNG HÓA PUSH**: Sau khi hoàn tất viết code hoặc sửa đổi bất cứ tính năng/bug nào, AI phải **TỰ ĐỘNG** `git add`, `git commit` và `git push` lên GitHub ngay lập tức, không được đợi người dùng nhắc. Tự giác đẩy code để lưu trữ và deploy liên tục!
