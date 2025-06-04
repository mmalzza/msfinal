import PyPDF2
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io

def fill_pdf(input_pdf, output_pdf, data):
    """
    PDF 파일에 데이터를 입력하는 함수
    """
    try:
        # 한글 폰트 등록
        pdfmetrics.registerFont(TTFont('MalgunGothic', 'C:/Windows/Fonts/malgun.ttf'))
        # 체크표시를 위한 폰트 등록 (Arial Unicode MS 사용)
        pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))

        # 기존 PDF 읽기
        with open(input_pdf, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            pdf_writer = PyPDF2.PdfWriter()

            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]

                # 새 캔버스 생성
                packet = io.BytesIO()
                can = canvas.Canvas(packet, pagesize=letter)
                can.setFont('MalgunGothic', 10)

                # 각 필드에 데이터 입력
                for field, value in data.items():
                    if field in ["FOREIGN  RESIDENT  REGISTRATION", "REISSUANCE OF REGISTRATION CARD", "EXTENSION  OF  SOJOURN  PERIOD", "CHANGE  OF  STATUS  OF  SOJOURN", "GRANTING  STATUS  OF  SOJOURN", "ENGAGE IN ACTIVITIES NOT COVERED BY THE STATUS OF SOJOURN", "CHANGE  OR  ADDITION  OF  WORKPLACE", "REENTRY  PERMIT  (SINGLE,  MULTIPLE)", "ALTERATION  OF  RESIDENCE", "CHANGE OF INFORMATION ON REGISTRATION", "boy", "girl", "Non-school", "Elementary", "Middle", "High", "Accredited school by Education Office", "Non-accredited, Alternative school"]:
                        if value.lower() == 'y' or value == '1':
                            x1, y1, x2, y2 = get_field_area(field)
                            # 체크박스 중앙 좌표 계산
                            center_x = x1 + (x2 - x1) / 2
                            center_y = y1 + (y2 - y1) / 2
                            # 체크 표시(올바른 방향)
                            can.setLineWidth(2)
                            can.line(center_x - 4, center_y, center_x, center_y - 4)      # 왼쪽 아래 → 중앙 위
                            can.line(center_x, center_y - 4, center_x + 6, center_y + 4)  # 중앙 위 → 오른쪽 아래
                            can.setLineWidth(1)
                    elif field in ["Status to apply for1", "Status to apply for2", "Status to apply for3", "Passport Issue Date", "Passport Expiry Date", "Address In Korea", "Telephone No", "Cell phone No", "Address  In  Home  Country", "Phone No1", "Name of School", "Phone No2", "Current Workplace", "Business Registration No1", "Phone No3", "New Workplace", "Business Registration No2", "Phone No4", "Annual Income Amount", "Occupation", "Intended Period Of Reentry", "E-Mail", "Refund Bank Account No. only for Foreign Resident Registration", "Date of application"]:
                        x1, y1, x2, y2 = get_field_area(field)
                        draw_text_in_area_centered(can, str(value), x1, y1, x2, y2)
                    elif field in ['Surname', 'Givenname', 'Year', 'month', 'day', 'nationality', 'passport_no']:
                        x1, y1, x2, y2 = get_field_area(field)
                        draw_text_in_area_centered(can, str(value), x1, y1, x2, y2)

                can.save()
                packet.seek(0)

                new_pdf = PyPDF2.PdfReader(packet)
                page.merge_page(new_pdf.pages[0])
                pdf_writer.add_page(page)

            # 결과 저장
            with open(output_pdf, 'wb') as output_file:
                pdf_writer.write(output_file)

        print(f"PDF 파일이 성공적으로 생성되었습니다: {output_pdf}")

    except Exception as e:
        print(f"PDF 파일 생성 중 오류가 발생했습니다: {str(e)}")


