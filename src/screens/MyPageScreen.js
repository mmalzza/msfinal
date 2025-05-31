import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, SafeAreaView, TouchableOpacity } from 'react-native';
import { Card, Avatar } from 'react-native-paper';
import { Picker } from '@react-native-picker/picker';
import * as Progress from 'react-native-progress';
import moment from 'moment';

const MyPageScreen = () => {
  const [userInfo, setUserInfo] = useState(null);
  const [language, setLanguage] = useState('kr');
  const [daysLeft, setDaysLeft] = useState(0);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    fetch('http://192.168.45.205:5000/userinfo')
      .then(response => response.json())
      .then(data => {
        setUserInfo({
          ...data,
          birth: '1995-03-12',
          gender: '여성',
          registrationNo: '950312',
          passportIssue: '2020-03-01',
          passportExpiry: '2030-03-01',
          phone: '02-1234-5678',
          mobile: '010-1234-5678',
          localAddress: '서울특별시 구로구 가마산로 123',
          homeAddress: '하노이시 호안끼엠구 456',
          extensionStart: '2025-06-01',
          extensionEnd: '2025-06-30',
        });
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
        <Text style={{ textAlign: 'center', marginTop: 50 }}>로딩 중...</Text>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.header}>마이페이지</Text>

        {/* 기본 정보 카드 */}
        <Card style={styles.card}>
          <Card.Title
            title={userInfo.name}
            subtitle={userInfo.nationality}
            left={(props) => <Avatar.Text {...props} label={userInfo.name[0]} />}
          />
          <Card.Content>
            <Text style={styles.sectionTitle}>기본 정보</Text>
            {renderInfoRow('생년월일', userInfo.birth)}
            {renderInfoRow('성별', userInfo.gender)}
            {renderInfoRow('외국인등록번호', userInfo.registrationNo)}
            {renderInfoRow('여권번호', userInfo.passport)}
            {renderInfoRow('여권 발급일자', userInfo.passportIssue)}
            {renderInfoRow('여권 유효기간', userInfo.passportExpiry)}
            {renderInfoRow('전화번호', userInfo.phone)}
            {renderInfoRow('휴대전화', userInfo.mobile)}
            {renderInfoRow('대한민국 내 주소', userInfo.localAddress)}
            {renderInfoRow('본국 주소', userInfo.homeAddress)}

            <TouchableOpacity
              style={styles.editButton}
              onPress={() => alert('기본 정보 수정 화면으로 이동합니다.')}
            >
              <Text style={styles.editButtonText}>기본 정보 수정하기</Text>
            </TouchableOpacity>
          </Card.Content>
        </Card>

        {/* 비자 정보 카드 */}
        <Card style={styles.card}>
          <Card.Content>
            <Text style={styles.sectionTitle}>비자 정보</Text>
            {renderInfoRow('비자 종류', userInfo.visaType)}
            {renderInfoRow('입국일', userInfo.entryDate)}
            {renderInfoRow('비자 만료일', userInfo.visaExpiry)}
            {renderInfoRow(`체류 진행률`, `${progress.toFixed(1)}%`)}
            <Progress.Bar
              progress={progress / 100}
              width={null}
              color="#4fc3f7"
              borderRadius={10}
              height={12}
              style={{ marginTop: 4, marginBottom: 12 }}
            />
            {renderInfoRow('비자 만료까지 남은 날짜', `D-${daysLeft}`)}
            {renderInfoRow('연장 신청 시작일', userInfo.extensionStart)}
            {renderInfoRow('연장 신청 마감일', userInfo.extensionEnd)}

            <TouchableOpacity
              style={styles.editButton}
              onPress={() => alert('비자 정보 수정 화면으로 이동합니다.')}
            >
              <Text style={styles.editButtonText}>비자 정보 수정하기</Text>
            </TouchableOpacity>
          </Card.Content>
        </Card>

        {/* 언어 선택 */}
        <View style={styles.section}>
          <Text style={styles.label}>언어 선택</Text>
          <View style={styles.pickerContainer}>
            <Picker
              selectedValue={language}
              onValueChange={(value) => setLanguage(value)}
              style={styles.picker}
              mode="dropdown"
            >
              <Picker.Item label="한국어" value="kr" />
              <Picker.Item label="English" value="en" />
              <Picker.Item label="Tiếng Việt" value="vi" />
              <Picker.Item label="বাংলা" value="bn" />
              <Picker.Item label="Tagalog" value="tl" />
            </Picker>

            <TouchableOpacity
              style={styles.applyButton}
              onPress={() => {
                console.log('언어 적용:', language);
                alert('언어가 적용되었습니다!');
              }}
            >
              <Text style={styles.applyButtonText}>적용하기</Text>
            </TouchableOpacity>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const renderInfoRow = (label, value) => (
  <View style={styles.infoRow}>
    <Text style={styles.infoLabel}>{label}</Text>
    <Text style={styles.infoValue}>{value}</Text>
  </View>
);

export default MyPageScreen;

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
  },
  container: {
    padding: 16,
    paddingBottom: 40,
  },
  header: {
    fontSize: 22,
    fontWeight: 'bold',
    marginBottom: 16,
    textAlign: 'center'
  },
  card: {
    backgroundColor: '#ffffff',
    borderRadius: 16,
    paddingVertical: 10,
    paddingHorizontal: 12,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 6,
    shadowOffset: { width: 0, height: 2 },
    elevation: 2,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 6,
  },
  infoLabel: {
    fontWeight: '600',
    color: '#333',
  },
  infoValue: {
    color: '#555',
    maxWidth: '60%',
    textAlign: 'right',
  },
  section: {
    marginVertical: 16,
  },
  label: {
    fontWeight: '600',
    marginBottom: 6,
  },
  pickerContainer: {
    borderRadius: 12,
    overflow: 'hidden',
  },
  picker: {
    height: 180,
  },
  applyButton: {
  backgroundColor: '#ffffff',
  paddingVertical: 10,
  paddingHorizontal: 20,
  borderRadius: 8,
  marginTop: 20,
  alignItems: 'center',
  },
  applyButtonText: {
    color: 'black',
    fontSize: 16,
    fontWeight: '600',
  },
  editButton: {
  marginTop: 16,
  paddingVertical: 10,
  paddingHorizontal: 20,
  borderRadius: 8,
  alignSelf: 'flex-end',
  },
  editButtonText: {
    color: 'black',
    fontSize: 14,
    fontWeight: '600',
  },
});
