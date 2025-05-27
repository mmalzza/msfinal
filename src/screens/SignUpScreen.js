import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  Image,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';

const SignUpScreen = ({ navigation }) => {
  const [id, setId] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [name, setName] = useState('');
  const [birthdate, setBirthdate] = useState('');
  const [passportImage, setPassportImage] = useState(null);

  const handleSignUp = () => {
    if (!id || !password || !confirmPassword || !name || !birthdate) {
      Alert.alert('입력 오류', '모든 항목을 입력해주세요.');
      return;
    }

    if (password !== confirmPassword) {
      Alert.alert('비밀번호 오류', '비밀번호가 일치하지 않습니다.');
      return;
    }

    // 회원가입 성공 처리
    Alert.alert('회원가입 완료', `${name}님 환영합니다!`);
    navigation.navigate('Start');
  };

  const pickImage = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [3, 4],
      quality: 1,
    });

    if (!result.canceled) {
      setPassportImage(result.assets[0].uri);
    }
  };

  const takePhoto = async () => {
    const permission = await ImagePicker.requestCameraPermissionsAsync();
    if (permission.status !== 'granted') {
      Alert.alert('카메라 권한 필요', '카메라 권한이 필요합니다.');
      return;
    }

    const result = await ImagePicker.launchCameraAsync({
      allowsEditing: true,
      aspect: [3, 4],
      quality: 1,
    });

    if (!result.canceled) {
      setPassportImage(result.assets[0].uri);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>회원가입</Text>

      <TextInput placeholder="아이디" value={id} onChangeText={setId} style={styles.input} />
      <TextInput
        placeholder="비밀번호"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
        style={styles.input}
      />
      <TextInput
        placeholder="비밀번호 확인"
        value={confirmPassword}
        onChangeText={setConfirmPassword}
        secureTextEntry
        style={styles.input}
      />
      <TextInput placeholder="이름" value={name} onChangeText={setName} style={styles.input} />
      <TextInput
        placeholder="생년월일 (YYYY-MM-DD)"
        value={birthdate}
        onChangeText={setBirthdate}
        style={styles.input}
      />

      <View style={styles.imageButtons}>
        <TouchableOpacity style={styles.subButton} onPress={pickImage}>
          <Text style={styles.subButtonText}>여권 업로드</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.subButton} onPress={takePhoto}>
          <Text style={styles.subButtonText}>사진 촬영</Text>
        </TouchableOpacity>
      </View>

      {passportImage && (
        <Image source={{ uri: passportImage }} style={styles.previewImage} />
      )}

      <TouchableOpacity style={styles.button} onPress={handleSignUp}>
        <Text style={styles.buttonText}>회원가입</Text>
      </TouchableOpacity>
    </View>
  );
};

export default SignUpScreen;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F7FAFC',
    justifyContent: 'center',
    paddingHorizontal: 30,
  },
  title: {
    fontSize: 26,
    fontWeight: 'bold',
    marginBottom: 30,
    textAlign: 'center',
    color: '#333',
  },
  input: {
    borderWidth: 1,
    borderColor: '#CBD5E0',
    backgroundColor: '#fff',
    borderRadius: 10,
    paddingHorizontal: 15,
    paddingVertical: 12,
    fontSize: 16,
    marginBottom: 15,
  },
  button: {
    backgroundColor: '#2B6CB0',
    borderRadius: 10,
    paddingVertical: 15,
    marginTop: 20,
    alignItems: 'center',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
  },
  subButton: {
    backgroundColor: '#E2E8F0',
    padding: 10,
    borderRadius: 10,
    marginHorizontal: 5,
  },
  subButtonText: {
    fontSize: 14,
    color: '#2D3748',
  },
  imageButtons: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: 10,
  },
  previewImage: {
    width: '100%',
    height: 180,
    marginTop: 15,
    borderRadius: 10,
  },
});
