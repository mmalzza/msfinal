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
    { field: "FOREIGN  RESIDENT  REGISTRATION", text: "외국인 등록에 해당하십니까? (y/n)" },
    { field: "REISSUANCE OF REGISTRATION CARD", text: "등록증 재발급에 해당하십니까? (y/n)" },
    { field: "EXTENSION  OF  SOJOURN  PERIOD", text: "체류기간 연장허가에 해당하십니까? (y/n)" },
    { field: "CHANGE  OF  STATUS  OF  SOJOURN", text: "체류자격 변경하기에 해당하십니까? (y/n)" },
    { field: "Status to apply for1", text: "희망자격은 무엇입니까?", condition: (data) => data["CHANGE  OF  STATUS  OF  SOJOURN"] === 'y' },
    { field: "GRANTING  STATUS  OF  SOJOURN", text: "체류자격 부여에 해당하십니까? (y/n)" },
    { field: "Status to apply for2", text: "희망자격은 무엇입니까?", condition: (data) => data["GRANTING  STATUS  OF  SOJOURN"] === 'y' },
    { field: "ENGAGE IN ACTIVITIES NOT COVERED BY THE STATUS OF SOJOURN", text: "체류자격 외 활동허가에 해당하십니까? (y/n)" },
    { field: "Status to apply for3", text: "희망자격은 무엇입니까?", condition: (data) => data["ENGAGE IN ACTIVITIES NOT COVERED BY THE STATUS OF SOJOURN"] === 'y' },
    { field: "CHANGE  OR  ADDITION  OF  WORKPLACE", text: "근무처 변경ㆍ추가허가 / 신고에 해당하십니까? (y/n)" },
    { field: "REENTRY  PERMIT  (SINGLE,  MULTIPLE)", text: "재입국허가 (단수, 복수) 에 해당하십니까? (y/n)" },
    { field: "ALTERATION  OF  RESIDENCE", text: "체류지 변경신고에 해당하십니까? (y/n)" },
    { field: "CHANGE OF INFORMATION ON REGISTRATION", text: "등록사항 변경신고에 해당하십니까? (y/n)" },
    { field: "Surname", text: "성을 입력하세요" },
    { field: "Givenname", text: "이름을 입력하세요" },
    { field: "Year", text: "생년을 입력하세요" },
    { field: "month", text: "생월을 입력하세요" },
    { field: "day", text: "생일을 입력하세요" },
    { field: "boy", text: "남자입니까 여자입니까?(남자1, 여자2)" },
    { field: "nationality", text: "국가을 입력하세요" },
    { field: "passport_no", text: "여권 번호을 입력하세요" },
    { field: "Passport Issue Date", text: "여권 발급일자를 입력하세요" },
    { field: "Passport Expiry Date", text: "여권 유효기간을 입력하세요" },
    { field: "Address In Korea", text: "대한민국 내 주소를 입력하세요" },
    { field: "Telephone No", text: "전화번호를 입력하세요" },
    { field: "Cell phone No", text: "휴대전화를 입력하세요" },
    { field: "Address  In  Home  Country", text: "본국주소를 입력하세요" },
    { field: "Phone No1", text: "본국 전화번호를 입력하세요" },
    { field: "Non-school", text: "재학여부를 선택하세요(미취학(1),초등학생(2),중학생(3),고등학생(4))" },
    { field: "Name of School", text: "학교이름을 입력하세요", condition: (data) => data["Non-school"] !== '1' },
    { field: "Phone No2", text: "학교전화번호를 입력하세요", condition: (data) => data["Non-school"] !== '1' },
    { field: "Accredited school by Education Office", text: "학교 종류를 입력하세요((1)교육청 인가 학교(2)교육청 비인가/대안학교)", condition: (data) => data["Non-school"] !== '1' },
    { field: "Current Workplace", text: "현 근무처를 입력하세요" },
    { field: "Business Registration No1", text: "현 근무처 사업자등록번호를 입력하세요" },
    { field: "Phone No3", text: "현 근무처 전화번호를 입력하세요" },
    { field: "New Workplace", text: "새로운 예정 근무처를 입력하세요" },
    { field: "Business Registration No2", text: "새로운 예정 근무처의 사업자등록번호를 입력하세요" },
    { field: "Phone No4", text: "새로운 예정 근무처의 전화번호를 입력하세요" },
    { field: "Annual Income Amount", text: "연 소득금액을 입력하세요(만원)" },
    { field: "Occupation", text: "직업을 입력하세요" },
    { field: "Intended Period Of Reentry", text: "재입국 신청 기간을 입력하세요" },
    { field: "E-Mail", text: "전자우편을 입력하세요" },
    { field: "Refund Bank Account No. only for Foreign Resident Registration", text: "반환용 계좌번호(외국인등록 및 외국인등록증 재발급 신청 시에만 기재)을 입력하세요" },
    { field: "Date of application", text: "신청일을 입력하세요" }
  ];

  useEffect(() => {
    // 첫 렌더 시 첫 질문 보여주기
    if (isFirstRender.current) {
      isFirstRender.current = false;
      setMessages([{ type: 'bot', text: questions[0].text }]);
      return;
    }

    //if (currentQuestion >= questions.length) return;
    if (pdfShown || currentQuestion >= questions.length) return;

    const currentQ = questions[currentQuestion];

    // 미취학(1) 선택 시 학교 관련 질문 건너뛰기
    if (
      data['Non-school'] === '1' &&
      ['Name of School', 'Phone No2', 'Accredited school by Education Office'].includes(currentQ.field)
    ) {
      const currentWorkplaceIndex = questions.findIndex(q => q.field === 'Current Workplace');
      setCurrentQuestion(currentWorkplaceIndex);
      return;
    }

    // 조건부 질문 처리
    if (!currentQ.condition || currentQ.condition(data)) {
      const lastMessage = messages[messages.length - 1];
      if (!lastMessage || lastMessage.text !== currentQ.text) {
        setMessages(prev => [...prev, { type: 'bot', text: currentQ.text }]);
      }
    } else {
      setCurrentQuestion(prev => prev + 1);
    }
  }, [currentQuestion, data]);

  const handleSubmit = async () => {
    if (!input.trim()) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { type: 'user', text: userMessage }]);

    try {
      if (currentQuestion >= questions.length) return;

      const field = questions[currentQuestion].field;
      let value = userMessage;

      if (field === 'boy') {
        if (userMessage === '1') {
          await axios.post(`${API_URL}/api/update_foreigner`, { field: 'boy', value: 'y' });
          await axios.post(`${API_URL}/api/update_foreigner`, { field: 'girl', value: 'n' });
          setData(prev => ({ ...prev, boy: 'y', girl: 'n' }));
        } else if (userMessage === '2') {
          await axios.post(`${API_URL}/api/update_foreigner`, { field: 'boy', value: 'n' });
          await axios.post(`${API_URL}/api/update_foreigner`, { field: 'girl', value: 'y' });
          setData(prev => ({ ...prev, boy: 'n', girl: 'y' }));
        } else {
          setMessages(prev => [...prev, { type: 'bot', text: '1(남자) 또는 2(여자)를 입력해주세요.' }]);
          return;
        }
      } else {
        await axios.post(`${API_URL}/api/update_foreigner`, { field, value: userMessage });
        setData(prev => ({ ...prev, [field]: userMessage }));
      }

      // 마지막 질문 다음엔 PDF URL 받아오기
      if (currentQuestion === questions.length - 1 && !pdfShown) {
        const response = await axios.get(`${API_URL}/api/get_foreigner_pdf_url`);
        setPdfUrl(response.data.pdfUrl);
        setMessages(prev => [
          ...prev,
          { type: 'bot', text: '모든 질문이 완료되었습니다. 아래 버튼을 눌러 PDF를 확인하세요.' },
          { type: 'pdf' }
        ]);
        setPdfShown(true);
        return;
      }

      setCurrentQuestion(prev => prev + 1);

    } catch (error) {
      if (axios.isAxiosError(error)) {
        console.error('Axios error message:', error.message);

        if (error.response) {
          console.error('Response status:', error.response.status);
          console.error('Response data:', error.response.data);
        } else if (error.request) {
          console.error('No response received, request details:', error.request);
        } else {
          console.error('Error setting up request:', error.message);
        }
      } else {
        console.error('Unexpected error:', error);
      }

      setMessages(prev => [...prev, { type: 'bot', text: '서버와 통신 중 오류가 발생했습니다.' }]);
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
          />
          <TouchableOpacity onPress={handleSubmit}>
            <Ionicons name="send" size={24} color="#4fc3f7" />
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

export const styles = StyleSheet.create({
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