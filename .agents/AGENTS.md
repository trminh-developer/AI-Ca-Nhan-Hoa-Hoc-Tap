# Custom Workspace Rules

## Git Branching Workflow
- Tự động áp dụng chiến lược phân nhánh (Branching Strategy) cho tất cả các thay đổi code.
- KHÔNG commit trực tiếp lên nhánh `master` (hoặc `main`).
- Mọi tính năng mới hoặc sửa lỗi phải được thực hiện trên một nhánh riêng (ví dụ: `dev`, `feature/...`, `bugfix/...`).
- Sau khi hoàn thành và push nhánh mới lên remote, mới tiến hành gộp (merge) lại vào nhánh chính nếu người dùng yêu cầu, hoặc tạo Pull Request.
