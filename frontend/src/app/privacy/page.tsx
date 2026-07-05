import Link from 'next/link';

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-background text-foreground py-20 px-6 font-sans">
      <div className="max-w-3xl mx-auto">
        <Link href="/" className="text-cyan-400 hover:text-cyan-300 text-sm mb-8 inline-block">
          ← Về trang chủ
        </Link>
        <h1 className="text-3xl font-bricolage font-bold mb-8">Chính sách bảo mật</h1>
        
        <div className="space-y-6 text-[#9090b8] leading-relaxed">
          <p>Cập nhật lần cuối: Tháng 7, 2024</p>
          
          <h2 className="text-xl font-semibold text-white mt-8 mb-4">1. Thu thập thông tin</h2>
          <p>
            Hệ thống thu thập dữ liệu về quá trình học tập của bạn, bao gồm lịch sử trả lời câu hỏi, 
            thời gian học, và mức độ tương tác để tối ưu hóa thuật toán gợi ý.
          </p>

          <h2 className="text-xl font-semibold text-white mt-8 mb-4">2. Sử dụng thông tin</h2>
          <p>
            Dữ liệu thu thập được chỉ nhằm mục đích:
          </p>
          <ul className="list-disc pl-6 space-y-2">
            <li>Cá nhân hóa lộ trình học tập.</li>
            <li>Đánh giá năng lực dựa trên Elo Rating.</li>
            <li>Nghiên cứu khoa học.</li>
          </ul>

          <h2 className="text-xl font-semibold text-white mt-8 mb-4">3. Bảo vệ dữ liệu</h2>
          <p>
            Hệ thống cam kết không bán, trao đổi hoặc chia sẻ thông tin cá nhân của bạn cho bên thứ ba
            dưới mọi hình thức, trừ khi có yêu cầu từ cơ quan pháp luật.
          </p>
        </div>
      </div>
    </div>
  );
}
