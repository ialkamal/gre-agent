import Link from "next/link";

export default function Home() {
  return (
    <div className="max-w-6xl mx-auto px-4 py-12">
      {/* Hero Section */}
      <div className="text-center mb-16">
        <h1 className="text-5xl font-bold text-gray-900 mb-6">
          Master Your GRE Issue Writing
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
          Get detailed feedback from our AI-powered multi-agent grading system.
          Three independent graders evaluate your essay across 8 dimensions,
          building consensus to provide accurate, actionable feedback.
        </p>
        <Link
          href="/practice"
          className="inline-flex items-center gap-2 bg-primary-600 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:bg-primary-700 transition shadow-lg"
        >
          ✍️ Start Practicing
        </Link>
      </div>

      {/* Features Grid */}
      <div className="grid md:grid-cols-3 gap-8 mb-16">
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <div className="text-4xl mb-4">🎯</div>
          <h3 className="text-xl font-semibold mb-2">8 Dimension Analysis</h3>
          <p className="text-gray-600">
            Detailed scoring on thesis clarity, reasoning, evidence, structure,
            analysis depth, language, grammar, and coherence.
          </p>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <div className="text-4xl mb-4">🤖</div>
          <h3 className="text-xl font-semibold mb-2">Multi-Agent Grading</h3>
          <p className="text-gray-600">
            Three independent AI graders with different perspectives reach
            consensus for more reliable and balanced feedback.
          </p>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <div className="text-4xl mb-4">📈</div>
          <h3 className="text-xl font-semibold mb-2">Track Your Progress</h3>
          <p className="text-gray-600">
            Long-term memory tracks your weak areas across sessions, providing
            personalized recommendations for improvement.
          </p>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <div className="text-4xl mb-4">🔍</div>
          <h3 className="text-xl font-semibold mb-2">Fact-Checking</h3>
          <p className="text-gray-600">
            Evidence agent verifies claims and examples using web search,
            ensuring your facts are accurate.
          </p>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <div className="text-4xl mb-4">⏱️</div>
          <h3 className="text-xl font-semibold mb-2">Timed Practice</h3>
          <p className="text-gray-600">
            Built-in 30-minute timer helps you practice under real GRE test
            conditions.
          </p>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <div className="text-4xl mb-4">🎓</div>
          <h3 className="text-xl font-semibold mb-2">GRE-Aligned Scoring</h3>
          <p className="text-gray-600">
            Scoring based on official GRE rubric (0-6 scale) with calibrated AI
            agents for accurate assessment.
          </p>
        </div>
      </div>

      {/* How It Works */}
      <div className="bg-white rounded-xl p-8 shadow-sm border border-gray-100 mb-16">
        <h2 className="text-2xl font-bold text-center mb-8">How It Works</h2>
        <div className="flex flex-col md:flex-row items-center justify-between gap-8">
          <div className="text-center">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center text-2xl mx-auto mb-3">
              1
            </div>
            <h4 className="font-semibold">Write Your Essay</h4>
            <p className="text-sm text-gray-600">
              Choose a prompt and write your response
            </p>
          </div>
          <div className="text-3xl text-gray-300 hidden md:block">→</div>
          <div className="text-center">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center text-2xl mx-auto mb-3">
              2
            </div>
            <h4 className="font-semibold">Submit for Grading</h4>
            <p className="text-sm text-gray-600">
              3 graders × 8 agents evaluate your essay
            </p>
          </div>
          <div className="text-3xl text-gray-300 hidden md:block">→</div>
          <div className="text-center">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center text-2xl mx-auto mb-3">
              3
            </div>
            <h4 className="font-semibold">Consensus Building</h4>
            <p className="text-sm text-gray-600">
              Scores averaged, feedback merged
            </p>
          </div>
          <div className="text-3xl text-gray-300 hidden md:block">→</div>
          <div className="text-center">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center text-2xl mx-auto mb-3">
              4
            </div>
            <h4 className="font-semibold">Get Feedback</h4>
            <p className="text-sm text-gray-600">
              Detailed scores and improvement tips
            </p>
          </div>
        </div>
      </div>

      {/* CTA */}
      <div className="text-center bg-gradient-to-r from-primary-600 to-primary-800 rounded-xl p-12 text-white">
        <h2 className="text-3xl font-bold mb-4">
          Ready to Improve Your Score?
        </h2>
        <p className="text-primary-100 mb-6">
          Start practicing with real GRE prompts and get instant, detailed
          feedback.
        </p>
        <Link
          href="/practice"
          className="inline-flex items-center gap-2 bg-white text-primary-700 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition"
        >
          Start Your First Essay →
        </Link>
      </div>
    </div>
  );
}
