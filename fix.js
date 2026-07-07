const fs = require('fs');
let code = fs.readFileSync('frontend/src/app/LandingPage.tsx', 'utf8');

const replacements = {
  'ví\u00A0 trí\u00AD tuệ': 'và trí tuệ',
  'nhí\u00AD tuệ': 'nhân tạo', // Let's just do precise replacements
  'ví  trí tuệ': 'và trí tuệ',
  'ví\u00A0 trí\u00AD tuệ': 'và trí tuệ',
  'khoa học nhận thức ví': 'khoa học nhận thức và',
  'đối tượng ví giải': 'đối tượng và giải',
  'quang học ví nhiệt': 'quang học và nhiệt',
  'thống kỉª ví ứng': 'thống kê và ứng',
  'cíc chủ đề': 'các chủ đề',
  'độ khỉª': 'độ khó',
  'riíªng biệt': 'riêng biệt',
  'toí n diện': 'toàn diện',
  'vấpn đề': 'vấn đề', // fix if vấpn is there
  'giải quyết ví': 'giải quyết vấn', // wait
  'xíc suất': 'xác suất',
  'kỉª': 'kê',
  'sí¡nh': 'sánh',
  'toí n hệ thống': 'toàn hệ thống',
  'Phí¢n tích': 'Phân tích',
  'ví¹ng': 'vùng',
  'lí ví¹ng': 'là vùng',
  'đí¢y lí': 'đây là',
  'liíªn tục': 'liên tục',
  'khỉª': 'khó',
  'xí¢y dựng': 'xây dựng',
  'tríªn': 'trên',
  'nhí¢n tạo': 'nhân tạo',
  'Â·': '·',
  'Â©': '©',
  'â€“': '–',
  'â€”': '—',
  'Nghiíªn cứu': 'Nghiên cứu',
  'íª': 'ê',
  'í¢': 'â',
  'í³': 'ó',
  'í¡': 'á',
  'í¹': 'ù',
  'íµ': 'õ',
  'í´': 'ô',
  'í²': 'ò',
  'í©': 'é',
  'í£': 'ã'
};

for (const [k, v] of Object.entries(replacements)) {
  code = code.split(k).join(v);
}

// Additional manual fixes for any weirdly combined corrupted letters
code = code.replace(/ví\s+trí\xAD\s+tuệ/g, 'và trí tuệ');
code = code.replace(/ví  trí­ tuệ/g, 'và trí tuệ');

// Let's replace line 251 entirely to be safe
code = code.replace(/Hệ thống học tập thế hệ mới.*nhân tạo\./, 'Hệ thống học tập thế hệ mới — cá nhân hóa từng câu hỏi, từng lịch ôn, từng gợi ý. Được xây dựng dựa trên khoa học nhận thức và trí tuệ nhân tạo.');

// Let's replace the Features section corrupted lines
code = code.replace(/Hệ thống Elo Rating liên tục hiệu chỉnh độ khó câu hỏi dựa trên mỗi câu trả lời của bạn\. Mục tiêu duy trì trong vùng 70–85% tỷ lệ đúng – đây là vùng học tập hiệu quả nhất theo nghiên cứu khoa học nhận thức\./g, 'Hệ thống Elo Rating liên tục hiệu chỉnh độ khó câu hỏi dựa trên mỗi câu trả lời của bạn. Mục tiêu duy trì trong vùng 70–85% tỷ lệ đúng – đây là vùng học tập hiệu quả nhất theo nghiên cứu khoa học nhận thức.');
code = code.replace(/So sánh với chuẩn học tập toàn hệ thống/g, 'So sánh với chuẩn học tập toàn hệ thống');
code = code.replace(/Phân tích xu hướng tiến bộ theo tuần/g, 'Phân tích xu hướng tiến bộ theo tuần');
code = code.replace(/Bốn trụ cột được xây dựng trên nền tảng nghiên cứu nhận thức học ví khoa học dữ liệu\./g, 'Bốn trụ cột được xây dựng trên nền tảng nghiên cứu nhận thức học và khoa học dữ liệu.');
code = code.replace(/Mỗi môn học được chia thành các chủ đề nhỏ với độ khó riêng biệt, đảm bảo học tập toàn diện\./g, 'Mỗi môn học được chia thành các chủ đề nhỏ với độ khó riêng biệt, đảm bảo học tập toàn diện.');
code = code.replace(/Thuật toán, cấu trúc dữ liệu, lập trình hướng đối tượng ví giải quyết vấn đề thực tế\./g, 'Thuật toán, cấu trúc dữ liệu, lập trình hướng đối tượng và giải quyết vấn đề thực tế.');
code = code.replace(/Giải tích, đại số tuyến tính, xác suất thống kê ví ứng dụng trong khoa học máy tính\./g, 'Giải tích, đại số tuyến tính, xác suất thống kê và ứng dụng trong khoa học máy tính.');
code = code.replace(/Cơ học cổ điển, điện từ học, quang học ví nhiệt động lực học với bài toán thực tế\./g, 'Cơ học cổ điển, điện từ học, quang học và nhiệt động lực học với bài toán thực tế.');

fs.writeFileSync('frontend/src/app/LandingPage.tsx', code, 'utf8');
console.log('Done replacement!');
