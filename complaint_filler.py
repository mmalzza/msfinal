import PyPDF2
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
from complaint import complaint_content


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

            # 페이지별 필드 정의
            page_fields = {
                1: ["cname", "cResident Registration", "cAddress", "cPhone (Landline)", 
                    "cPhone (Mobile)", "cEmail", "cReceive Processing Status Notifications yes",
                    "cReceive Processing Status Notifications no", "cReceive Notifications via Labor Portal yes",
                    "cReceive Notifications via Labor Portal no", "rname", "rPhone", "rAddress",
                    "Workplace", "Construction site", "Name of Business", "Actual place of business",
                    "rePhone", "Number of Employees"],
                2: ["Date of Employment", "Date of Resignation/Termination", "Total Amount of Unpaid Wages",
                    "Resigned/terminated", "Currently employed", "Amount of Unpaid Severance Pay",
                    "Other Unpaid Amounts", "Job Description", "Wage Payment Date", "Written", "Oral", "Details"]
            }

            # 각 페이지 처리
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                packet = io.BytesIO()
                can = canvas.Canvas(packet, pagesize=letter)
                can.setFont('MalgunGothic', 10)

                # 현재 페이지의 필드만 처리
                current_page_fields = page_fields.get(page_num + 1, [])
                
                for field, value in data.items():
                    if field in current_page_fields:
                        # 체크박스 필드 처리
                        if field in ["cReceive Processing Status Notifications yes", "cReceive Processing Status Notifications no",
                                   "cReceive Notifications via Labor Portal yes", "cReceive Notifications via Labor Portal no",
                                   "Workplace", "Construction site", "Resigned/terminated", "Currently employed",
                                   "Written", "Oral"]:
                            if value.lower() == 'y':
                                x1, y1, x2, y2 = get_field_area(field, page_num + 1)
                                center_x = x1 + (x2 - x1) / 2
                                center_y = y1 + (y2 - y1) / 2
                                can.setLineWidth(2)
                                can.line(center_x - 4, center_y, center_x, center_y - 4)
                                can.line(center_x, center_y - 4, center_x + 6, center_y + 4)
                                can.setLineWidth(1)
                        # 텍스트 필드 처리
                        else:
                            x1, y1, x2, y2 = get_field_area(field, page_num + 1)
                            draw_text_in_area_centered(can, str(value), x1, y1, x2, y2)

                can.save()
                packet.seek(0)
                new_pdf = PyPDF2.PdfReader(packet)
                
                # 새로 생성된 PDF가 페이지를 가지고 있는지 확인
                if len(new_pdf.pages) > 0:
                    page.merge_page(new_pdf.pages[0])
                pdf_writer.add_page(page)

            # 결과 저장
            with open(output_pdf, 'wb') as output_file:
                pdf_writer.write(output_file)

        print(f"PDF 파일이 성공적으로 생성되었습니다: {output_pdf}")
        
        # PDF 파일이 이미 열려있다면 닫고 다시 열기
        try:
            # 여러 PDF 뷰어 프로세스 종료 시도
            pdf_viewers = ['AcroRd32.exe', 'Acrobat.exe', 'FoxitReader.exe', 'SumatraPDF.exe']
            for viewer in pdf_viewers:
                try:
                    os.system(f'taskkill /F /IM {viewer} 2>nul')
                except:
                    pass
        except:
            pass
        open_pdf(output_pdf)

    except Exception as e:
        print(f"PDF 파일 생성 중 오류가 발생했습니다: {str(e)}")
        print("오류 상세 정보:", e.__class__.__name__)
        import traceback
        print(traceback.format_exc())

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

def get_field_area(field, page_num):
    """
    각 필드에 대한 텍스트 영역 좌표 반환 (x1, y1, x2, y2)
    page_num: 1 또는 2 (페이지 번호)
    """
    areas = {
        # 첫 번째 페이지 필드
        1: {
            "cname": (142, 632, 261, 577),
            "cResident Registration": (342, 631, 505, 577),
            "cAddress": (141, 575, 506, 548),
            "cPhone (Landline)": (141, 546, 262, 505),
            "cPhone (Mobile)": (343, 547, 504, 507),
            "cEmail": (142, 505, 504, 464),
            "cReceive Processing Status Notifications yes": (147, 441, 156, 432),
            "cReceive Processing Status Notifications no": (197, 441, 205, 433),
            "cReceive Notifications via Labor Portal yes": (347, 441, 355, 433),
            "cReceive Notifications via Labor Portal no": (402, 441, 411, 433),
            "rname": (140, 333, 264, 306),
            "rPhone": (342, 333, 506, 305),
            "rAddress": (141, 305, 505, 278),
            "Workplace": (146, 269, 157, 258),
            "Construction site": (227, 269, 237, 259),
            "Name of Business": (141, 237, 505, 200),
            "Actual place of business": (143, 199, 506, 135),
            "rePhone": (143, 133, 262, 93),
            "Number of Employees": (341, 132, 506, 94)
        },
        # 두 번째 페이지 필드
        2: {
            "Date of Employment": (141, 765, 263, 717),
            "Date of Resignation/Termination": (343, 765, 502, 718),
            "Total Amount of Unpaid Wages": (143, 713, 263, 664),
            "Resigned/terminated": (347, 712, 356, 704),
            "Currently employed": (347, 687, 356, 677),
            "Amount of Unpaid Severance Pay": (142, 662, 263, 605),
            "Other Unpaid Amounts": (341, 663, 505, 607),
            "Job Description": (141, 604, 505, 566),
            "Wage Payment Date": (142, 565, 263, 509),
            "Written": (347, 547, 357, 537),
            "Oral": (417, 547, 426, 537),
            "Details": (142, 508, 506, 386)
        }
    }
    return areas.get(page_num, {}).get(field, (100, 100, 300, 120))

