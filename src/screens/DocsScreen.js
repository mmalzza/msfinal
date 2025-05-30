import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const DocsScreen = () => {
  return (
    <View style={styles.container}>
      <Text style={styles.text}>문서 작성</Text>
    </View>
  );
};

export default DocsScreen;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  text: {
    fontSize: 18,
  },
});