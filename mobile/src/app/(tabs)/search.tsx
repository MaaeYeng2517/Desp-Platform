import { useEffect, useState } from 'react';
import { ScrollView, StyleSheet, Text, View } from 'react-native';
import { Button, ErrorText, Input, Loading, Pill, Section, Screen, colors } from '../components/Ui';
import { knowledgeBaseApi } from '../lib/api';
import { defaultDocuments } from '../lib/constants';
import { getApiBase } from '../lib/storage';
import { KnowledgeBaseRecord, RetrieveResponse, SearchResponse, StatusResponse } from '../lib/types';

function parseDocuments(value: string) {
  const documents = JSON.parse(value || '[]');
  if (!Array.isArray(documents) || documents.some((document) => !document?.content)) {
    throw new Error('Documents must be an array with non-empty content');
  }
  return documents;
}

export default function SearchScreen() {
  const [apiBase, setApiBase] = useState('');
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBaseRecord[]>([]);
  const [selectedId, setSelectedId] = useState('');
  const [documents, setDocuments] = useState(defaultDocuments);
  const [query, setQuery] = useState('How do I reset my password?');
  const [rag, setRag] = useState(true);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState('');
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [response, setResponse] = useState<SearchResponse | RetrieveResponse | null>(null);

  async function load() {
    setLoading(true);
    setError('');
    try {
      const base = await getApiBase('http://localhost:3000/api/knowledge-base');
      setApiBase(base);
      const items = await knowledgeBaseApi.list(base);
      setKnowledgeBases(items);
      const selected = items[0];
      if (selected) {
        setSelectedId(selected.id);
        const currentStatus = await knowledgeBaseApi.status(base, selected.id).catch(() => null);
        setStatus(currentStatus);
      }
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to load knowledge bases');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { void load(); }, []);

  async function refreshStatus() {
    if (!selectedId) return;
    const current = await knowledgeBaseApi.status(apiBase, selectedId);
    setStatus(current);
  }

  async function runPipeline() {
    if (!selectedId) return;
    setRunning(true);
    setError('');
    try {
      const result = await knowledgeBaseApi.run(apiBase, selectedId, parseDocuments(documents));
      setStatus({
        id: result.id,
        name: result.id,
        status: result.status,
        workflow: { nodes: 0, edges: 0 },
        index: { documents: result.documentCount, chunks: result.chunkCount, embeddingDimension: result.embeddingDimension },
        validation: result.validation,
        updatedAt: result.updatedAt,
      });
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to run indexing');
    } finally {
      setRunning(false);
    }
  }

  async function search() {
    if (!selectedId || !query.trim()) return;
    setRunning(true);
    setError('');
    try {
      const result = rag
        ? await knowledgeBaseApi.retrieve(apiBase, selectedId, query.trim(), 4)
        : await knowledgeBaseApi.search(apiBase, selectedId, query.trim(), 4);
      setResponse(result);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to search knowledge base');
    } finally {
      setRunning(false);
    }
  }

  const selected = knowledgeBases.find((item) => item.id === selectedId);

  return (
    <Screen title="Index & RAG" subtitle="Chunk, embed, search, and retrieve answers">
      <ScrollView showsVerticalScrollIndicator={false}>
        {loading ? <Loading label="Loading workspace" /> : null}
        {error ? <ErrorText>{error}</ErrorText> : null}
        <Section eyebrow="Target" title="Knowledge base">
          <View style={styles.selectRow}>
            {knowledgeBases.map((item) => (
              <Button
                key={item.id}
                variant={item.id === selectedId ? 'primary' : 'quiet'}
                onPress={() => { setSelectedId(item.id); void refreshStatus(); }}
              >
                {item.name.length > 18 ? `${item.name.slice(0, 17)}...` : item.name}
              </Button>
            ))}
          </View>
          {status ? (
            <View style={styles.statusGrid}>
              <View style={styles.statusCard}><Text style={styles.statusLabel}>Status</Text><Pill tone={status.status === 'ready' ? 'success' : status.status === 'failed' ? 'danger' : 'running'}>{status.status}</Pill></View>
              <View style={styles.statusCard}><Text style={styles.statusLabel}>Chunks</Text><Text style={styles.statusValue}>{status.index.chunks}</Text></View>
              <View style={styles.statusCard}><Text style={styles.statusLabel}>Dimension</Text><Text style={styles.statusValue}>{status.index.embeddingDimension || '—'}</Text></View>
            </View>
          ) : null}
        </Section>

        <Section eyebrow="Documents" title="Run indexing">
          <Input multiline value={documents} onChangeText={setDocuments} />
          <Button onPress={runPipeline} disabled={running || !selectedId}>{running ? 'Indexing...' : 'Run pipeline'}</Button>
        </Section>

        <Section eyebrow="Vector search" title="Ask your knowledge base">
          <View style={styles.field}>
            <Text style={styles.label}>Query</Text>
            <Input value={query} onChangeText={setQuery} />
          </View>
          <View style={styles.toggleRow}>
            <Text style={styles.toggleLabel}>RAG answer</Text>
            <Button variant={rag ? 'secondary' : 'quiet'} onPress={() => setRag((value) => !value)}>{rag ? 'On' : 'Off'}</Button>
          </View>
          <Button onPress={search} disabled={running || !selectedId || !query.trim()}>{running ? 'Searching...' : 'Search'}</Button>
        </Section>

        {response ? (
          <Section eyebrow="Results" title="Retrieved context">
            {'answer' in response ? <Text style={styles.answer}>{response.answer}</Text> : null}
            {response.results.map((result) => (
              <View key={result.chunk.id} style={styles.result}>
                <View style={styles.resultMeta}>
                  <Text style={styles.resultSource}>{result.chunk.metadata?.documentId || result.chunk.sourceDocumentId}</Text>
                  <Text style={styles.resultScore}>{Math.round(result.score * 100)}%</Text>
                </View>
                <Text style={styles.resultText}>{result.chunk.content}</Text>
              </View>
            ))}
            {!response.results.length ? <Text style={styles.noResults}>No matching chunks found.</Text> : null}
          </Section>
        ) : null}
      </ScrollView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  selectRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 7 },
  statusGrid: { flexDirection: 'row', gap: 8, marginTop: 12 },
  statusCard: { alignItems: 'flex-start', backgroundColor: 'rgba(148,170,205,0.06)', borderRadius: 10, flex: 1, gap: 7, padding: 10 },
  statusLabel: { color: '#8fa3bf', fontSize: 10, fontWeight: '700' },
  statusValue: { color: '#edf4ff', fontSize: 15, fontWeight: '800', marginTop: 3 },
  field: { marginBottom: 11 },
  label: { color: '#8fa3bf', fontSize: 11, fontWeight: '700', marginBottom: 6 },
  toggleRow: { alignItems: 'center', flexDirection: 'row', justifyContent: 'space-between', marginBottom: 11 },
  toggleLabel: { color: '#8fa3bf', fontSize: 12, fontWeight: '700' },
  answer: { backgroundColor: 'rgba(110,168,254,0.08)', borderColor: 'rgba(110,168,254,0.2)', borderRadius: 10, borderWidth: 1, color: '#dce8ff', fontSize: 12, lineHeight: 18, padding: 11 },
  result: { borderBottomColor: 'rgba(148,170,205,0.12)', borderBottomWidth: 1, paddingVertical: 10 },
  resultMeta: { alignItems: 'center', flexDirection: 'row', justifyContent: 'space-between' },
  resultSource: { color: '#8fa3bf', fontSize: 10, fontWeight: '700' },
  resultScore: { color: '#6ee7d8', fontSize: 11, fontWeight: '900' },
  resultText: { color: '#c6d5eb', fontSize: 12, lineHeight: 17, marginTop: 6 },
  noResults: { color: '#8fa3bf', fontSize: 12, marginTop: 8 },
});
