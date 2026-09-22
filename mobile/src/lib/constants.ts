import { ComponentDefinition, WorkflowDefinition, WorkflowNodeType } from './types';

export const defaultApiBase =
  process.env.EXPO_PUBLIC_API_BASE ||
  'http://localhost:3000/api/knowledge-base';

export const defaultTypes: WorkflowNodeType[] = [
  'source_pdf',
  'extract_text',
  'clean_text',
  'chunk',
  'metadata',
  'embedding',
  'vector_database',
  'knowledge_base',
  'rag',
  'agent',
];

export const defaultComponents: ComponentDefinition[] = [
  { type: 'source_pdf', label: 'PDF', category: 'Sources', description: 'Load text from PDF files', defaultConfig: { extractLayout: true } },
  { type: 'source_docx', label: 'DOCX', category: 'Sources', description: 'Load text from Word documents', defaultConfig: { includeTables: true } },
  { type: 'source_csv', label: 'CSV', category: 'Sources', description: 'Load rows from a CSV file', defaultConfig: { delimiter: ',' } },
  { type: 'source_website', label: 'Website', category: 'Sources', description: 'Crawl and load web content', defaultConfig: { maxPages: 10 } },
  { type: 'source_database', label: 'Database', category: 'Sources', description: 'Read rows from a database query', defaultConfig: { batchSize: 500 } },
  { type: 'source_api', label: 'API', category: 'Sources', description: 'Ingest JSON from an API endpoint', defaultConfig: { method: 'GET' } },
  { type: 'extract_text', label: 'Extract Text', category: 'Processing', description: 'Extract readable text', defaultConfig: { preserveParagraphs: true } },
  { type: 'clean_text', label: 'Clean Text', category: 'Processing', description: 'Remove noise and normalize text', defaultConfig: { removeExtraWhitespace: true } },
  { type: 'chunk', label: 'Chunk', category: 'Processing', description: 'Split content into chunks', defaultConfig: { chunkSize: 500, overlap: 50 } },
  { type: 'metadata', label: 'Metadata', category: 'Metadata', description: 'Attach structured metadata', defaultConfig: { requiredFields: ['source', 'language'] } },
  { type: 'embedding', label: 'Embedding', category: 'Processing', description: 'Create vector embeddings', defaultConfig: { dimension: 32, model: 'local-hash-v1' } },
  { type: 'reranking', label: 'Reranking', category: 'AI', description: 'Reorder search results', defaultConfig: { topK: 5 } },
  { type: 'vector_database', label: 'Vector DB', category: 'Storage', description: 'Store and index embeddings', defaultConfig: { index: 'cosine' } },
  { type: 'knowledge_base', label: 'Knowledge Base', category: 'Storage', description: 'Publish an indexed collection', defaultConfig: { publish: true } },
  { type: 'rag', label: 'RAG', category: 'AI', description: 'Retrieve context for an answer', defaultConfig: { topK: 4 } },
  { type: 'agent', label: 'AI Agent', category: 'AI', description: 'Expose the knowledge base', defaultConfig: { temperature: 0.2 } },
];

export function createDefaultWorkflow(): WorkflowDefinition {
  const nodes = defaultTypes.map((type, index) => {
    const component = defaultComponents.find((item) => item.type === type) || defaultComponents[7];
    return {
      id: `node-${index + 1}`,
      type,
      label: component.label,
      config: { ...component.defaultConfig },
      position: { x: 40 + index * 180, y: 120 },
    };
  });
  return {
    nodes,
    edges: nodes.slice(0, -1).map((node, index) => ({
      id: `edge-${index + 1}`,
      from: node.id,
      to: nodes[index + 1].id,
    })),
  };
}

export const defaultDocuments = JSON.stringify(
  [
    {
      id: 'demo-refunds',
      content: 'Customers can request a refund within 30 days of purchase. Refunds return to the original payment method within five business days.',
      metadata: { source: 'refund-policy', language: 'en' },
    },
    {
      id: 'demo-password',
      content: 'To reset a password, open the sign in screen, choose forgot password, and follow the email verification link. Contact support if the email does not arrive.',
      metadata: { source: 'account-help', language: 'en' },
    },
    {
      id: 'demo-export',
      content: 'Export reports from the analytics page. Choose CSV for spreadsheets or JSON for API integrations, then confirm the date range before exporting.',
      metadata: { source: 'analytics-guide', language: 'en' },
    },
  ],
  null,
  2,
);

export function categoryTone(category: string) {
  if (category === 'Sources') return '#5eead4';
  if (category === 'Processing') return '#93c5fd';
  if (category === 'Metadata') return '#c4b5fd';
  if (category === 'Storage') return '#f0abfc';
  return '#fbbf63';
}
