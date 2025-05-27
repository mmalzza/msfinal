import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function ChatScreen({ route }) {
  const { country, language } = route.params || {};

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Chat Screen</Text>
      <Text>Selected Country: {country}</Text>
      <Text>Selected Language: {language}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, justifyContent: 'center', alignItems: 'center' },
  title: { fontSize: 24, marginBottom: 20 },
});
