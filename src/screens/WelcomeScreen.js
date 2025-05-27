import React, { useState } from 'react';
import { View, Text, Button, StyleSheet } from 'react-native';
import { Picker } from '@react-native-picker/picker';

export default function WelcomeScreen({ navigation }) {
  const [country, setCountry] = useState('Vietnam');
  const [language, setLanguage] = useState('Vietnamese');

  const handleContinue = () => {
    navigation.navigate('Chat', { country, language });
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Welcome to Korea!</Text>

      <Text>국가를 선택해주세요:</Text>
      <Picker selectedValue={country} onValueChange={(itemValue) => setCountry(itemValue)}>
        <Picker.Item label="Vietnam" value="Vietnam" />
        <Picker.Item label="Nepal" value="Nepal" />
        <Picker.Item label="Philippines" value="Philippines" />
        <Picker.Item label="Thailand" value="Thailand" />
      </Picker>

      <Text>언어를 선택해주세요:</Text>
      <Picker selectedValue={language} onValueChange={(itemValue) => setLanguage(itemValue)}>
        <Picker.Item label="Vietnamese" value="Vietnamese" />
        <Picker.Item label="Nepali" value="Nepali" />
        <Picker.Item label="Tagalog" value="Tagalog" />
        <Picker.Item label="Thai" value="Thai" />
      </Picker>

      <Button title="계속하기" onPress={handleContinue} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, justifyContent: 'center' },
  title: { fontSize: 24, marginBottom: 20, textAlign: 'center' },
});
