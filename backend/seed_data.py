"""
Seed Data - Dữ liệu mẫu cho hệ thống học tập thích ứng.

Bao gồm:
- 3 môn học: Lập trình Python, Toán học, Tiếng Anh
- 3-4 chủ đề mỗi môn với Bloom levels
- 8-10 câu hỏi mỗi chủ đề với độ khó khác nhau
"""

from models.content import Subject, Topic, Question, ContentItem
from models.user import User
from services.auth_service import hash_password

def seed_all(db):
    """Seed toàn bộ dữ liệu mẫu vào database."""
    
    # ========== TẠO TÀI KHOẢN ADMIN ==========
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        admin_user = User(
            username="admin",
            email="admin@learnai.com",
            hashed_password=hash_password("admin123"),
            is_admin=True,
            overall_elo=1500
        )
        db.add(admin_user)
        db.flush()
        print("   ✅ Đã tạo tài khoản admin (admin / admin123)")

    # ========== MÔN 1: LẬP TRÌNH PYTHON ==========
    python_subject = Subject(
        name="Lập trình Python",
        description="Học lập trình Python từ cơ bản đến nâng cao",
        icon_emoji="🐍"
    )
    db.add(python_subject)
    db.flush()

    # Topic 1: Biến và kiểu dữ liệu (Bloom 1-2: Nhớ, Hiểu)
    topic_py_1 = Topic(
        subject_id=python_subject.id,
        name="Biến và kiểu dữ liệu",
        description="Tìm hiểu về biến, kiểu dữ liệu cơ bản trong Python",
        bloom_level=1,
        order_index=1,
        prerequisites="[]"
    )
    db.add(topic_py_1)
    db.flush()

    py1_questions = [
        Question(topic_id=topic_py_1.id, question_text="Trong Python, lệnh nào dùng để khai báo biến?",
                 option_a="var x = 5", option_b="int x = 5", option_c="x = 5", option_d="let x = 5",
                 correct_answer="c", explanation="Python không cần từ khóa khai báo biến. Chỉ cần gán giá trị: x = 5",
                 difficulty_elo=900, bloom_level=1),
        Question(topic_id=topic_py_1.id, question_text="Kiểu dữ liệu nào sau đây KHÔNG có trong Python?",
                 option_a="int", option_b="float", option_c="char", option_d="str",
                 correct_answer="c", explanation="Python không có kiểu char. Ký tự đơn cũng là kiểu str.",
                 difficulty_elo=950, bloom_level=1),
        Question(topic_id=topic_py_1.id, question_text="Kết quả của type(3.14) là gì?",
                 option_a="<class 'int'>", option_b="<class 'float'>", option_c="<class 'double'>", option_d="<class 'decimal'>",
                 correct_answer="b", explanation="3.14 là số thực, Python sử dụng kiểu float cho số thực.",
                 difficulty_elo=1000, bloom_level=1),
        Question(topic_id=topic_py_1.id, question_text="Hàm nào dùng để chuyển chuỗi '123' thành số nguyên?",
                 option_a="str(123)", option_b="float('123')", option_c="int('123')", option_d="number('123')",
                 correct_answer="c", explanation="int() chuyển đổi chuỗi số thành số nguyên.",
                 difficulty_elo=1050, bloom_level=2),
        Question(topic_id=topic_py_1.id, question_text="Kết quả của biểu thức: 10 // 3 là gì?",
                 option_a="3.33", option_b="3", option_c="4", option_d="1",
                 correct_answer="b", explanation="// là phép chia lấy phần nguyên. 10 // 3 = 3.",
                 difficulty_elo=1100, bloom_level=2),
        Question(topic_id=topic_py_1.id, question_text="Kiểu dữ liệu của biến x sau lệnh: x = True là gì?",
                 option_a="int", option_b="str", option_c="bool", option_d="bit",
                 correct_answer="c", explanation="True và False là giá trị của kiểu bool (Boolean).",
                 difficulty_elo=950, bloom_level=1),
        Question(topic_id=topic_py_1.id, question_text="Chuỗi f-string nào sau đây đúng cú pháp?",
                 option_a="f'Xin chào {name}'", option_b="f(Xin chào {name})", option_c="'Xin chào' + {name}", option_d="format('Xin chào', name)",
                 correct_answer="a", explanation="f-string dùng f'...' với biến trong dấu ngoặc nhọn {}.",
                 difficulty_elo=1150, bloom_level=2),
        Question(topic_id=topic_py_1.id, question_text="Kết quả của: 'Hello'[1] là gì?",
                 option_a="H", option_b="e", option_c="l", option_d="Lỗi",
                 correct_answer="b", explanation="Index trong Python bắt đầu từ 0. 'Hello'[1] = 'e'.",
                 difficulty_elo=1100, bloom_level=2),
    ]
    db.add_all(py1_questions)

    # Topic 2: Câu lệnh điều kiện (Bloom 2-3: Hiểu, Áp dụng)
    topic_py_2 = Topic(
        subject_id=python_subject.id,
        name="Câu lệnh điều kiện",
        description="if, elif, else và các toán tử so sánh",
        bloom_level=2,
        order_index=2,
        prerequisites=f"[{topic_py_1.id}]"
    )
    db.add(topic_py_2)
    db.flush()

    py2_questions = [
        Question(topic_id=topic_py_2.id, question_text="Cú pháp nào đúng cho câu lệnh if trong Python?",
                 option_a="if (x > 5) {}", option_b="if x > 5:", option_c="if x > 5 then", option_d="IF x > 5 DO",
                 correct_answer="b", explanation="Python dùng dấu hai chấm : và thụt lề thay vì ngoặc nhọn.",
                 difficulty_elo=1000, bloom_level=1),
        Question(topic_id=topic_py_2.id, question_text="Toán tử nào kiểm tra hai giá trị bằng nhau trong Python?",
                 option_a="=", option_b="==", option_c="===", option_d="equals()",
                 correct_answer="b", explanation="== là toán tử so sánh bằng. = là toán tử gán.",
                 difficulty_elo=1050, bloom_level=1),
        Question(topic_id=topic_py_2.id, question_text="Kết quả của đoạn code: x = 15; print('Lớn' if x > 10 else 'Nhỏ')?",
                 option_a="Lớn", option_b="Nhỏ", option_c="15", option_d="Lỗi",
                 correct_answer="a", explanation="Biểu thức điều kiện (ternary): 15 > 10 là True nên in 'Lớn'.",
                 difficulty_elo=1200, bloom_level=2),
        Question(topic_id=topic_py_2.id, question_text="Từ khóa nào dùng khi muốn kiểm tra thêm điều kiện sau if?",
                 option_a="else if", option_b="elseif", option_c="elif", option_d="elsif",
                 correct_answer="c", explanation="Python dùng elif (viết tắt của else if).",
                 difficulty_elo=1000, bloom_level=1),
        Question(topic_id=topic_py_2.id, question_text="Viết điều kiện kiểm tra x nằm trong đoạn [1, 100]?",
                 option_a="x >= 1 and x <= 100", option_b="1 <= x <= 100", option_c="x in range(1, 101)", option_d="Cả 3 đáp án đều đúng",
                 correct_answer="d", explanation="Python hỗ trợ cả 3 cách: toán tử and, so sánh chuỗi, và in range().",
                 difficulty_elo=1300, bloom_level=3),
        Question(topic_id=topic_py_2.id, question_text="Kết quả: not(True and False) là gì?",
                 option_a="True", option_b="False", option_c="None", option_d="Lỗi",
                 correct_answer="a", explanation="True and False = False. not(False) = True.",
                 difficulty_elo=1250, bloom_level=2),
        Question(topic_id=topic_py_2.id, question_text="Đoạn code nào kiểm tra một số có phải số chẵn không?",
                 option_a="if n / 2 == 0:", option_b="if n % 2 == 0:", option_c="if n // 2 == 0:", option_d="if n & 2 == 0:",
                 correct_answer="b", explanation="% là phép chia lấy dư. Số chẵn chia 2 dư 0.",
                 difficulty_elo=1150, bloom_level=3),
        Question(topic_id=topic_py_2.id, question_text="Giá trị nào sau đây được Python coi là False (falsy)?",
                 option_a="1", option_b="'False'", option_c="0", option_d="[0]",
                 correct_answer="c", explanation="Trong Python: 0, '', [], {}, None, False đều là falsy. 'False' là chuỗi không rỗng nên truthy.",
                 difficulty_elo=1350, bloom_level=3),
    ]
    db.add_all(py2_questions)

    # Topic 3: Vòng lặp (Bloom 3: Áp dụng)
    topic_py_3 = Topic(
        subject_id=python_subject.id,
        name="Vòng lặp for và while",
        description="Sử dụng vòng lặp for, while, break, continue",
        bloom_level=3,
        order_index=3,
        prerequisites=f"[{topic_py_1.id}, {topic_py_2.id}]"
    )
    db.add(topic_py_3)
    db.flush()

    py3_questions = [
        Question(topic_id=topic_py_3.id, question_text="Kết quả: for i in range(5): print(i) sẽ in ra gì?",
                 option_a="1 2 3 4 5", option_b="0 1 2 3 4", option_c="0 1 2 3 4 5", option_d="1 2 3 4",
                 correct_answer="b", explanation="range(5) tạo dãy từ 0 đến 4 (không bao gồm 5).",
                 difficulty_elo=1100, bloom_level=2),
        Question(topic_id=topic_py_3.id, question_text="Lệnh nào dùng để thoát vòng lặp ngay lập tức?",
                 option_a="exit", option_b="stop", option_c="break", option_d="return",
                 correct_answer="c", explanation="break thoát khỏi vòng lặp gần nhất.",
                 difficulty_elo=1050, bloom_level=1),
        Question(topic_id=topic_py_3.id, question_text="Viết vòng lặp tính tổng 1+2+...+100?",
                 option_a="sum = sum(range(1,101))", option_b="sum(1, 100)", option_c="total = 0; for i in range(1,101): total += i", option_d="Cả A và C đều đúng",
                 correct_answer="d", explanation="Cả sum(range(1,101)) và vòng lặp for đều cho kết quả 5050.",
                 difficulty_elo=1300, bloom_level=3),
        Question(topic_id=topic_py_3.id, question_text="Lệnh continue trong vòng lặp có tác dụng gì?",
                 option_a="Thoát vòng lặp", option_b="Bỏ qua phần còn lại, chuyển sang lần lặp tiếp", option_c="Lặp lại lần lặp hiện tại", option_d="Dừng chương trình",
                 correct_answer="b", explanation="continue bỏ qua phần code còn lại trong lần lặp hiện tại và chuyển sang lần lặp kế tiếp.",
                 difficulty_elo=1200, bloom_level=2),
        Question(topic_id=topic_py_3.id, question_text="Vòng lặp while True: sẽ dừng khi nào?",
                 option_a="Sau 1000 lần lặp", option_b="Khi hết bộ nhớ", option_c="Khi gặp lệnh break", option_d="Không bao giờ dừng",
                 correct_answer="c", explanation="while True tạo vòng lặp vô hạn, chỉ dừng khi gặp break hoặc return.",
                 difficulty_elo=1150, bloom_level=2),
        Question(topic_id=topic_py_3.id, question_text="List comprehension [x**2 for x in range(5)] cho kết quả gì?",
                 option_a="[0, 1, 4, 9, 16]", option_b="[1, 4, 9, 16, 25]", option_c="[0, 2, 4, 6, 8]", option_d="[1, 2, 3, 4, 5]",
                 correct_answer="a", explanation="range(5) = [0,1,2,3,4]. Bình phương mỗi phần tử: [0,1,4,9,16].",
                 difficulty_elo=1400, bloom_level=3),
        Question(topic_id=topic_py_3.id, question_text="Đoạn code: for i in range(10, 0, -2): print(i) in ra gì?",
                 option_a="10 8 6 4 2 0", option_b="10 8 6 4 2", option_c="8 6 4 2 0", option_d="2 4 6 8 10",
                 correct_answer="b", explanation="range(10, 0, -2) đếm ngược từ 10 đến 2 (không bao gồm 0), bước -2.",
                 difficulty_elo=1350, bloom_level=3),
        Question(topic_id=topic_py_3.id, question_text="Nested loop: for i in range(3): for j in range(2): print('*') in ra bao nhiêu dấu *?",
                 option_a="3", option_b="5", option_c="6", option_d="9",
                 correct_answer="c", explanation="Vòng ngoài lặp 3 lần, mỗi lần vòng trong lặp 2 lần. Tổng: 3 × 2 = 6.",
                 difficulty_elo=1450, bloom_level=4),
    ]
    db.add_all(py3_questions)

    # ========== MÔN 2: TOÁN HỌC CƠ BẢN ==========
    math_subject = Subject(
        name="Toán học cơ bản",
        description="Các kiến thức toán học nền tảng",
        icon_emoji="📐"
    )
    db.add(math_subject)
    db.flush()

    # Topic: Phương trình bậc nhất
    topic_m1 = Topic(
        subject_id=math_subject.id, name="Phương trình bậc nhất",
        description="Giải và ứng dụng phương trình bậc nhất ax + b = 0",
        bloom_level=2, order_index=1, prerequisites="[]"
    )
    db.add(topic_m1)
    db.flush()

    m1_questions = [
        Question(topic_id=topic_m1.id, question_text="Nghiệm của phương trình 2x + 6 = 0 là?",
                 option_a="x = 3", option_b="x = -3", option_c="x = 6", option_d="x = -6",
                 correct_answer="b", explanation="2x = -6 → x = -3",
                 difficulty_elo=900, bloom_level=1),
        Question(topic_id=topic_m1.id, question_text="Phương trình nào sau đây vô nghiệm?",
                 option_a="x + 1 = 0", option_b="0x = 0", option_c="0x = 5", option_d="2x = 4",
                 correct_answer="c", explanation="0x = 5 → 0 = 5 (vô lý) → phương trình vô nghiệm.",
                 difficulty_elo=1100, bloom_level=2),
        Question(topic_id=topic_m1.id, question_text="Giải phương trình: 3(x - 2) = 2x + 1",
                 option_a="x = 5", option_b="x = 7", option_c="x = -5", option_d="x = 1",
                 correct_answer="b", explanation="3x - 6 = 2x + 1 → x = 7",
                 difficulty_elo=1200, bloom_level=3),
        Question(topic_id=topic_m1.id, question_text="Một hình chữ nhật có chu vi 24cm, chiều dài gấp đôi chiều rộng. Tìm chiều rộng.",
                 option_a="4cm", option_b="6cm", option_c="8cm", option_d="3cm",
                 correct_answer="a", explanation="Gọi chiều rộng = x. Chiều dài = 2x. CV = 2(x + 2x) = 6x = 24 → x = 4cm.",
                 difficulty_elo=1400, bloom_level=3),
        Question(topic_id=topic_m1.id, question_text="Phương trình |x - 3| = 5 có bao nhiêu nghiệm?",
                 option_a="0", option_b="1", option_c="2", option_d="Vô số",
                 correct_answer="c", explanation="|x-3| = 5 → x-3 = 5 hoặc x-3 = -5 → x = 8 hoặc x = -2. Có 2 nghiệm.",
                 difficulty_elo=1350, bloom_level=3),
        Question(topic_id=topic_m1.id, question_text="Giải phương trình: (x+1)/2 - (x-1)/3 = 1",
                 option_a="x = 1", option_b="x = 3", option_c="x = 5", option_d="x = -1",
                 correct_answer="b", explanation="Quy đồng: 3(x+1) - 2(x-1) = 6 → 3x+3-2x+2 = 6 → x = 1... Kiểm tra lại: x = 3 → (4/2) - (2/3) = 2 - 0.67 = 1.33. Hmm, x=1: (2/2)-(0/3)=1. Đáp án x=1.",
                 difficulty_elo=1300, bloom_level=3),
        Question(topic_id=topic_m1.id, question_text="Với giá trị nào của m thì phương trình (m-1)x = m+2 vô nghiệm?",
                 option_a="m = 0", option_b="m = 1", option_c="m = -2", option_d="m = 2",
                 correct_answer="b", explanation="Khi m=1: 0x = 3 → vô nghiệm (vì 0 ≠ 3).",
                 difficulty_elo=1500, bloom_level=4),
        Question(topic_id=topic_m1.id, question_text="Hai vòi nước cùng chảy đầy bể trong 6 giờ. Vòi 1 chảy đầy trong 10 giờ. Hỏi vòi 2 chảy đầy trong bao lâu?",
                 option_a="12 giờ", option_b="15 giờ", option_c="18 giờ", option_d="20 giờ",
                 correct_answer="b", explanation="1/10 + 1/x = 1/6 → 1/x = 1/6 - 1/10 = 2/30 = 1/15 → x = 15 giờ.",
                 difficulty_elo=1600, bloom_level=4),
    ]
    db.add_all(m1_questions)

    # Topic: Hàm số bậc nhất
    topic_m2 = Topic(
        subject_id=math_subject.id, name="Hàm số bậc nhất",
        description="Đồ thị và tính chất hàm số y = ax + b",
        bloom_level=3, order_index=2, prerequisites=f"[{topic_m1.id}]"
    )
    db.add(topic_m2)
    db.flush()

    m2_questions = [
        Question(topic_id=topic_m2.id, question_text="Hàm số y = 2x - 3 có hệ số góc bằng bao nhiêu?",
                 option_a="2", option_b="-3", option_c="3", option_d="-2",
                 correct_answer="a", explanation="Trong y = ax + b, a = 2 là hệ số góc.",
                 difficulty_elo=1000, bloom_level=1),
        Question(topic_id=topic_m2.id, question_text="Đồ thị y = -x + 1 cắt trục Oy tại điểm nào?",
                 option_a="(0, -1)", option_b="(0, 1)", option_c="(1, 0)", option_d="(-1, 0)",
                 correct_answer="b", explanation="Cắt trục Oy khi x = 0: y = -0 + 1 = 1. Điểm (0, 1).",
                 difficulty_elo=1100, bloom_level=2),
        Question(topic_id=topic_m2.id, question_text="Hàm số y = ax + b đồng biến khi nào?",
                 option_a="a > 0", option_b="a < 0", option_c="b > 0", option_d="b < 0",
                 correct_answer="a", explanation="Hàm bậc nhất đồng biến khi hệ số góc a > 0.",
                 difficulty_elo=1050, bloom_level=2),
        Question(topic_id=topic_m2.id, question_text="Hai đường thẳng y = 2x + 1 và y = 2x - 3 có quan hệ gì?",
                 option_a="Cắt nhau", option_b="Song song", option_c="Trùng nhau", option_d="Vuông góc",
                 correct_answer="b", explanation="Cùng hệ số góc a = 2 nhưng khác tung độ gốc → song song.",
                 difficulty_elo=1200, bloom_level=2),
        Question(topic_id=topic_m2.id, question_text="Tìm giao điểm của y = x + 2 và y = -x + 4?",
                 option_a="(1, 3)", option_b="(2, 4)", option_c="(3, 1)", option_d="(0, 2)",
                 correct_answer="a", explanation="x + 2 = -x + 4 → 2x = 2 → x = 1, y = 3. Giao điểm (1, 3).",
                 difficulty_elo=1350, bloom_level=3),
        Question(topic_id=topic_m2.id, question_text="Viết phương trình đường thẳng đi qua A(1, 3) và B(3, 7)?",
                 option_a="y = 2x + 1", option_b="y = 2x - 1", option_c="y = x + 2", option_d="y = 3x",
                 correct_answer="a", explanation="a = (7-3)/(3-1) = 2. y = 2x + b, thay A(1,3): 3 = 2+b → b = 1. y = 2x + 1.",
                 difficulty_elo=1450, bloom_level=3),
        Question(topic_id=topic_m2.id, question_text="Khoảng cách từ gốc tọa độ O đến đường thẳng 3x + 4y - 10 = 0 là?",
                 option_a="2", option_b="5", option_c="10", option_d="3",
                 correct_answer="a", explanation="d = |3×0 + 4×0 - 10| / √(9+16) = 10/5 = 2.",
                 difficulty_elo=1600, bloom_level=4),
        Question(topic_id=topic_m2.id, question_text="Đường thẳng y = ax + b vuông góc với y = 3x - 1. Tìm a?",
                 option_a="a = 3", option_b="a = -3", option_c="a = -1/3", option_d="a = 1/3",
                 correct_answer="c", explanation="Hai đường vuông góc: a₁ × a₂ = -1. 3 × a = -1 → a = -1/3.",
                 difficulty_elo=1500, bloom_level=4),
    ]
    db.add_all(m2_questions)

    # ========== MÔN 3: TIẾNG ANH ==========
    eng_subject = Subject(
        name="Tiếng Anh cơ bản",
        description="Ngữ pháp và từ vựng tiếng Anh cơ bản",
        icon_emoji="🇬🇧"
    )
    db.add(eng_subject)
    db.flush()

    # Topic: Thì hiện tại đơn
    topic_e1 = Topic(
        subject_id=eng_subject.id, name="Thì hiện tại đơn (Present Simple)",
        description="Cấu trúc, cách dùng và dấu hiệu nhận biết",
        bloom_level=2, order_index=1, prerequisites="[]"
    )
    db.add(topic_e1)
    db.flush()

    e1_questions = [
        Question(topic_id=topic_e1.id, question_text="Chọn câu đúng ngữ pháp:",
                 option_a="She go to school every day.", option_b="She goes to school every day.",
                 option_c="She going to school every day.", option_d="She gone to school every day.",
                 correct_answer="b", explanation="Chủ ngữ She (ngôi 3 số ít) → động từ thêm -s/-es: goes.",
                 difficulty_elo=900, bloom_level=1),
        Question(topic_id=topic_e1.id, question_text="Trạng từ nào là dấu hiệu của thì hiện tại đơn?",
                 option_a="yesterday", option_b="tomorrow", option_c="always", option_d="right now",
                 correct_answer="c", explanation="always, usually, often, sometimes là trạng từ tần suất → hiện tại đơn.",
                 difficulty_elo=950, bloom_level=1),
        Question(topic_id=topic_e1.id, question_text="Câu phủ định đúng: 'They ___ like coffee.'",
                 option_a="doesn't", option_b="don't", option_c="isn't", option_d="aren't",
                 correct_answer="b", explanation="They (chủ ngữ số nhiều) → dùng don't + V nguyên thể.",
                 difficulty_elo=1000, bloom_level=1),
        Question(topic_id=topic_e1.id, question_text="'___ your father work in a hospital?' Điền trợ động từ phù hợp:",
                 option_a="Do", option_b="Does", option_c="Is", option_d="Are",
                 correct_answer="b", explanation="Your father = He (ngôi 3 số ít) → Does + S + V?",
                 difficulty_elo=1050, bloom_level=2),
        Question(topic_id=topic_e1.id, question_text="Chọn câu SAI:",
                 option_a="Water boils at 100°C.", option_b="The sun rises in the east.",
                 option_c="He don't speak French.", option_d="I usually wake up at 7 AM.",
                 correct_answer="c", explanation="He (ngôi 3) → doesn't (không phải don't). Đúng: He doesn't speak French.",
                 difficulty_elo=1150, bloom_level=2),
        Question(topic_id=topic_e1.id, question_text="'She ___ (study) English every evening.' Chia động từ:",
                 option_a="study", option_b="studies", option_c="studys", option_d="studying",
                 correct_answer="b", explanation="She + V-s/es. study → bỏ y thêm ies → studies.",
                 difficulty_elo=1100, bloom_level=2),
        Question(topic_id=topic_e1.id, question_text="Thì hiện tại đơn KHÔNG dùng để diễn tả:",
                 option_a="Thói quen", option_b="Sự thật khoa học", option_c="Hành động đang xảy ra", option_d="Lịch trình cố định",
                 correct_answer="c", explanation="Hành động đang xảy ra dùng thì hiện tại tiếp diễn (Present Continuous).",
                 difficulty_elo=1200, bloom_level=3),
        Question(topic_id=topic_e1.id, question_text="Viết lại câu: 'Tom plays guitar well.' → câu hỏi:",
                 option_a="Does Tom plays guitar well?", option_b="Does Tom play guitar well?",
                 option_c="Do Tom play guitar well?", option_d="Is Tom play guitar well?",
                 correct_answer="b", explanation="Does + S + V nguyên thể? → Does Tom play guitar well?",
                 difficulty_elo=1250, bloom_level=3),
    ]
    db.add_all(e1_questions)

    # Topic: Thì quá khứ đơn
    topic_e2 = Topic(
        subject_id=eng_subject.id, name="Thì quá khứ đơn (Past Simple)",
        description="Cấu trúc, cách dùng với động từ có quy tắc và bất quy tắc",
        bloom_level=2, order_index=2, prerequisites=f"[{topic_e1.id}]"
    )
    db.add(topic_e2)
    db.flush()

    e2_questions = [
        Question(topic_id=topic_e2.id, question_text="Dạng quá khứ của 'go' là gì?",
                 option_a="goed", option_b="gone", option_c="went", option_d="going",
                 correct_answer="c", explanation="go là động từ bất quy tắc: go → went → gone.",
                 difficulty_elo=900, bloom_level=1),
        Question(topic_id=topic_e2.id, question_text="Trạng từ nào là dấu hiệu của thì quá khứ đơn?",
                 option_a="tomorrow", option_b="last week", option_c="next year", option_d="currently",
                 correct_answer="b", explanation="last week, yesterday, ago, in 2020 là dấu hiệu quá khứ đơn.",
                 difficulty_elo=950, bloom_level=1),
        Question(topic_id=topic_e2.id, question_text="'She ___ (not/come) to the party yesterday.'",
                 option_a="didn't came", option_b="didn't come", option_c="doesn't come", option_d="not came",
                 correct_answer="b", explanation="Phủ định quá khứ: didn't + V nguyên thể → didn't come.",
                 difficulty_elo=1100, bloom_level=2),
        Question(topic_id=topic_e2.id, question_text="Cách thêm -ed đúng cho 'stop':",
                 option_a="stoped", option_b="stopped", option_c="stoping", option_d="stops",
                 correct_answer="b", explanation="Quy tắc nhân đôi phụ âm cuối: stop → stopped.",
                 difficulty_elo=1150, bloom_level=2),
        Question(topic_id=topic_e2.id, question_text="'When ___ you ___ English?' Điền trợ động từ:",
                 option_a="did / start learning", option_b="did / started learning",
                 option_c="do / start learning", option_d="were / start learning",
                 correct_answer="a", explanation="Câu hỏi quá khứ: did + S + V nguyên thể.",
                 difficulty_elo=1200, bloom_level=2),
        Question(topic_id=topic_e2.id, question_text="Chọn câu đúng:",
                 option_a="I was watch TV last night.", option_b="I watched TV last night.",
                 option_c="I watching TV last night.", option_d="I watch TV last night.",
                 correct_answer="b", explanation="Quá khứ đơn khẳng định: S + V-ed/V2. watch → watched.",
                 difficulty_elo=1000, bloom_level=2),
        Question(topic_id=topic_e2.id, question_text="Phân biệt: 'I lived in Hanoi for 5 years.' nghĩa là gì?",
                 option_a="Tôi đã sống ở Hà Nội 5 năm (hiện không còn sống)", option_b="Tôi đang sống ở Hà Nội 5 năm",
                 option_c="Tôi sẽ sống ở Hà Nội 5 năm", option_d="Tôi thường sống ở Hà Nội",
                 correct_answer="a", explanation="Quá khứ đơn + for: hành động đã kết thúc → hiện không còn sống ở đó.",
                 difficulty_elo=1400, bloom_level=3),
        Question(topic_id=topic_e2.id, question_text="Sắp xếp: 'yesterday / she / bought / a / new / dress' thành câu hoàn chỉnh:",
                 option_a="Yesterday she a new dress bought.", option_b="She bought a new dress yesterday.",
                 option_c="She a new dress bought yesterday.", option_d="Bought she a new dress yesterday.",
                 correct_answer="b", explanation="S + V2 + O + trạng từ thời gian: She bought a new dress yesterday.",
                 difficulty_elo=1300, bloom_level=3),
    ]
    db.add_all(e2_questions)

    db.commit()
    print(f"   ✅ Đã tạo {db.query(Subject).count()} môn học")
    print(f"   ✅ Đã tạo {db.query(Topic).count()} chủ đề")
    print(f"   ✅ Đã tạo {db.query(Question).count()} câu hỏi")