def draw_text_in_area_centered(can, text, x1, y1, x2, y2, font_name='MalgunGothic', font_size=10):
    """
    지정된 영역 내에 중앙 정렬로 텍스트를 그리는 함수 (자동 줄바꿈)
    """
    can.setFont(font_name, font_size)
    line_height = font_size + 2
    max_width = x2 - x1
    box_height = y2 - y1

    lines = split_text_to_fit(text, max_width, font_name, font_size)
    total_text_height = len(lines) * line_height
    start_y = y1 + (box_height - total_text_height) / 2 + (line_height * (len(lines) - 1))

    for i, line in enumerate(lines):
        text_width = pdfmetrics.stringWidth(line, font_name, font_size)
        text_x = x1 + (max_width - text_width) / 2
        text_y = start_y - i * line_height
        can.drawString(text_x, text_y, line)


def split_text_to_fit(text, max_width, font_name, font_size):
    """
    영역 너비에 맞게 텍스트를 줄 단위로 나누는 함수
    """
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        if pdfmetrics.stringWidth(test_line, font_name, font_size) <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    return lines


def open_pdf(pdf_path):
    """
    PDF 파일을 기본 PDF 뷰어로 열기
    """
    try:
        os.startfile(pdf_path)  # Windows 기준
    except Exception as e:
        print(f"PDF 파일을 여는 중 오류가 발생했습니다: {str(e)}")
        print("생성된 PDF 파일을 수동으로 열어주세요.")


def get_field_area(field):
    """
    각 필드에 대한 텍스트 영역 좌표 반환 (x1, y1, x2, y2)
    """
    areas = {
        "FOREIGN  RESIDENT  REGISTRATION": (61, 702, 77, 688),
        "REISSUANCE OF REGISTRATION CARD": (60, 667, 75, 655),
        "EXTENSION  OF  SOJOURN  PERIOD": (61, 643, 75, 633),
        "CHANGE  OF  STATUS  OF  SOJOURN": (60, 620, 75, 609),
        "Status to apply for1": (187, 620, 209, 609),
        "GRANTING  STATUS  OF  SOJOURN": (61, 584, 74, 573),
        "Status to apply for2": (187, 583, 209, 575),
        "ENGAGE IN ACTIVITIES NOT COVERED BY THE STATUS OF SOJOURN": (219, 701, 233, 689),
        "Status to apply for3": (363, 701, 391, 691),
        "CHANGE  OR  ADDITION  OF  WORKPLACE": (219, 667, 234, 655),
        "REENTRY  PERMIT  (SINGLE,  MULTIPLE)": (219, 644, 234, 632),
        "ALTERATION  OF  RESIDENCE": (219, 619, 235, 611),
        "CHANGE OF INFORMATION ON REGISTRATION": (219, 583, 233, 574),
        'Surname': (129, 534, 263, 525),
        'Givenname': (270, 534, 428, 526),
        'Year': (148, 508, 224, 498),
        'month': (228, 507, 265, 498),
        'day': (269, 507, 305, 499),
        "boy": (364, 519, 373, 510),
        "girl": (364, 508, 374, 499),
        'nationality': (479, 523, 537, 476),
        'passport_no': (125, 475, 226, 455),
        "Passport Issue Date": (310, 472, 395, 456),
        "Passport Expiry Date": (481, 472, 539, 457),
        'Address In Korea': (128, 452, 536, 435),
        "Telephone No": (185, 430, 295, 420),
        "Cell phone No": (418, 430, 540, 421),
        "Address  In  Home  Country": (185, 418, 414, 400),
        "Phone No1": (484, 417, 537, 401),
        "Non-school": (159, 396, 168, 387),
        "Elementary": (212, 396, 220, 388),
        "Middle": (247, 396, 255, 387),
        "High": (277, 397, 283, 387),
        "Name of School": (365, 396, 415, 378),
        "Phone No2": (484, 395, 539, 379),
        "Accredited school by Education Office": (367, 374, 377, 365),
        "Non-accredited, Alternative school": (504, 375, 512, 365),
        "Current Workplace": (207, 356, 258, 335),
        "Business Registration No1": (355, 355, 415, 334),
        "Phone No3": (481, 355, 529, 335),
        "New Workplace": (208, 335, 259, 314),
        "Business Registration No2": (354, 335, 415, 313),
        "Phone No4": (481, 335, 537, 313),
        "Annual Income Amount": (207, 313, 253, 300),
        "Occupation": (481, 313, 531, 300),
        "Intended Period Of Reentry": (207, 299, 259, 287),
        "E-Mail": (355, 299, 532, 286),
        "Refund Bank Account No. only for Foreign Resident Registration": (354, 285, 543, 266),
        "Date of application": (207, 265, 293, 253)
    }
    return areas.get(field, (100, 100, 300, 120))


