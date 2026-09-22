import Link from 'next/link';

export default function Home() {
  return (
    <main className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <h1 className="text-xl font-bold text-primary-600">
                  Knowledge Engineering Platform
                </h1>
              </div>
              <div className="hidden sm:ml-6 sm:flex space-x-8">
                <Link href="/dashboard" className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center pt-1 px-1 border-b-2 text-sm font-medium">
                  Dashboard
                </Link>
                <Link href="/knowledge-bases" className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center pt-1 px-1 border-b-2 text-sm font-medium">
                  Knowledge Bases
                </Link>
                <Link href="/workflows" className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center pt-1 px-1 border-b-2 text-sm font-medium">
                  Workflows
                </Link>
                <Link href="/search" className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center pt-1 px-1 border-b-2 text-sm font-medium">
                  Search Studio
                </Link>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="lg:grid lg:grid-cols-2 lg:gap-8">
            <div>
              <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">
                Transform Knowledge into Intelligence
              </h1>
              <p className="mt-6 text-xl text-gray-600">
                A comprehensive platform for building, managing, and querying knowledge bases with AI-powered retrieval, hybrid search, and visual workflow engineering.
              </p>
              <div className="mt-10 flex gap-4">
                <Link href="/dashboard" className="bg-primary-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-primary-700">
                  Get Started
                </Link>
                <Link href="/search" className="bg-gray-100 text-gray-700 px-6 py-3 rounded-lg font-medium hover:bg-gray-200">
                  Try Search Studio
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <div className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            Platform Capabilities
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-2">Multi-Source Ingestion</h3>
              <p className="text-gray-600">Connect to PDFs, websites, databases, APIs, and more with a unified connector framework.</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-2">Visual Workflow Builder</h3>
              <p className="text-gray-600">Design knowledge pipelines with drag-and-drop canvas and executable workflows.</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-2">Hybrid Search</h3>
              <p className="text-gray-600">Combine BM25 keyword, vector, metadata, and graph search for maximum relevance.</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-2">RAG Engine</h3>
              <p className="text-gray-600">Context engineering with citation, verification, and evaluation built-in.</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-2">AI Agent</h3>
              <p className="text-gray-600">Agentic RAG with tool calling, MCP integration, and multi-step reasoning.</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-2">Governance</h3>
              <p className="text-gray-600">RBAC, multi-tenant isolation, audit logging, and approval workflows.</p>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}