import { Tabs } from 'expo-router';
import { Text, View } from 'react-native';
import { colors } from '../components/Ui';

function TabIcon({ children, color }: { children: string; color: string }) {
  return (
    <View style={{ alignItems: 'center', justifyContent: 'center' }}>
      <Text style={{ color, fontSize: 15, fontWeight: '900' }}>{children}</Text>
    </View>
  );
}

export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: colors.accent,
        tabBarInactiveTintColor: colors.muted,
        tabBarStyle: { backgroundColor: '#0d1829', borderColor: 'rgba(148,170,205,0.16)', borderTopWidth: 1, minHeight: 64, paddingBottom: 8, paddingTop: 8 },
        tabBarItemStyle: { paddingBottom: 3 },
        tabBarLabelStyle: { fontSize: 10, fontWeight: '800' },
      }}
    >
      <Tabs.Screen
        name="index"
        options={{ title: 'Home', tabBarIcon: ({ color }) => <TabIcon color={color}>KB</TabIcon> }}
      />
      <Tabs.Screen
        name="builder"
        options={{ title: 'Builder', tabBarIcon: ({ color }) => <TabIcon color={color}>WF</TabIcon> }}
      />
      <Tabs.Screen
        name="search"
        options={{ title: 'RAG', tabBarIcon: ({ color }) => <TabIcon color={color}>AI</TabIcon> }}
      />
      <Tabs.Screen
        name="settings"
        options={{ title: 'Settings', tabBarIcon: ({ color }) => <TabIcon color={color}>IO</TabIcon> }}
      />
    </Tabs>
  );
}