def main():
    print("진정서 작성")
    print("-" * 50)

    data = {}
    input_pdf = "진정서.pdf"
    output_pdf = "진정서_작성완료.pdf"

    # 각 입력마다 PDF 생성
    def update_pdf():
        if os.path.exists(input_pdf):
            fill_pdf(input_pdf, output_pdf, data)
        else:
            print(f"입력 PDF 파일을 찾을 수 없습니다: {input_pdf}")

    # 첫 번째 페이지 정보 입력
    print("\n[첫 번째 페이지 - 진정인 및 사업장 정보]")
    print("-" * 50)
    
    # 진정인 정보 입력
    print("\n[진정인 정보]")
    data["cname"] = input("진정인 성명을 입력해주세요: ")
    update_pdf()
    
    data["cResident Registration"] = input("진정인 주민등록번호를 입력해주세요: ")
    update_pdf()
    
    data["cAddress"] = input("진정인 주소를 입력해 주세요: ")
    update_pdf()
    
    data["cPhone (Landline)"] = input("진정인 전화번호를 입력해 주세요: ")
    update_pdf()
    
    data["cPhone (Mobile)"] = input("진정인 휴대전화번호를 입력해주세요: ")
    update_pdf()
    
    data["cEmail"] = input("진정인 전자우편주소를 입력해 주세요: ")
    update_pdf()

    # 처리 상황 수신여부
    process_status = input("\n처리 상황 수신여부에 동의하십니까? (y/n): ")
    if process_status.lower() == 'y':
        data["cReceive Processing Status Notifications yes"] = 'y'
    else:
        data["cReceive Processing Status Notifications no"] = 'y'
    update_pdf()

    # 노동포털 통지여부
    labor_portal = input("노동포털 통지여부에 동의하십니까? (y/n): ")
    if labor_portal.lower() == 'y':
        data["cReceive Notifications via Labor Portal yes"] = 'y'
    else:
        data["cReceive Notifications via Labor Portal no"] = 'y'
    update_pdf()

    # 피진정인 정보 입력
    print("\n[피진정인 정보]")
    data["rname"] = input("피진정인 성명을 입력해주세요: ")
    update_pdf()
    
    data["rPhone"] = input("피진정인 연락처를 입력해 주세요: ")
    update_pdf()
    
    data["rAddress"] = input("피진정인 주소를 입력해 주세요: ")
    update_pdf()

    # 사업장/공사현장 선택
    workplace_type = input("\n사업장 공사현장중 어떤것입니까? (사업장(1), 공사현장(2)): ")
    if workplace_type == '1':
        data["Workplace"] = 'y'
    else:
        data["Construction site"] = 'y'
    update_pdf()

    # 사업장 정보 입력
    print("\n[사업장 정보]")
    data["Name of Business"] = input("사업장명을 입력해 주세요: ")
    update_pdf()
    
    data["Actual place of business"] = input("사업장 주소를 입력해 주세요: ")
    update_pdf()
    
    data["rePhone"] = input("사업장전화번호를 입력해 주세요: ")
    update_pdf()
    
    data["Number of Employees"] = input("근로자 수를 입력해 주세요: ")
    update_pdf()

    # 두 번째 페이지로 이동
    print("\n[두 번째 페이지 - 근로 정보]")
    print("-" * 50)
    input("첫 번째 페이지 입력이 완료되었습니다. Enter를 눌러 두 번째 페이지로 이동하세요...")

    # 근로 정보 입력
    print("\n[근로 정보]")
    data["Date of Employment"] = input("입사일을 입력해 주세요: ")
    update_pdf()
    
    data["Date of Resignation/Termination"] = input("퇴사일을 입력해 주세요: ")
    update_pdf()
    
    data["Total Amount of Unpaid Wages"] = input("체불임금 총액을 입력해 주세요: ")
    update_pdf()

    # 퇴직 여부
    employment_status = input("\n퇴직 여부가 어떻게 되십니까? (퇴직(1), 재직(2)): ")
    if employment_status == '1':
        data["Resigned/terminated"] = 'y'
    else:
        data["Currently employed"] = 'y'
    update_pdf()

    data["Amount of Unpaid Severance Pay"] = input("체불 퇴직금액을 입력해 주세요: ")
    update_pdf()
    
    data["Other Unpaid Amounts"] = input("기타 체불 금액을 입력해 주세요: ")
    update_pdf()
    
    data["Job Description"] = input("업무내용을 입력해 주세요: ")
    update_pdf()
    
    data["Wage Payment Date"] = input("임금 지급일을 입력해 주세요: ")
    update_pdf()

    # 근로계약방법
    contract_type = input("\n근로계약방법이 서면입니까 구두입니까? (서면(1), 구두(2)): ")
    if contract_type == '1':
        data["Written"] = 'y'
    else:
        data["Oral"] = 'y'
    update_pdf()

    # 진정 내용 입력
    work_detail = input("1. 어떤 일을 하셨나요? (직무와 담당한 작업 내용을 알려주세요)")
    period = input("2. 언제부터 언제까지 일하셨고, 그 중 임금을 받지 못한 기간은 언제인가요?")
    location = input("3. 어느 지역, 어떤 회사(또는 인력사무소)에서 일하셨나요? 정확한 주소를 알려주세요.")
    wage = input("4. 월급은 원래 얼마였고, 체불된 금액은 총 얼마인가요?")
    response= input("5. 임금 체불에 대해 사업주에게 요청해보신 적이 있나요? 어떤 대응이 있었나요?")
    extra_info = input("6. 추가로 제가 알아야 하는 내용을 더 알려주세요.")
    user_answer = (
    f"{{\n"
    f'  "work_detail": "{work_detail}",\n'
    f'  "period": "{period}",\n'
    f'  "location": "{location}",\n'
    f'  "wage": "{wage}",\n'
    f'  "response": "{response}",\n'
    f'  "extra_info": "{extra_info}"\n'
    f"}}"
)
    
    content = complaint_content(user_answer)
    print("\n진정 내용이 작성되었습니다:")
    data["Details"] = content
    update_pdf()

    print("\n모든 입력이 완료되었습니다. 최종 PDF가 생성되었습니다.")
    help_docs = input("\n추가 서류 안내를 도와드릴까요? (y/n): ").strip().lower()

    if help_docs == 'y':
        while True:
            print("\n※ 추가 서류 종류를 선택하세요(외국인 등록(1), 근무처 변경(2), 체류기간 연장(3), 종료(q)):")
            doc_type = input("번호를 입력하세요 (1/2/3) 또는 q: ").strip().lower()

            if doc_type == '1':
                print("\n1. 외국인 등록")
                print("  1) 신청서(별지34호 서식), 여권원본, 표준규격사진 1장, 수수료 3만원")
                print("  2) 사업자등록증 사본")
                print("  3) 외국인근로자가 교육 중(또는 외국인등록 전) 고용회사의 폐업, 휴업, 기타 외국인의 귀책사유 없이")
                print("     고용관계를 개시할 수 없어 고용노동부에서 사업장 변경을 해주는 경우 근무처변경허가가 아닌 변경된 사업장으로 외국인등록")
                print("     - 추가서류 : 고용허가서 사본, 표준근로계약서 사본")
                print("  4) 법무부 지정 의료기관에서 발급한 '마약검사확인서*'")
                print("     - '마약류 관리에 관한 법률' 제2조 제1항의 '마약류'를 말하며, 등록 시 기준으로 3개월 이내에 발급된 확인서일 것")
                print("     - 건강진단서 및 마약검사확인서는 반드시 봉투에 밀봉된 상태로 제출(개봉 불가)")
                print("  5) 체류지 입증서류")

            elif doc_type == '2':
                print("\n2. 근무처 변경")
                print("  1) 신청서(별지 34호서식), 여권 및 외국인등록증, 수수료")
                print("  2) 고용허가서 사본")
                print("  3) 표준근로계약서 사본")
                print("  4) '사업자등록증’ 등 사업장 관련 입증서류")
                print("  5) 건설업체의 경우 해당 현장 책임건설업체(원도급업체)가 작성한 '건설현장에 대한 외국인력 현황표'")
                print("     (고용노동부 「외국인 고용관리 지침 서식 참조)")

            elif doc_type == '3':
                print("\n3. 체류기간 연장")
                print("  1) 신청서(별지 34호 서식), 여권 및 외국인등록증, 수수료")
                print("  2) 고용허가서 사본")
                print("  3) 표준근로계약서 사본")
                print("  4) 사업자등록증 사본")
                print("  5) 입국 후 3년 만료 재고용에 따른 최대 1년 10개월 추가 연장의 경우")
                print("     ‘취업기간만료자 취업활동기간 연장확인서(고용노동부 발급)'")
                print("  6) 체류지 입증서류(임대차계약서, 숙소제공 확인서, 체류기간 만료예고 통지우편물, 공공요금 납부영수증, 기숙사비 영수증 등)")

            elif doc_type == 'q':
                print("\n안내를 종료합니다.")
                break

            else:
                print("잘못된 입력입니다. 1, 2, 3 중에서 선택하거나 q로 종료하세요.")

    elif help_docs == 'n':
        print("\n프로그램을 종료합니다.")
        exit()

    else:
        print("\n잘못된 입력입니다. y 또는 n으로 입력해 주세요.")
        exit()

if __name__ == "__main__":
    main() 