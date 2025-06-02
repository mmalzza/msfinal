import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from openai import AzureOpenAI
from difflib import SequenceMatcher
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain_openai import AzureChatOpenAI

load_dotenv()

# 환경 설정
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
AZURE_SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX")
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

TOP_N_DOCUMENTS = 5
STRICTNESS = 3

app = Flask(__name__)
CORS(app)

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

# 실행
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
