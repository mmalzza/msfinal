import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, SafeAreaView, Dimensions, Alert } from 'react-native';
import { Avatar, Card, Button } from 'react-native-paper';
import { Picker } from '@react-native-picker/picker';
import * as Progress from 'react-native-progress';
import moment from 'moment';

const screenHeight = Dimensions.get('window').height;

const MyPageScreen = () => {
  const [userInfo, setUserInfo] = useState(null);
  const [language, setLanguage] = useState('kr');
  const [daysLeft, setDaysLeft] = useState(0);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    fetch('http://192.168.45.205:5000/userinfo')
      .then(response => response.json())
      .then(data => {
        setUserInfo(data);
      })
      .catch(error => {
        Alert.alert('오류', '유저 정보를 불러오는데 실패했습니다.');
        console.error(error);
      });
  }, []);

  useEffect(() => {
    if (!userInfo) return;

    const today = moment();
    const expiry = moment(userInfo.visaExpiry);
    const total = expiry.diff(moment(userInfo.entryDate), 'days');
    const left = expiry.diff(today, 'days');
    const done = ((total - left) / total) * 100;
    setDaysLeft(left);
    setProgress(done);
  }, [userInfo]);

  if (!userInfo) {
    return (
      <SafeAreaView style={styles.safeArea}>
        <Text style={{textAlign: 'center', marginTop: 50}}>로딩중...</Text>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.header}>마이페이지</Text>

        <Card style={styles.card}>
          <Card.Title
            title={userInfo.name}
            subtitle={`${userInfo.nationality} • ${userInfo.visaType}`}
            left={(props) => <Avatar.Text {...props} label={userInfo.name[0]} />}
          />
          <Card.Content>
            <Text>여권번호: {userInfo.passport}</Text>
            <Text>입국일: {userInfo.entryDate}</Text>
            <Text>비자 만료일: {userInfo.visaExpiry}</Text>
          </Card.Content>
        </Card>

        <View style={styles.section}>
          <Text style={styles.text}>비자 만료까지 D-{daysLeft}</Text>
          <Progress.Bar
            progress={progress / 100}
            width={null}
            color={daysLeft <= 30 ? '#f44336' : daysLeft <= 60 ? '#ff9800' : '#4caf50'}
            borderRadius={10}
            height={16}
          />
          {daysLeft <= 60 && (
            <Text style={styles.warning}>비자 연장 신청 시기가 다가오고 있습니다!</Text>
          )}
        </View>

        <View style={styles.section}>
          <Text style={styles.label}>언어 선택</Text>
          <Picker
            selectedValue={language}
            onValueChange={(value) => setLanguage(value)}
            style={styles.picker}
          >
            <Picker.Item label="한국어" value="kr" />
            <Picker.Item label="English" value="en" />
            <Picker.Item label="Tiếng Việt" value="vi" />
            <Picker.Item label="বাংলা" value="bn" />
            <Picker.Item label="Tagalog" value="tl" />
          </Picker>
        </View>

        <Button mode="contained" style={styles.button}>
          문서 작성하러 가기
        </Button>
      </ScrollView>
    </SafeAreaView>
  );
};

export default MyPageScreen;

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#fff',
  },
  container: {
    padding: 16,
    minHeight: screenHeight,
    backgroundColor: '#fff',
  },
  header: {
    fontSize: 22,
    fontWeight: 'bold',
    marginBottom: 12,
    textAlign: 'center',
  },
  card: {
    marginBottom: 16,
    minHeight: screenHeight * 0.3,
    justifyContent: 'center',
    paddingVertical: 16,
  },
  section: {
    marginVertical: 12,
  },
  text: {
    marginBottom: 6,
    fontWeight: 'bold',
  },
  warning: {
    color: '#f44336',
    marginTop: 6,
    fontWeight: 'bold',
  },
  label: {
    marginBottom: 6,
    fontWeight: '600',
  },
  picker: {
    backgroundColor: '#f1f1f1',
  },
  button: {
    marginTop: 20,
  },
});
