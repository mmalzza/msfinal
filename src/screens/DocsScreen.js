import React from 'react';
import { View, Text, Button, StyleSheet } from 'react-native';

export default function DocsScreen({ navigation }) {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>문서 작성</Text>
      <View style={styles.buttonContainer}>
        <Button
          title="통합신청서 작성"
          onPress={() => navigation.navigate('PDFDocs')}
        />
      </View>
      <View style={styles.buttonContainer}>
        <Button
          title="진정서 작성"
          onPress={() => navigation.navigate('ComplaintDocs')}
        />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    paddingHorizontal: 20,
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 24,
    marginBottom: 40,
    textAlign: 'center',
  },
  buttonContainer: {
    marginVertical: 10,
  },
});
