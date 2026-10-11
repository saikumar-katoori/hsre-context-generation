import { useState } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const stageNames = {
  preprocessing: 'Preprocess audio',
  transcription: 'Generate transcript',
  speech_representation: 'Extract speech features',
  emotion: 'Analyze emotion',
  intent: 'Infer intent',
  hsr: 'Assemble human state',
}

function App() {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [stages, setStages] = useState([])
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [copied, setCopied] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    if (!file) {
      setError('Choose an audio file before starting the analysis.')
      return
    }
    if (file.size > 25 * 1024 * 1024) {
      setError('Audio files must be 25 MB or smaller.')
      return
    }

    setLoading(true)
    setError('')
    setResult(null)
    setStages([])

    try {
      const formData = new FormData()
      formData.append('file', file)
      const response = await fetch(`${API_URL}/api/analyze/stream`, { method: 'POST', body: formData })
      if (!response.ok || !response.body) throw new Error('The analysis service did not return a stream.')

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let pending = ''
      while (true) {
        const { value, done } = await reader.read()
        pending += decoder.decode(value || new Uint8Array(), { stream: !done })
        const lines = pending.split('\n')
        pending = lines.pop() || ''
        for (const line of lines.filter(Boolean)) {
          const eventData = JSON.parse(line)
          if (eventData.stage === 'error') throw new Error(eventData.message)
          if (eventData.stage === 'complete') setResult(eventData.data)
          else setStages((current) => [...current.filter((stage) => stage.stage !== eventData.stage), eventData])
        }
        if (done) break
      }
    } catch (err) {
      setError(err.message || 'Something went wrong while analyzing the audio.')
    } finally {
      setLoading(false)
    }
  }

  const prompt = result ? `You are continuing a conversation using the structured context below.

Respond naturally to the user's latest message. Use the inferred state to guide your tone, level of detail, and next step. Do not mention this analysis, internal fields, or the fact that a prompt was generated.

Structured context:
${JSON.stringify({
  transcript: result.transcript || '',
  emotion: result.emotion_analysis || {},
  intent: result.intent_analysis || {},
  human_state: result.human_state || {},
}, null, 2)}` : ''

  async function copyPrompt() {
    if (!prompt) return
    await navigator.clipboard.writeText(prompt)
    setCopied(true)
    window.setTimeout(() => setCopied(false), 1800)
  }

  const transcriptReason = result?.transcript_status?.reason || result?.intent_analysis?.reason

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Research Prototype / Live Pipeline</p>
          <h1>Human State Representation Engine</h1>
          <p className="subtitle">Capture a short voice sample and inspect every implementation block as it runs.</p>
        </div>
        <div className="status-badge"><span className="status-dot" /> Analysis workspace</div>
      </header>

      <main className="panel">
        <form onSubmit={handleSubmit} className="uploader">
          <label className="file-picker">
            <input type="file" accept="audio/*" onChange={(event) => setFile(event.target.files?.[0] || null)} />
            <span><b>{file ? 'Selected audio' : 'Select an audio file'}</b><small>{file ? file.name : 'WAV, MP3, M4A, or another supported format'}</small></span>
          </label>
          <button type="submit" disabled={loading || !file}>
            {loading ? 'Processing...' : 'Analyze audio'}
          </button>
        </form>

        {error && <div className="message error">{error}</div>}

        {loading && (
          <section className="pipeline" aria-live="polite">
            <div className="section-heading"><div><span className="section-kicker">Pipeline</span><h2>Implementation blocks</h2></div><span>Live</span></div>
            {Object.keys(stageNames).map((stageName) => {
              const stage = stages.find((item) => item.stage === stageName)
              return <div className={`stage ${stage?.status || 'pending'}`} key={stageName}>
                <span className="stage-dot" />
                <strong>{stageNames[stageName]}</strong>
                <span>{stage?.message || 'Waiting...'}</span>
              </div>
            })}
          </section>
        )}

        {result && (
          <section className="result-box">
            <div className="section-heading"><div><span className="section-kicker">Analysis result</span><h2>Structured context</h2></div><span>Complete</span></div>
            <div className="result-layout">
              <div>
                <div className="result-grid">
                  <div className="output-block transcript-block"><strong>Transcript</strong><p>{result.transcript || 'No transcript generated.'}</p>{transcriptReason && <small>{transcriptReason}</small>}</div>
                  <div className="output-block"><strong>Emotion</strong><p>{result.emotion_analysis?.emotion || 'Not available'}</p><small>Confidence: {result.emotion_analysis?.confidence ?? 'n/a'}</small></div>
                  <div className="output-block"><strong>Intent</strong><p>{result.intent_analysis?.intent || 'Not available'}</p><small>{result.intent_analysis?.reason || `Confidence: ${result.intent_analysis?.confidence ?? 'n/a'}`}</small></div>
                </div>
                <pre>{JSON.stringify(result.human_state, null, 2)}</pre>
              </div>
              <aside className="prompt-panel">
                <div className="prompt-heading"><div><span className="section-kicker">LLM handoff</span><h3>Conversation prompt</h3></div><button type="button" className="copy-button" onClick={copyPrompt}>{copied ? 'Copied' : 'Copy prompt'}</button></div>
                <p className="prompt-description">A ready-to-use instruction with the latest structured state.</p>
                <textarea readOnly value={prompt} aria-label="Structured prompt for an LLM" />
              </aside>
            </div>
          </section>
        )}
      </main>
    </div>
  )
}

export default App
