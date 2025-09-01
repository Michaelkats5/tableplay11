import React from 'react';
import { View, Text, SafeAreaView, StyleSheet } from 'react-native';
import { theme } from '@/lib/theme';

export default function Notifications() {
  return (
    <SafeAreaView style={styles.safe}>
      <View style={styles.container}>
        <Text style={styles.h1}>Notifications</Text>
        <Text style={{ color: theme.colors.subtext }}>You'll see queue buzz, offers, and allergen alerts here.</Text>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: theme.colors.bg },
  container: { padding: 16 },
  h1: { fontSize: 24, fontWeight: '800', marginBottom: 12, color: theme.colors.text }
});
