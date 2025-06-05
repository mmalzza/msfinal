import React, { useState, useEffect, useRef } from 'react';
import { SafeAreaView, View, Text, TextInput, TouchableOpacity, ScrollView, StyleSheet, Platform, KeyboardAvoidingView } from 'react-native';
import axios from 'axios';
import * as WebBrowser from 'expo-web-browser';
import { Ionicons } from '@expo/vector-icons';

const API_URL = 'http://192.168.45.205:5000';

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [pdfUrl, setPdfUrl] = useState('');
  const [data, setData] = useState({});
  const [pdfShown, setPdfShown] = useState(false);
  const scrollViewRef = useRef(null);
  const isFirstRender = useRef(true);

  const openPdfInSafari = async () => {
    if (pdfUrl) {
      await WebBrowser.openBrowserAsync(pdfUrl);
    }
  };

  const questions = [
    { key: "cname", question: "진정인 성명을 입력해주세요:", type: "text" },
    { key: "cResident Registration", question: "진정인 주민등록번호를 입력해주세요:", type: "text" },
    { key: "cAddress", question: "진정인 주소를 입력해 주세요:", type: "text" },
    { key: "cPhone (Landline)", question: "진정인 전화번호를 입력해 주세요:", type: "text" },
    { key: "cPhone (Mobile)", question: "진정인 휴대전화번호를 입력해주세요:", type: "text" },
    { key: "cEmail", question: "진정인 전자우편주소를 입력해 주세요:", type: "text" },
    { key: "cReceive Processing Status Notifications", question: "처리 상황 수신여부에 동의하십니까? (yes/no)", type: "radio" },
    { key: "cReceive Notifications via Labor Portal", question: "노동포털 통지여부에 동의하십니까? (yes/no)", type: "radio" },
    { key: "rname", question: "피진정인 성명을 입력해주세요:", type: "text" },
    { key: "rPhone", question: "피진정인 연락처를 입력해 주세요:", type: "text" },
    { key: "rAddress", question: "피진정인 주소를 입력해 주세요:", type: "text" },
    { key: "workplace_type", question: "사업장 공사현장중 어떤것입니까? (business/construction)", type: "radio" },
    { key: "Name of Business", question: "사업장명을 입력해 주세요:", type: "text" },
    { key: "Actual place of business", question: "사업장 주소를 입력해 주세요:", type: "text" },
    { key: "rePhone", question: "사업장전화번호를 입력해 주세요:", type: "text" },
    { key: "Number of Employees", question: "근로자 수를 입력해 주세요:", type: "number" },
    { key: "Date of Employment", question: "입사일을 입력해 주세요:", type: "date" },
    { key: "Date of Resignation/Termination", question: "퇴사일을 입력해 주세요:", type: "date" },
    { key: "Total Amount of Unpaid Wages", question: "체불임금 총액을 입력해 주세요:", type: "number" },
    { key: "employment_status", question: "퇴직 여부가 어떻게 되십니까? (resigned/employed)", type: "radio" },
    { key: "Amount of Unpaid Severance Pay", question: "체불 퇴직금액을 입력해 주세요:", type: "number" },
    { key: "Other Unpaid Amounts", question: "기타 체불 금액을 입력해 주세요:", type: "number" },
    { key: "Job Description", question: "업무내용을 입력해 주세요:", type: "textarea" },
    { key: "Wage Payment Date", question: "임금 지급일을 입력해 주세요:", type: "text" },
    { key: "contract_type", question: "근로계약방법이 서면입니까 구두입니까? (written/oral)", type: "radio" },
    { key: "work_detail", question: "1. 어떤 일을 하셨나요? (직무와 담당한 작업 내용을 알려주세요)", type: "textarea" },
    { key: "period", question: "2. 언제부터 언제까지 일하셨고, 그 중 임금을 받지 못한 기간은 언제인가요?", type: "textarea" },
    { key: "location", question: "3. 어느 지역, 어떤 회사(또는 인력사무소)에서 일하셨나요? 정확한 주소를 알려주세요.", type: "textarea" },
    { key: "wage", question: "4. 월급은 원래 얼마였고, 체불된 금액은 총 얼마인가요?", type: "textarea" },
    { key: "response", question: "5. 임금 체불에 대해 사업주에게 요청해보신 적이 있나요? 어떤 대응이 있었나요?", type: "textarea" },
    { key: "extra_info", question: "6. 추가로 제가 알아야 하는 내용을 더 알려주세요.", type: "textarea" },
  ];

  useEffect(() => {
    // 첫 렌더 시 첫 질문 보여주기
    if (isFirstRender.current) {
      isFirstRender.current = false;
      setMessages([{ type: 'bot', text: questions[0].question }]);
      return;
    }
  }, []);

  const handleSubmit = async () => {
    if (!input.trim()) return;

    const userMessage = input.trim();
    const key = questions[currentQuestion].key;

    // 사용자 메시지를 화면에 추가
    setMessages(prev => [...prev, { type: 'user', text: userMessage }]);
    setData(prevData => ({ ...prevData, [key]: userMessage }));
    setInput('');

    if (currentQuestion >= questions.length) return;

    // 서버에 PDF 데이터 업데이트 요청
    try {
      // 특수 필드 처리
      let serverField = key;
      let serverValue = userMessage;

      if (key === 'cReceive Processing Status Notifications') {
        serverField = userMessage.toLowerCase() === 'yes'
          ? 'cReceive Processing Status Notifications yes'
          : 'cReceive Processing Status Notifications no';
        serverValue = 'y';
      } else if (key === 'cReceive Notifications via Labor Portal') {
        serverField = userMessage.toLowerCase() === 'yes'
          ? 'cReceive Notifications via Labor Portal yes'
          : 'cReceive Notifications via Labor Portal no';
        serverValue = 'y';
      } else if (key === 'workplace_type') {
        serverField = userMessage.toLowerCase() === 'business'
          ? 'Workplace'
          : 'Construction site';
        serverValue = 'y';
      } else if (key === 'employment_status') {
        serverField = userMessage.toLowerCase() === 'resigned'
          ? 'Resigned/terminated'
          : 'Currently employed';
        serverValue = 'y';
      } else if (key === 'contract_type') {
        serverField = userMessage.toLowerCase() === 'written'
          ? 'Written'
          : 'Oral';
        serverValue = 'y';
      }

      // 서버에 PDF 데이터 업데이트 API 호출
      await axios.post(`${API_URL}/api/update_complaint`, {
        field: serverField,
        value: serverValue
      });

      // 6개 답변 다 받은 후(마지막 질문인 경우) /api/generate_complaint_content 호출하여 내용 생성 및 data["Details"]에 저장
      if (
        currentQuestion === questions.length - 1 &&
        !pdfShown
      ) {
        // 6개 질문 key 목록
        const detailKeys = [
          "work_detail",
          "period",
          "location",
          "wage",
          "response",
          "extra_info",
        ];

        // detailKeys에 해당하는 답변만 필터링
        const detailData = detailKeys.reduce((acc, k) => {
          acc[k] = (k in data ? data[k] : "") || "";
          // 현재 마지막 답변도 포함
          if (k === key) acc[k] = userMessage;
          return acc;
        }, {});

        // 서버에 detailData 보내어 complaint content 생성 요청
        const contentResponse = await axios.post(`${API_URL}/api/generate_complaint_content`, detailData, {
          headers: {
            'Content-Type': 'application/json',
          }
        });

        // 서버가 생성한 내용 받아서 data["Details"]에 저장
        const content = contentResponse.data.content || '';
        setData(prevData => ({ ...prevData, Details: content }));

        // 서버에 Details 내용 업데이트 (PDF 반영)
        await axios.post(`${API_URL}/api/update_complaint`, {
          field: "Details",
          value: content,
        });

        // PDF URL 받아오기
        const pdfResponse = await axios.get(`${API_URL}/api/get_complaint_pdf_url`);
        setPdfUrl(pdfResponse.data.pdfUrl);

        // 메시지 및 PDF 버튼 표시
        setMessages(prev => [
          ...prev,
          { type: 'bot', text: '모든 질문이 완료되었습니다. 아래 버튼을 눌러 PDF를 확인하세요.' },
          { type: 'pdf' },
        ]);
        setPdfShown(true);
        setCurrentQuestion(prev => prev + 1);
        return;
      }

      // 다음 질문 출력
      const nextQuestionIndex = currentQuestion + 1;
      setCurrentQuestion(nextQuestionIndex);
      setMessages(prev => [
        ...prev,
        { type: 'bot', text: questions[nextQuestionIndex]?.question || '' },
      ]);
    } catch (error) {
      console.error('서버 통신 오류:', error);
      if (error.response) {
        console.error('응답 데이터:', error.response.data);
        console.error('응답 상태:', error.response.status);
        console.error('응답 헤더:', error.response.headers);
      } else if (error.request) {
        console.error('요청은 되었지만 응답이 없습니다:', error.request);
      } else {
        console.error('에러 메시지:', error.message);
      }

      setMessages(prev => [
        ...prev,
        { type: 'bot', text: '서버와 통신 중 오류가 발생했습니다.' },
      ]);
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView
        style={styles.container}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        <ScrollView
          contentContainerStyle={styles.chatContainer}
          ref={scrollViewRef}
          onContentSizeChange={() => scrollViewRef.current?.scrollToEnd({ animated: true })}
        >
          {messages.map((msg, index) => {
            if (msg.type === 'pdf') {
              return (
                <View key={index} style={[styles.messageBubble, styles.botBubble]}>
                  <TouchableOpacity style={styles.pdfButton} onPress={openPdfInSafari}>
                    <Text style={styles.pdfButtonText}>PDF 열기</Text>
                  </TouchableOpacity>
                </View>
              );
            } else {
              return (
                <View
                  key={index}
                  style={[
                    styles.messageBubble,
                    msg.type === 'bot' ? styles.botBubble : styles.userBubble,
                  ]}
                >
                  <Text style={styles.messageText}>{msg.text}</Text>
                </View>
              );
            }
          })}
        </ScrollView>

        <View style={styles.inputContainer}>
          <TextInput
            style={styles.input}
            placeholder="메시지를 입력하세요"
            value={input}
            onChangeText={setInput}
            onSubmitEditing={handleSubmit}
            returnKeyType="send"
          />
          <TouchableOpacity onPress={handleSubmit} disabled={!input.trim()}>
            <Ionicons name="send" size={28} color={input.trim() ? '#4fc3f7' : '#ccc'} />
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#fff',
  },
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  chatContainer: {
    padding: 16,
  },
  messageBubble: {
    padding: 12,
    borderRadius: 12,
    marginVertical: 6,
    maxWidth: '80%',
  },
  botBubble: {
    backgroundColor: '#c8e6c9',
    alignSelf: 'flex-start',
  },
  userBubble: {
    backgroundColor: '#e0f7fa',
    alignSelf: 'flex-end',
  },
  messageText: {
    fontSize: 16,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderTopWidth: 1,
    borderColor: '#ccc',
  },
  input: {
    flex: 1,
    height: 40,
    paddingHorizontal: 12,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#4fc3f7',
    marginRight: 8,
  },
  pdfButton: {
    backgroundColor: '#4fc3f7',
    paddingVertical: 10,
    paddingHorizontal: 18,
    borderRadius: 8,
  },
  pdfButtonText: {
    color: '#fff',
    fontSize: 16,
  },
});