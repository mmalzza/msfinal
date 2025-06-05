import os
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from dotenv import load_dotenv
from openai import AzureOpenAI
from difflib import SequenceMatcher
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain_openai import AzureChatOpenAI
from werkzeug.utils import secure_filename
import json
from pdf_filler import fill_pdf
from complaint_filler import fill_pdf as fill_complaint_pdf

load_dotenv()

# 환경 설정
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
AZURE_SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX")
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
search_endpoint = os.getenv("AZURE_AI_SEARCH_ENDPOINT")
search_key = os.getenv("AZURE_AI_SEARCH_KEY")
search_index = "law-index"
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")

TOP_N_DOCUMENTS = 5
STRICTNESS = 3

app = Flask(__name__)
CORS(app)

# 공통 설정
UPLOAD_FOLDER = "./uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = {'pdf'}

# 외국인등록신청서 설정
INPUT_PDF_FOREIGNER = "외국인등록신청서.pdf"
OUTPUT_PDF_FOREIGNER_NAME = "외국인등록신청서_작성완료.pdf"
OUTPUT_PDF_FOREIGNER_PATH = os.path.join(UPLOAD_FOLDER, OUTPUT_PDF_FOREIGNER_NAME)

# 진정서 설정
INPUT_PDF_COMPLAINT = "진정서.pdf"
OUTPUT_PDF_COMPLAINT_NAME = "진정서_작성완료.pdf"
OUTPUT_PDF_COMPLAINT_PATH = os.path.join(UPLOAD_FOLDER, OUTPUT_PDF_COMPLAINT_NAME)

# 현재 상태 저장
current_data_foreigner = {}
current_data_complaint = {}

# LLM 설정
llm = AzureChatOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    deployment_name=DEPLOYMENT_NAME,
    api_version=API_VERSION,
    api_key=AZURE_OPENAI_API_KEY,
    temperature=0.7,
    top_p=0.95,
    max_tokens=1500
)

# Prompt Template
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an AI assistant that helps people find information. 
Your task is to provide detailed and accurate answers based on the provided context.
Follow these guidelines:
1. Use the search results as your primary source of information
2. Include specific details and examples when available
3. If the search results are not sufficient, acknowledge the limitations
4. Maintain context from previous conversations when relevant
5. Structure your response in a clear and organized manner
6. If there are multiple relevant pieces of information, present them in a logical order"""),
    ("human", "{query}")
])

# Chain 정의
chain = (
    {"query": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 유사 문장 제거
def remove_redundant_sentences(text, threshold=0.85):
    sentences = text.strip().split('\n')
    result = []
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        if not any(SequenceMatcher(None, sentence, r).ratio() > threshold for r in result):
            result.append(sentence)
    return '\n'.join(result)

# Azure Search 결과 가져오기
def get_search_results(query, top_n=TOP_N_DOCUMENTS, strictness=STRICTNESS):
    client = AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        api_version=API_VERSION,
    )

    completion = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": "You are an AI assistant that helps people find information. Provide detailed and accurate information from the search results."},
            {"role": "user", "content": query}
        ],
        max_tokens=1500,
        temperature=0.7,
        top_p=0.95,
        stream=False,
        extra_body={
            "data_sources": [{
                "type": "azure_search",
                "parameters": {
                    "endpoint": AZURE_SEARCH_ENDPOINT,
                    "index_name": AZURE_SEARCH_INDEX,
                    "semantic_configuration": "default",
                    "query_type": "vector_semantic_hybrid",
                    "in_scope": True,
                    "strictness": strictness,
                    "top_n_documents": top_n,
                    "authentication": {
                        "type": "api_key",
                        "key": AZURE_SEARCH_KEY
                    },
                    "embedding_dependency": {
                        "type": "deployment_name",
                        "deployment_name": "text-embedding-ada-002"
                    }
                }
            }]
        }
    )

    return completion.choices[0].message.content

# 핵심 응답 함수
def enhanced_rag_chat(query, chat_history):
    search_results = get_search_results(query)

    # 최근 대화 3개 유지
    context = "Previous Conversation (for context):\n"
    for prev_q, prev_a in chat_history[-3:]:
        context += f"- Q: {prev_q}\n  A: {prev_a[:300]}...\n"

    prompt_context = f"""
[사용자 질문]
{query}