def main():
    print("외국인등록신청서 작성")
    print("-" * 50)

    data = {}
    input_pdf = "외국인등록신청서.pdf"
    output_pdf = "외국인등록신청서_작성완료.pdf"

    # 각 입력마다 PDF 생성
    def update_pdf():
        if os.path.exists(input_pdf):
            fill_pdf(input_pdf, output_pdf, data)
        else:
            print(f"입력 PDF 파일을 찾을 수 없습니다: {input_pdf}")

    data["FOREIGN  RESIDENT  REGISTRATION"] = input('외국인 등록에 해당하십니까? (y/n): ')
    update_pdf()

    data["REISSUANCE OF REGISTRATION CARD"] = input('등록증 재발급에 해당하십니까? (y/n): ')
    update_pdf()

    data["EXTENSION  OF  SOJOURN  PERIOD"] = input('체류기간 연장허가에 해당하십니까? (y/n): ')
    update_pdf()

    change_status = input('체류자격 변경하기에 해당하십니까? (y/n): ')
    if change_status.lower() == 'y':
        data["CHANGE  OF  STATUS  OF  SOJOURN"] = 'y'
        data["Status to apply for1"] = input('희망자격은 무엇입니까?: ')
        update_pdf()

    granting_status = input('체류자격 부여에 해당하십니까? (y/n): ')
    if granting_status.lower() == 'y':
        data["GRANTING  STATUS  OF  SOJOURN"] = 'y'
        data["Status to apply for2"] = input('희망자격은 무엇입니까?: ')
        update_pdf()

    engage_activities = input('체류자격 외 활동허가에 해당하십니까? (y/n): ')
    if engage_activities.lower() == 'y':
        data["ENGAGE IN ACTIVITIES NOT COVERED BY THE STATUS OF SOJOURN"] = 'y'
        data["Status to apply for3"] = input('희망자격은 무엇입니까?: ')
        update_pdf()

    change_workplace = input('근무처 변경ㆍ추가허가 / 신고에 해당하십니까? (y/n): ')
    if change_workplace.lower() == 'y':
        data["CHANGE  OR  ADDITION  OF  WORKPLACE"] = 'y'
        update_pdf()

    reentry_permit = input('재입국허가 (단수, 복수) 에 해당하십니까? (y/n): ')
    if reentry_permit.lower() == 'y':
        data["REENTRY  PERMIT  (SINGLE,  MULTIPLE)"] = 'y'
        update_pdf()

    alteration_residence = input('체류지 변경신고에 해당하십니까? (y/n): ')
    if alteration_residence.lower() == 'y':
        data["ALTERATION  OF  RESIDENCE"] = 'y'
        update_pdf()

    change_info = input('등록사항 변경신고에 해당하십니까? (y/n): ')
    if change_info.lower() == 'y':
        data["CHANGE OF INFORMATION ON REGISTRATION"] = 'y'
        update_pdf()

    data['Surname'] = input("성을 입력하세요: ")
    update_pdf()
    data['Givenname'] = input("이름을 입력하세요: ")
    update_pdf()
    data['Year'] = input("생년을 입력하세요: ")
    update_pdf()
    data['month'] = input("생월을 입력하세요: ")
    update_pdf()
    data['day'] = input("생일을 입력하세요: ")
    update_pdf()

    # 성별 질문
    gender = input('남자입니까 여자입니까?(남자1, 여자2): ')
    if gender == '1':
        data['boy'] = 'y'
    elif gender == '2':
        data['girl'] = 'y'
    update_pdf()

    data['nationality'] = input("국가을 입력하세요: ")
    update_pdf()
    data['passport_no'] = input("여권 번호을 입력하세요: ")
    update_pdf()
    data['Passport Issue Date'] = input("여권 발급일자를 입력하세요: ")
    update_pdf()
    data['Passport Expiry Date'] = input("여권 유효기간을 입력하세요: ")
    update_pdf()
    data['Address In Korea'] = input("대한민국 내 주소를 입력하세요: ")
    update_pdf()
    data['Telephone No'] = input("전화번호를 입력하세요: ")
    update_pdf()
    data['Cell phone No'] = input("휴대전화를 입력하세요: ")
    update_pdf()
    data['Address  In  Home  Country'] = input("본국주소를 입력하세요: ")
    update_pdf()
    data['Phone No1'] = input("본국 전화번호를 입력하세요: ")
    update_pdf()

    # 재학여부
    school_status = input('재학여부를 선택하세요(미취학(1),초등학생(2),중학생(3),고등학생(4)): ')
    if school_status == '1':
        data['Non-school'] = 'y'
    elif school_status == '2':
        data['Elementary'] = 'y'
    elif school_status == '3':
        data['Middle'] = 'y'
    elif school_status == '4':
        data['High'] = 'y'
    update_pdf()

    # 2,3,4(초등,중등,고등)만 추가 질문
    if school_status in ['2', '3', '4']:
        data['Name of School'] = input('학교이름을 입력하세요: ')
        update_pdf()
        data['Phone No2'] = input('학교전화번호를 입력하세요: ')
        update_pdf()
        school_type = input('학교 종류를 입력하세요((1)교육청 인가 학교(2)교육청 비인가/대안학교): ')
        if school_type == '1':
            data['Accredited school by Education Office'] = 'y'
        elif school_type == '2':
            data['Non-accredited, Alternative school'] = 'y'
        update_pdf()

    # 추가 질문
    data['Current Workplace'] = input("현 근무처를 입력하세요: ")
    update_pdf()
    data['Business Registration No1'] = input("현 근무처 사업자등록번호를 입력하세요: ")
    update_pdf()
    data['Phone No3'] = input("현 근무처 전화번호를 입력하세요: ")
    update_pdf()
    data['New Workplace'] = input("새로운 예정 근무처를 입력하세요: ")
    update_pdf()
    data['Business Registration No2'] = input("새로운 예정 근무처의 사업자등록번호를 입력하세요: ")
    update_pdf()
    data['Phone No4'] = input("새로운 예정 근무처의 전화번호를 입력하세요: ")
    update_pdf()
    data['Annual Income Amount'] = input("연 소득금액을 입력하세요(만원): ")
    update_pdf()
    data['Occupation'] = input("직업을 입력하세요: ")
    update_pdf()
    data['Intended Period Of Reentry'] = input("재입국 신청 기간을 입력하세요: ")
    update_pdf()
    data['E-Mail'] = input("전자우편을 입력하세요: ")
    update_pdf()
    data['Refund Bank Account No. only for Foreign Resident Registration'] = input("반환용 계좌번호(외국인등록 및 외국인등록증 재발급 신청 시에만 기재)을 입력하세요: ")
    update_pdf()
    data['Date of application'] = input("신청일을 입력하세요: ")
    update_pdf()

    print("\n모든 입력이 완료되었습니다. 최종 PDF가 생성되었습니다.")


if __name__ == "__main__":
    main()
