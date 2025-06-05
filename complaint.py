import os
import base64
from openai import AzureOpenAI
from dotenv import load_dotenv
load_dotenv()

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
search_endpoint = os.getenv("AZURE_AI_SEARCH_ENDPOINT")
search_key = os.getenv("AZURE_AI_SEARCH_KEY")
search_index = "law-index"
subscription_key = os.getenv("AZURE_OPENAI_API_KEY", "REPLACE_WITH_YOUR_KEY_VALUE_HERE")

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

      content = completion.choices[0].message.content
      return content