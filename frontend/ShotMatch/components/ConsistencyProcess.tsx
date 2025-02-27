import React from 'react';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';

const ConsistencyProcess: React.FC = () => {
  return (
    <View style={styles.container}>
      <ActivityIndicator size="large" color="#007AFF" />
      <Text style={styles.title}>Processing Videos</Text>
      <Text style={styles.subtitle}>
        Please wait while we process your consistency videos...
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    marginVertical: 10,
  },
  subtitle: {
    fontSize: 16,
    textAlign: 'center',
  },
});

export default ConsistencyProcess;