[검색 결과 요약]
{search_results}

[지시 사항]
- 위 검색 결과만을 기반으로 정확하고 구체적인 정보를 제공합니다.
- 정보가 중복되지 않도록 정리합니다.
- 항목별로 제목(굵게)을 붙여 깔끔하게 정리합니다.
- 모든 문장은 완결된 서술형으로 작성합니다.
- 대화 흐름을 고려해 맥락 있는 문장으로 연결합니다.
- 출처 링크나 파일명은 출력하지 않습니다.
"""

    #raw_response = chain.invoke(prompt_context)
    raw_response = chain.invoke({"query": prompt_context})
    cleaned_response = remove_redundant_sentences(raw_response)
    chat_history.append((query, cleaned_response))

    return cleaned_response, chat_history

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# API 엔드포인트
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        query = data.get("query", "")
        history = data.get("history", [])
        chat_history = [(item["question"], item["answer"]) for item in history]

        if not query:
            return jsonify({"error": "query가 비어있습니다."}), 400

        response, chat_history = enhanced_rag_chat(query, chat_history)
        history_output = [{"question": q, "answer": a} for q, a in chat_history]
        return jsonify({"response": response, "history": history_output})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# 유저 정보 (예시)
@app.route('/userinfo', methods=['GET'])
def get_user_info():
    return jsonify({
        'name': 'John Doe',
        'nationality': '필리핀',
        'passport': 'AB1234567',
        'visaType': 'E-9 (비전문취업)',
        'entryDate': '2024-07-31',
        'visaExpiry': '2025-07-30'
    })

# 유저 정보 업데이트
@app.route('/update', methods=['POST'])
def update_info():
    data = request.json
    print('Received from client:', data)
    return jsonify({'message': '정보 업데이트 완료'})

# 외국인등록신청서 관련 라우터
@app.route('/api/update_foreigner', methods=['POST'])
def update_foreigner_pdf():
    try:
        data = request.json
        field = data.get('field')
        value = data.get('value')

        current_data_foreigner[field] = value

        if os.path.exists(INPUT_PDF_FOREIGNER):
            fill_pdf(INPUT_PDF_FOREIGNER, OUTPUT_PDF_FOREIGNER_PATH, current_data_foreigner)
            return jsonify({
                'success': True,
                'message': f'PDF 파일이 성공적으로 생성되었습니다: {OUTPUT_PDF_FOREIGNER_NAME}',
                'pdf_url': f'/uploads/{OUTPUT_PDF_FOREIGNER_NAME}?t={os.path.getmtime(OUTPUT_PDF_FOREIGNER_PATH)}'
            })
        else:
            return jsonify({'success': False, 'message': '외국인등록신청서 원본 파일이 없습니다.'}), 404

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/get_foreigner_pdf_url')
def get_foreigner_pdf_url():
    try:
        if os.path.exists(OUTPUT_PDF_FOREIGNER_PATH):
            pdf_url = request.host_url + 'uploads/' + OUTPUT_PDF_FOREIGNER_NAME + '?t=' + str(os.path.getmtime(OUTPUT_PDF_FOREIGNER_PATH))
            return jsonify({'success': True, 'pdfUrl': pdf_url})
        else:
            return jsonify({'success': False, 'message': 'PDF 파일이 없습니다.'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/reset_foreigner', methods=['POST'])
def reset_foreigner_data():
    global current_data_foreigner
    current_data_foreigner = {}
    return jsonify({'success': True, 'message': '외국인등록신청서 데이터 초기화 완료'})


# 진정서 관련 라우터
@app.route('/api/update_complaint', methods=['POST'])
def update_complaint_pdf():
    try:
        data = request.json
        field = data.get('field')
        value = data.get('value')

        current_data_complaint[field] = value

        if os.path.exists(INPUT_PDF_COMPLAINT):
            fill_complaint_pdf(INPUT_PDF_COMPLAINT, OUTPUT_PDF_COMPLAINT_PATH, current_data_complaint)
            return jsonify({
                'success': True,
                'message': f'진정서 PDF가 성공적으로 생성되었습니다: {OUTPUT_PDF_COMPLAINT_NAME}',
                'pdf_url': f'/uploads/{OUTPUT_PDF_COMPLAINT_NAME}?t={os.path.getmtime(OUTPUT_PDF_COMPLAINT_PATH)}'
            })
        else:
            return jsonify({'success': False, 'message': '진정서 원본 파일이 없습니다.'}), 404

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/get_complaint_pdf_url')
def get_complaint_pdf_url():
    try:
        if os.path.exists(OUTPUT_PDF_COMPLAINT_PATH):
            pdf_url = request.host_url + 'uploads/' + OUTPUT_PDF_COMPLAINT_NAME + '?t=' + str(os.path.getmtime(OUTPUT_PDF_COMPLAINT_PATH))
            return jsonify({'success': True, 'pdfUrl': pdf_url})
        else:
            return jsonify({'success': False, 'message': 'PDF 파일이 없습니다.'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/reset_complaint', methods=['POST'])
def reset_complaint_data():
    global current_data_complaint
    current_data_complaint = {}
    return jsonify({'success': True, 'message': '진정서 데이터 초기화 완료'})

# 파일 업로드 및 제공
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    try:
        return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), mimetype='application/pdf')
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '파일이 없습니다.'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '파일 이름이 없습니다.'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        file_url = request.host_url + 'uploads/' + filename
        return jsonify({'success': True, 'file_url': file_url})

    return jsonify({'success': False, 'message': '허용되지 않는 파일 형식입니다.'}), 400

def complaint_content(query):
      client = AzureOpenAI(
          azure_endpoint=endpoint,
          api_key=subscription_key,
          api_version="2025-01-01-preview",
      )

      chat_prompt = [
          {
              "role": "system",
              "content":  "당신은 한국의 근로기준법, 최저임금법, 외국인근로자의 고용 등에 관한 법률, 퇴직급여보장법에 정통한 AI 노무사입니다. \n당신의 역할은 외국인 근로자가 제공한 정보를 바탕으로, 실제 고용노동부에 제출 가능한 임금체불 진정서의 '진정 내용' 부분을 500자 이내로 전문적으로 작성하는 것입니다.\n\n작성 시 유의사항:\n- 문장은 정중하고 간결하며 객관적인 진술 형태로 작성합니다.\n- 사실관계, 법률 위반 요소(퇴직금 미지급, 체불임금 등), 대응 과정 등을 포함합니다.\n- 관련 법령에 근거하여 체불 사유가 위법임을 명시하는 문장을 포함합니다.\n- JSON의 각 항목(work_detail, period, location, wage, response)을 모두 반영하십시오.\n- 불필요한 반복 없이 자연스럽게 연결된 문단으로 구성하십시오.\n- 출력은 '진정인은'으로 시작하고 내용 문단 한 개만 출력하십시오.\n- 반드시 500자를 초과하지 않도록 하십시오.\n"

          },
          {
              "role": "user",
              "content": query}
              ]
      
      messages = chat_prompt

      completion = client.chat.completions.create(
          model=deployment,
          messages=messages,
          max_tokens=800,
          temperature=0.7,
          top_p=0.95,
          frequency_penalty=0,
          presence_penalty=0,
          stop=None,
          stream=False,
          extra_body={
            "data_sources": [{
                "type": "azure_search",
                "parameters": {
                  "endpoint": f"{search_endpoint}",
                  "index_name": "law-index",
                  "semantic_configuration": "default",
                  "query_type": "vector_semantic_hybrid",
                  "fields_mapping": {},
                  "in_scope": True,
                  "filter": None,
                  "strictness": 2,
                  "top_n_documents": 5,
                  "authentication": {
                    "type": "api_key",
                    "key": f"{search_key}"
                  },
                  "embedding_dependency": {
                    "type": "deployment_name",
                    "deployment_name": "text-embedding-ada-002"
                  }
                }
              }]
          }
      )

      return completion.choices[0].message.content

@app.route('/api/generate_complaint_content', methods=['POST'])
def generate_complaint_content():
    try:
        data = request.json

        # 필수 필드가 다 있는지 확인
        required_fields = ['work_detail', 'period', 'location', 'wage', 'response', 'extra_info']
        if not all(field in data for field in required_fields):
            return jsonify({'success': False, 'message': '필수 필드 누락'}), 400

        # 하나의 텍스트로 이어붙이기
        query = "\n\n".join(f"{field}: {data[field]}" for field in required_fields)

        result = complaint_content(query)
        return jsonify({'success': True, 'content': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 실행
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
