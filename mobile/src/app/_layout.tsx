import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';

export default function RootLayout() {
  return (
    <>
      <Stack
        screenOptions={{
          contentStyle: { backgroundColor: '#08111f' },
          headerStyle: { backgroundColor: '#08111f' },
          headerTintColor: '#edf4ff',
          headerTitleStyle: { fontWeight: '800' },
        }}
      />
      <StatusBar style="light" />
    </>
  );
}
