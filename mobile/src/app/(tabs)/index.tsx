import { useEffect, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { router } from 'expo-router';
import { Button, ErrorText, Loading, Pill, Screen, Section, colors } from '../components/Ui';
import { getFallbackApiBase, knowledgeBaseApi } from '../lib/api';
import { getApiBase } from '../lib/storage';
import { KnowledgeBaseRecord } from '../lib/types';

function statusTone(status: KnowledgeBaseRecord['status']) {
  if (status === 'ready') return 'success';
  if (status === 'failed') return 'danger';
  if (status === 'indexing' || status === 'validating') return 'running';
  return 'warning';
}

export default function HomeScreen() {
  const [apiBase, setApiBase] = useState(getFallbackApiBase());
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBaseRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  async function refresh() {
    setLoading(true);
    setError('');
    try {
      const storedBase = await getApiBase(apiBase);
      setApiBase(storedBase);
      const items = await knowledgeBaseApi.list(storedBase);
      setKnowledgeBases(items);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to load knowledge bases');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { void refresh(); }, []);

  async function createDemo() {
    setLoading(true);
    setError('');
    try {
      await knowledgeBaseApi.demo(apiBase);
      await refresh();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to create demo');
      setLoading(false);
    }
  }

  return (
    <Screen
      title="Knowledge Base Studio"
      subtitle="Build, index, and query knowledge from your phone"
      actions={<Button variant="quiet" onPress={() => router.push('/settings')}>API</Button>}
    >
      <ScrollView showsVerticalScrollIndicator={false}>
        <Section eyebrow="Workspace" title="Knowledge bases" action={<Button variant="quiet" onPress={createDemo}>Demo</Button>}>
          {loading ? <Loading label="Loading knowledge bases" /> : null}
          {error ? <ErrorText>{error}</ErrorText> : null}
          {!loading && !error && !knowledgeBases.length ? (
            <View style={styles.empty}>
              <Text style={styles.emptyTitle}>No knowledge bases yet</Text>
              <Text style={styles.emptyText}>Create the demo workspace or open Builder to design a pipeline.</Text>
            </View>
          ) : null}
          {knowledgeBases.map((knowledgeBase) => (
            <Pressable
              key={knowledgeBase.id}
              onPress={() => router.push({ pathname: '/builder', params: { id: knowledgeBase.id } })}
              style={({ pressed }) => [styles.card, pressed && styles.pressed]}
            >
              <View style={styles.cardTop}>
                <View style={styles.cardTitleWrap}>
                  <Text numberOfLines={1} style={styles.cardTitle}>{knowledgeBase.name}</Text>
                  <Text numberOfLines={2} style={styles.cardDescription}>{knowledgeBase.description || 'No description'}</Text>
                </View>
                <Pill tone={statusTone(knowledgeBase.status)}>{knowledgeBase.status}</Pill>
              </View>
              <View style={styles.cardMeta}>
                <Text style={styles.cardMetaText}>{knowledgeBase.workflow?.nodes?.length || 0} nodes</Text>
                <Text style={styles.cardMetaText}>{knowledgeBase.chunks?.length || 0} chunks</Text>
                <Text style={styles.cardMetaText}>{knowledgeBase.metadata?.version || 'v1'}</Text>
              </View>
            </Pressable>
          ))}
        </Section>
        <Section eyebrow="Pipeline" title="From source to answer">
          <View style={styles.pipeline}>
            {['Source', 'Process', 'Metadata', 'Embed', 'Vector DB', 'RAG'].map((label, index) => (
              <View key={label} style={styles.pipelineItem}>
                <View style={[styles.pipelineDot, { backgroundColor: index < 2 ? colors.accent : index < 4 ? colors.blue : colors.violet }]} />
                <Text style={styles.pipelineLabel}>{label}</Text>
              </View>
            ))}
          </View>
          <Button variant="secondary" onPress={() => router.push('/builder')}>Open workflow builder</Button>
        </Section>
      </ScrollView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  card: { backgroundColor: colors.panelSoft, borderColor: colors.border, borderRadius: 12, borderWidth: 1, marginBottom: 10, padding: 13 },
  pressed: { opacity: 0.7 },
  cardTop: { alignItems: 'flex-start', flexDirection: 'row', gap: 10, justifyContent: 'space-between' },
  cardTitleWrap: { flex: 1, minWidth: 0 },
  cardTitle: { color: colors.text, fontSize: 15, fontWeight: '800' },
  cardDescription: { color: colors.muted, fontSize: 12, lineHeight: 17, marginTop: 4 },
  cardMeta: { flexDirection: 'row', flexWrap: 'wrap', gap: 12, marginTop: 12 },
  cardMetaText: { color: colors.muted, fontSize: 11 },
  empty: { alignItems: 'center', padding: 18 },
  emptyTitle: { color: colors.text, fontSize: 14, fontWeight: '750' },
  emptyText: { color: colors.muted, fontSize: 12, lineHeight: 17, marginTop: 5, textAlign: 'center' },
  pipeline: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginBottom: 14 },
  pipelineItem: { alignItems: 'center', backgroundColor: 'rgba(148,170,205,0.06)', borderColor: colors.border, borderRadius: 10, borderWidth: 1, flexDirection: 'row', gap: 6, paddingHorizontal: 9, paddingVertical: 7 },
  pipelineDot: { borderRadius: 5, height: 7, width: 7 },
  pipelineLabel: { color: colors.muted, fontSize: 10, fontWeight: '700' },
  border: 'rgba(148,170,205,0.18)',
});
