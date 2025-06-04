import React, { useState, useEffect } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, ScrollView,
  StyleSheet, KeyboardAvoidingView, Platform, SafeAreaView,
  Alert, Pressable
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import axios from 'axios';
import { Audio } from "expo-av";
import * as FileSystem from "expo-file-system";

const SPEECH_KEY = "FoM5freZRdxxMOav8bKJO69UnFjgShnxOJWtMcI2E7yV5Y0kuMtOJQQJ99BEACYeBjFXJ3w3AAAEACOG2mxM";
const SPEECH_REGION = "eastus";

const TTS_VOICES = {
  "ko-KR": "ko-KR-SoonBokNeural",
  "en-US": "en-US-JennyNeural",
};

const ChatScreen = () => {
  const [messages, setMessages] = useState([
    {
      type: 'bot',
      text: '안녕하세요.\n7팀 챗봇이에요😊\n출입국/체류에 관해서 궁금한 점을 질문해주시면 안내해드릴게요!',
    },
  ]);
  const [input, setInput] = useState('');
  const [recording, setRecording] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState("ko-KR");

  const speakText = async (text) => {
    if (!text || isSpeaking) return;
    try {
      setIsSpeaking(true);
      const voice = TTS_VOICES[selectedLanguage] || TTS_VOICES["en-US"];
      const ssml = `
        <speak version='1.0' xml:lang='${selectedLanguage}'>
          <voice name='${voice}'>${text}</voice>
        </speak>`;

      const response = await fetch(
        `https://${SPEECH_REGION}.tts.speech.microsoft.com/cognitiveservices/v1`,
        {
          method: "POST",
          headers: {
            "Ocp-Apim-Subscription-Key": SPEECH_KEY,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "audio-16khz-32kbitrate-mono-mp3",
          },
          body: ssml,
        }
      );

      if (!response.ok) throw new Error(`TTS 오류: ${response.status}`);

      const blob = await response.blob();
      const path = `${FileSystem.cacheDirectory}speech-${Date.now()}.mp3`;

      const reader = new FileReader();
      reader.onload = async () => {
        const base64 = reader.result.split(',')[1];
        await FileSystem.writeAsStringAsync(path, base64, { encoding: FileSystem.EncodingType.Base64 });

        const { sound } = await Audio.Sound.createAsync({ uri: path });
        await sound.playAsync();
        sound.setOnPlaybackStatusUpdate(async (status) => {
          if (status.didJustFinish) {
            await sound.unloadAsync();
            await FileSystem.deleteAsync(path, { idempotent: true });
            setIsSpeaking(false);
          }
        });
      };
      reader.readAsDataURL(blob);
    } catch (error) {
      Alert.alert("TTS 실패", error.message);
      setIsSpeaking(false);
    }
  };

  const startRecording = async () => {
    try {
      const permission = await Audio.requestPermissionsAsync();
      if (permission.status !== 'granted') {
        Alert.alert('권한 필요', '마이크 권한을 허용해주세요.');
        return;
      }

      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      const { recording } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );

      setRecording(recording);
      setIsRecording(true);
    } catch (error) {
      Alert.alert('녹음 오류', error.message);
    }
  };

  const stopRecording = async () => {
    try {
      if (!recording) return;
      setIsRecording(false);
      await recording.stopAndUnloadAsync();
      const uri = recording.getURI();
      setRecording(null);
      if (uri) await sendToAzure(uri);
    } catch (error) {
      Alert.alert('녹음 중지 오류', error.message);
    }
  };

  const sendToAzure = async (uri) => {
    try {
      const response = await fetch(uri);
      const blob = await response.blob();

      const azureResponse = await fetch(
        `https://${SPEECH_REGION}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1?language=${selectedLanguage}`,
        {
          method: "POST",
          headers: {
            "Ocp-Apim-Subscription-Key": SPEECH_KEY,
            "Content-Type": "audio/wav",
          },
          body: blob,
        }
      );

      const result = await azureResponse.json();
      if (result.RecognitionStatus === "Success") {
        sendMessage(result.DisplayText);
      } else {
        Alert.alert("STT 실패", "음성을 인식하지 못했습니다.");
      }
    } catch (error) {
      Alert.alert("STT 오류", error.message);
    }
  };

  const sendMessage = async (text) => {
    const userMessage = { type: 'user', text };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');

    try {
      const response = await axios.post('http://192.168.45.205:5000/chat', {
        query: text,
      });

      const botText = response.data.response;
      const botMessage = { type: 'bot', text: botText };
      setMessages((prev) => [...prev, botMessage]);
      await speakText(botText);
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

  const categories = [
    '초청/사증', '출입국심사', '체류',
    '국적/귀화', '제도/절차', '증명발급',
    '출입국안내', '계절근로자', '기타',
  ];

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

          <View style={styles.buttonContainer}>
            {categories.map((cat, i) => (
              <TouchableOpacity
                key={i}
                style={styles.categoryButton}
                onPress={() => {
                  const question = `${cat} 관련 도움은 어디서 받을 수 있나요?`;
                  sendMessage(question);
                }}
              >
                <Text style={styles.categoryText}>{cat}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </ScrollView>

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
          <TouchableOpacity
            onPress={isRecording ? stopRecording : startRecording}
            style={{ marginLeft: 10 }}
          >
            <Ionicons name={isRecording ? "stop-circle" : "mic"} size={28} color={isRecording ? "red" : "#4fc3f7"} />
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
