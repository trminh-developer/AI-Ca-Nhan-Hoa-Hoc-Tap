import Link from 'next/link';

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-background text-foreground py-20 px-6 font-sans">
      <div className="max-w-3xl mx-auto">
        <Link href="/" className="text-cyan-400 hover:text-cyan-300 text-sm mb-8 inline-block">
          ← Về trang chủ
        </Link>
        <h1 className="text-3xl font-bricolage font-bold mb-8">Điều khoản sử dụng</h1>
        
        <div className="space-y-6 text-[#9090b8] leading-relaxed">
          <p>Cập nhật lần cuối: Tháng 7, 2024</p>
          
          <h2 className="text-xl font-semibold text-white mt-8 mb-4">1. Chấp nhận điều khoản</h2>
          <p>
            Bằng việc truy cập và sử dụng hệ thống LearnAI, bạn đồng ý bị ràng buộc bởi các điều khoản
            và điều kiện này. Nếu bạn không đồng ý với bất kỳ phần nào của các điều khoản, bạn không
            thể truy cập hệ thống.
          </p>

          <h2 className="text-xl font-semibold text-white mt-8 mb-4">2. Mô tả dịch vụ</h2>
          <p>
            LearnAI là hệ thống học tập cá nhân hóa sử dụng thuật toán Elo Rating và Spaced Repetition
            để tối ưu hóa lộ trình học tập. Dịch vụ được cung cấp &quot;như nguyên trạng&quot; (as is) và &quot;khi có sẵn&quot;.
          </p>

          <h2 className="text-xl font-semibold text-white mt-8 mb-4">3. Trách nhiệm người dùng</h2>
          <ul className="list-disc pl-6 space-y-2">
            <li>Bảo mật thông tin tài khoản.</li>
            <li>Không chia sẻ tài khoản cho người khác.</li>
            <li>Không có hành vi phá hoại hệ thống.</li>
          </ul>

          <h2 className="text-xl font-semibold text-white mt-8 mb-4">4. Sở hữu trí tuệ</h2>
          <p>
            Tất cả nội dung, giao diện, và thuật toán trên LearnAI đều thuộc bản quyền của nhóm
            Nghiên cứu khoa học sinh viên.
          </p>
        </div>
      </div>
    </div>
  );
}
