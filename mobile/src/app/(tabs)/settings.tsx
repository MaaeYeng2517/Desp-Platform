import { useEffect, useState } from 'react';
import { ScrollView, StyleSheet, Text, View } from 'react-native';
import { Button, ErrorText, Input, Pill, Section, Screen, colors } from '../../components/Ui';
import { getFallbackApiBase, knowledgeBaseApi, normalizeApiBase } from '../../lib/api';
import { getApiBase, setApiBase } from '../../lib/storage';

export default function SettingsScreen() {
  const [apiBase, setApiBaseValue] = useState(getFallbackApiBase());
  const [savedApiBase, setSavedApiBase] = useState('');
  const [connected, setConnected] = useState<null | boolean>(null);
  const [message, setMessage] = useState('');

  async function load() {
    const stored = await getApiBase(getFallbackApiBase());
    setApiBaseValue(stored);
    setSavedApiBase(stored);
  }

  useEffect(() => { void load(); }, []);

  async function save() {
    const normalized = normalizeApiBase(apiBase);
    if (!normalized) {
      setMessage('API base URL is required');
      return;
    }
    await setApiBase(normalized);
    setSavedApiBase(normalized);
    setMessage('API base saved');
  }

  async function testConnection() {
    setMessage('');
    setConnected(null);
    try {
      await knowledgeBaseApi.catalog(normalizeApiBase(apiBase));
      setConnected(true);
      setMessage('API is reachable');
    } catch (caught) {
      setConnected(false);
      setMessage(caught instanceof Error ? caught.message : 'API is not reachable');
    }
  }

  return (
    <Screen title="Settings" subtitle="Connect the mobile app to your Knowledge Base API">
      <ScrollView showsVerticalScrollIndicator={false}>
        <Section eyebrow="Connection" title="API endpoint">
          <View style={styles.field}>
            <Text style={styles.label}>Base URL</Text>
            <Input
              autoCapitalize="none"
              keyboardType="url"
              value={apiBase}
              onChangeText={(value) => setApiBaseValue(value)}
              placeholder="http://localhost:3000/api/knowledge-base"
            />
          </View>
          <View style={styles.actionRow}>
            <Button variant="secondary" onPress={testConnection}>Test</Button>
            <Button onPress={save}>Save</Button>
          </View>
          {message ? <Text style={[styles.message, connected === false && styles.errorMessage]}>{message}</Text> : null}
          {connected === true ? <Pill tone="success">Connected</Pill> : null}
          {connected === false ? <Pill tone="danger">Disconnected</Pill> : null}
        </Section>
        <Section eyebrow="Current workspace" title="Saved configuration">
          <View style={styles.settingRow}>
            <Text style={styles.settingLabel}>Active endpoint</Text>
            <Text numberOfLines={1} style={styles.settingValue}>{savedApiBase}</Text>
          </View>
          <View style={styles.settingRow}>
            <Text style={styles.settingLabel}>Mobile mode</Text>
            <Pill tone="running">Expo Go ready</Pill>
          </View>
          <Text style={styles.help}>Use http://localhost:3000 for iOS simulator or your LAN address for a physical device. The Web App and API use the same backend.</Text>
        </Section>
      </ScrollView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  field: { marginBottom: 12 },
  label: { color: '#8fa3bf', fontSize: 11, fontWeight: '700', marginBottom: 6 },
  actionRow: { flexDirection: 'row', gap: 8 },
  message: { color: '#8fa3bf', fontSize: 12, lineHeight: 17, marginTop: 10 },
  errorMessage: { color: '#fb7185' },
  settingRow: { alignItems: 'center', borderBottomColor: 'rgba(148,170,205,0.12)', borderBottomWidth: 1, flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 11 },
  settingLabel: { color: '#8fa3bf', fontSize: 12, fontWeight: '700' },
  settingValue: { color: '#edf4ff', flex: 1, fontSize: 12, marginLeft: 12, textAlign: 'right' },
  help: { color: '#8fa3bf', fontSize: 12, lineHeight: 18, marginTop: 14 },
});
