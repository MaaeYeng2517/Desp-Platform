import { useEffect, useState } from 'react';
import { Alert, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { useLocalSearchParams } from 'expo-router';
import { Button, ErrorText, Input, Loading, Pill, Section, Screen, colors } from '../../components/Ui';
import { knowledgeBaseApi } from '../../lib/api';
import { createDefaultWorkflow, defaultComponents, categoryTone } from '../../lib/constants';
import { getApiBase } from '../../lib/storage';
import {
  ComponentDefinition,
  KnowledgeBaseInput,
  KnowledgeBaseRecord,
  MetadataInput,
  WorkflowDefinition,
  WorkflowNode,
  WorkflowNodeType,
} from '../../lib/types';

function componentFor(type: WorkflowNodeType): ComponentDefinition {
  return defaultComponents.find((component) => component.type === type) || defaultComponents[3];
}

export default function BuilderScreen() {
  const { id } = useLocalSearchParams<{ id?: string }>();
  const [apiBase, setApiBase] = useState('');
  const [catalog, setCatalog] = useState<ComponentDefinition[]>(defaultComponents);
  const [knowledgeBase, setKnowledgeBase] = useState<KnowledgeBaseRecord | null>(null);
  const [metadata, setMetadata] = useState<MetadataInput>({
    title: 'Product Support Knowledge',
    description: 'Support policies, troubleshooting, and product guidance',
    owner: 'Knowledge Team',
    version: '1.0.0',
    visibility: 'team',
    language: 'en',
    tags: ['support', 'product', 'demo'],
  });
  const [workflow, setWorkflow] = useState<WorkflowDefinition>(createDefaultWorkflow());
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [validation, setValidation] = useState<KnowledgeBaseRecord['validation']>();

  async function load() {
    setLoading(true);
    setError('');
    try {
      const storedBase = await getApiBase('http://localhost:3000/api/knowledge-base');
      setApiBase(storedBase);
      const [components, items] = await Promise.all([
        knowledgeBaseApi.catalog(storedBase).catch(() => defaultComponents),
        knowledgeBaseApi.list(storedBase),
      ]);
      setCatalog(components);
      const selected = items.find((item) => item.id === id) || items[0] || null;
      if (selected) {
        setKnowledgeBase(selected);
        setMetadata(selected.metadata || {});
        setWorkflow(selected.workflow || createDefaultWorkflow());
        setValidation(selected.validation);
      }
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to load builder');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { void load(); }, [id]);

  function updateMetadataField(field: keyof MetadataInput, value: string | string[] | undefined) {
    setMetadata((current) => ({ ...current, [field]: value }));
  }

  function addComponent(type: WorkflowNodeType) {
    const component = componentFor(type);
    const node: WorkflowNode = {
      id: `node-${Date.now()}`,
      type,
      label: component.label,
      config: { ...component.defaultConfig },
      position: { x: 40 + workflow.nodes.length * 36, y: 100 + (workflow.nodes.length % 3) * 36 },
    };
    const previous = workflow.nodes[workflow.nodes.length - 1];
    const edge = previous ? { id: `edge-${Date.now()}`, from: previous.id, to: node.id } : undefined;
    setWorkflow((current) => ({ nodes: [...current.nodes, node], edges: edge ? [...current.edges, edge] : current.edges }));
    setSelectedNodeId(node.id);
  }

  function removeNode(nodeId: string) {
    Alert.alert('Remove component', 'This also removes connections to the selected component.', [
      { style: 'cancel', text: 'Cancel' },
      {
        style: 'destructive',
        text: 'Remove',
        onPress: () => {
          setWorkflow((current) => ({
            nodes: current.nodes.filter((node) => node.id !== nodeId),
            edges: current.edges.filter((edge) => edge.from !== nodeId && edge.to !== nodeId),
          }));
          if (selectedNodeId === nodeId) setSelectedNodeId(null);
        },
      },
    ]);
  }

  async function save() {
    setSaving(true);
    setError('');
    try {
      const input: KnowledgeBaseInput = {
        name: metadata.title || 'Untitled knowledge base',
        description: metadata.description,
        metadata,
        workflow,
      };
      const saved = knowledgeBase?.id
        ? await knowledgeBaseApi.update(apiBase, knowledgeBase.id, input)
        : await knowledgeBaseApi.create(apiBase, input);
      setKnowledgeBase(saved);
      setValidation(saved.validation);
      Alert.alert('Workspace saved', saved.id ? 'Your workflow and metadata are stored.' : 'Knowledge base created.');
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to save workspace');
    } finally {
      setSaving(false);
    }
  }

  async function validate() {
    if (!knowledgeBase?.id) {
      setError('Save the workspace before validation');
      return;
    }
    setSaving(true);
    setError('');
    try {
      const result = await knowledgeBaseApi.validate(apiBase, knowledgeBase.id);
      setValidation(result.validation);
      setKnowledgeBase((current) => current ? { ...current, validation: result.validation, status: result.status } : current);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to validate workflow');
    } finally {
      setSaving(false);
    }
  }

  const selectedNode = workflow.nodes.find((node) => node.id === selectedNodeId);

  return (
    <Screen title="Workflow Builder" subtitle="Design the knowledge pipeline on mobile">
      <ScrollView showsVerticalScrollIndicator={false}>
        {loading ? <Loading label="Loading workspace" /> : null}
        {error ? <ErrorText>{error}</ErrorText> : null}
        <Section eyebrow="Metadata" title="Knowledge base details">
          <View style={styles.field}>
            <Text style={styles.label}>Name</Text>
            <Input value={metadata.title || ''} onChangeText={(value) => updateMetadataField('title', value)} />
          </View>
          <View style={styles.field}>
            <Text style={styles.label}>Description</Text>
            <Input multiline value={metadata.description || ''} onChangeText={(value) => updateMetadataField('description', value)} />
          </View>
          <View style={styles.fieldRow}>
            <View style={styles.field}>
              <Text style={styles.label}>Owner</Text>
              <Input value={metadata.owner || ''} onChangeText={(value) => updateMetadataField('owner', value)} />
            </View>
            <View style={styles.field}>
              <Text style={styles.label}>Version</Text>
              <Input value={metadata.version || ''} onChangeText={(value) => updateMetadataField('version', value)} />
            </View>
          </View>
          <View style={styles.fieldRow}>
            <View style={styles.field}>
              <Text style={styles.label}>Visibility</Text>
              <Input value={metadata.visibility || 'private'} onChangeText={(value) => updateMetadataField('visibility', value)} />
            </View>
            <View style={styles.field}>
              <Text style={styles.label}>Language</Text>
              <Input value={metadata.language || ''} onChangeText={(value) => updateMetadataField('language', value)} />
            </View>
          </View>
          <View style={styles.field}>
            <Text style={styles.label}>Tags</Text>
            <Input value={(metadata.tags || []).join(', ')} onChangeText={(value) => updateMetadataField('tags', value.split(',').map((tag) => tag.trim()).filter(Boolean))} />
          </View>
          <View style={styles.actionRow}>
            <Button variant="secondary" onPress={validate} disabled={saving}>Validate</Button>
            <Button onPress={save} disabled={saving}>{saving ? 'Saving...' : 'Save workspace'}</Button>
          </View>
          {validation ? (
            <Pill tone={validation.valid ? 'success' : 'danger'}>{validation.valid ? 'Workflow valid' : 'Workflow needs attention'}</Pill>
          ) : null}
        </Section>

        <Section eyebrow="Components" title="Add pipeline components">
          <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.componentList}>
            {catalog.map((component) => (
              <Pressable
                key={component.type}
                onPress={() => addComponent(component.type)}
                style={({ pressed }) => [styles.componentButton, { borderColor: `${categoryTone(component.category)}55` }, pressed && styles.pressed]}
              >
                <Text style={[styles.componentGlyph, { color: categoryTone(component.category) }]}>{component.label.slice(0, 2).toUpperCase()}</Text>
                <Text style={styles.componentLabel}>{component.label}</Text>
              </Pressable>
            ))}
          </ScrollView>
        </Section>

        <Section eyebrow="Canvas" title={`Workflow · ${workflow.nodes.length} nodes · ${workflow.edges.length} connections`}>
          {workflow.nodes.map((node) => {
            const component = componentFor(node.type);
            const selected = node.id === selectedNodeId;
            return (
              <Pressable
                key={node.id}
                onPress={() => setSelectedNodeId(node.id)}
                style={({ pressed }) => [styles.node, selected && styles.selectedNode, pressed && styles.pressed]}
              >
                <View style={[styles.nodeGlyph, { backgroundColor: `${categoryTone(component.category)}1f` }]}>
                  <Text style={[styles.nodeGlyphText, { color: categoryTone(component.category) }]}>{component.category.slice(0, 1)}</Text>
                </View>
                <View style={styles.nodeCopy}>
                  <Text style={styles.nodeName}>{node.label}</Text>
                  <Text style={styles.nodeType}>{component.category}</Text>
                </View>
                <Pressable onPress={() => removeNode(node.id)} style={styles.removeButton}>
                  <Text style={styles.removeText}>Remove</Text>
                </Pressable>
              </Pressable>
            );
          })}
          {selectedNode ? (
            <View style={styles.selectedConfig}>
              <Text style={styles.label}>Selected: {selectedNode.label}</Text>
              <Text style={styles.configText}>{JSON.stringify(selectedNode.config || {}, null, 2)}</Text>
            </View>
          ) : null}
        </Section>
      </ScrollView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  field: { marginBottom: 11 },
  fieldRow: { flexDirection: 'row', gap: 10, marginBottom: 11 },
  fieldRowField: { flex: 1, minWidth: 0 },
  label: { color: '#8fa3bf', fontSize: 11, fontWeight: '700', marginBottom: 6 },
  actionRow: { flexDirection: 'row', gap: 8, marginTop: 3 },
  componentList: { gap: 8, paddingRight: 4 },
  componentButton: { alignItems: 'center', backgroundColor: 'rgba(148,170,205,0.07)', borderColor: 'rgba(148,170,205,0.18)', borderRadius: 11, borderWidth: 1, minWidth: 82, padding: 10 },
  pressed: { opacity: 0.65 },
  componentGlyph: { fontSize: 11, fontWeight: '900' },
  componentLabel: { color: '#edf4ff', fontSize: 11, fontWeight: '800', marginTop: 5 },
  node: { alignItems: 'center', backgroundColor: '#172842', borderColor: 'rgba(148,170,205,0.18)', borderRadius: 12, borderWidth: 1, flexDirection: 'row', gap: 10, marginBottom: 9, padding: 10 },
  selectedNode: { borderColor: '#6ee7d8' },
  nodeGlyph: { alignItems: 'center', borderRadius: 9, height: 30, justifyContent: 'center', width: 30 },
  nodeGlyphText: { fontSize: 12, fontWeight: '900' },
  nodeCopy: { flex: 1, minWidth: 0 },
  nodeName: { color: '#edf4ff', fontSize: 13, fontWeight: '800' },
  nodeType: { color: '#8fa3bf', fontSize: 10, marginTop: 3, textTransform: 'uppercase' },
  removeButton: { padding: 7 },
  removeText: { color: '#fb7185', fontSize: 11, fontWeight: '800' },
  selectedConfig: { backgroundColor: '#050d19', borderColor: 'rgba(148,170,205,0.14)', borderRadius: 9, borderWidth: 1, marginTop: 8, padding: 10 },
  configText: { color: '#8fa3bf', fontFamily: 'Courier New', fontSize: 10, lineHeight: 15, marginTop: 6 },
});
