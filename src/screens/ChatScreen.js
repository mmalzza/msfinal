import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, ScrollView, StyleSheet, KeyboardAvoidingView, Platform, SafeAreaView,} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import axios from 'axios';

const ChatScreen = () => {
  const [messages, setMessages] = useState([
    {
      type: 'bot',
      text: '안녕하세요.\n7팀 챗봇이에요😊\n출입국/체류에 관해서 궁금한 점을 질문해주시면 안내해드릴게요!',
    },
  ]);
  const [input, setInput] = useState('');

  const categories = [
    '초청/사증', '출입국심사', '체류',
    '국적/귀화', '제도/절차', '증명발급',
    '출입국안내', '계절근로자', '기타',
  ];

  const sendMessage = async (text) => {
    const userMessage = { type: 'user', text };
    setMessages([...messages, userMessage]);

    setInput('');

    try {
      const response = await axios.post('http://192.168.45.205:5000/chat', {
        message: text,
      });

      const botResponse = {
        type: 'bot',
        text: response.data.reply,
      };
      setMessages((prev) => [...prev, botResponse]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          type: 'bot',
          text: '죄송합니다. 현재 서버와 연결할 수 없습니다.',
        },
      ]);
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView
        style={styles.container}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        <ScrollView contentContainerStyle={styles.chatContainer}>
          {messages.map((msg, index) => (
            <View
              key={index}
              style={[
                styles.messageBubble,
                msg.type === 'bot' ? styles.botBubble : styles.userBubble,
              ]}
            >
              <Text style={styles.messageText}>{msg.text}</Text>
            </View>
          ))}

          {/* 카테고리 버튼 */}
          <View style={styles.buttonContainer}>
            {categories.map((cat, i) => (
              <TouchableOpacity
                key={i}
                style={styles.categoryButton}
                onPress={() => sendMessage(cat)}
              >
                <Text style={styles.categoryText}>{cat}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </ScrollView>

        {/* 입력창 + 전송 */}
        <View style={styles.inputContainer}>
          <TextInput
            style={styles.input}
            placeholder="메시지를 입력하세요"
            value={input}
            onChangeText={setInput}
          />
          <TouchableOpacity onPress={() => sendMessage(input)}>
            <Ionicons name="send" size={24} color="#4fc3f7" />
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

export default ChatScreen;

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
  buttonContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 10,
    justifyContent: 'flex-start',
  },
  categoryButton: {
    paddingVertical: 8,
    paddingHorizontal: 14,
    backgroundColor: '#f1f8e9',
    borderRadius: 8,
    margin: 4,
    borderWidth: 1,
    borderColor: '#a5d6a7',
  },
  categoryText: {
    fontSize: 14,
    color: '#333',
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
});

