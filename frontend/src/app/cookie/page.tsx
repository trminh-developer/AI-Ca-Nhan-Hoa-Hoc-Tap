import Link from 'next/link';

export default function CookiesPage() {
  return (
    <div className="min-h-screen bg-background text-foreground py-20 px-6 font-sans">
      <div className="max-w-3xl mx-auto">
        <Link href="/" className="text-cyan-400 hover:text-cyan-300 text-sm mb-8 inline-block">
          ← Về trang chủ
        </Link>
        <h1 className="text-3xl font-bricolage font-bold mb-8">Chính sách Cookie</h1>
        
        <div className="space-y-6 text-[#9090b8] leading-relaxed">
          <p>Cập nhật lần cuối: Tháng 7, 2024</p>
          
          <h2 className="text-xl font-semibold text-white mt-8 mb-4">1. Cookie là gì?</h2>
          <p>
            Cookie là các tập tin văn bản nhỏ được lưu trữ trên thiết bị của bạn khi truy cập trang web.
            Chúng giúp hệ thống ghi nhớ phiên đăng nhập và các tùy chọn cá nhân hóa.
          </p>

          <h2 className="text-xl font-semibold text-white mt-8 mb-4">2. Chúng tôi sử dụng cookie nào?</h2>
          <ul className="list-disc pl-6 space-y-2">
            <li><strong>Cookie thiết yếu:</strong> Để duy trì trạng thái đăng nhập và bảo mật.</li>
            <li><strong>Cookie hiệu suất:</strong> Phục vụ việc theo dõi lỗi, thống kê lưu lượng.</li>
          </ul>

          <h2 className="text-xl font-semibold text-white mt-8 mb-4">3. Quản lý cookie</h2>
          <p>
            Bạn có thể vô hiệu hóa cookie trong phần cài đặt trình duyệt. Tuy nhiên, nếu vô hiệu hóa 
            cookie thiết yếu, bạn sẽ không thể đăng nhập hoặc sử dụng tính năng lưu trữ tiến trình học tập.
          </p>
        </div>
      </div>
    </div>
  );
}
