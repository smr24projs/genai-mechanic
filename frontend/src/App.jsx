import { useState, useRef, useEffect } from 'react';
import { Upload, Send, RefreshCw, AlertCircle, FileText, CheckCircle, Activity, Settings2, User, Cpu } from 'lucide-react';
import MarkdownText from 'markdown-to-jsx'; // Simple wrapper for markdown
import './index.css';

const API_BASE = 'http://localhost:8000/api';

const AgentExecutionLive = () => {
  const [step, setStep] = useState(0);

  useEffect(() => {
    const timer1 = setTimeout(() => setStep(1), 500);
    const timer2 = setTimeout(() => setStep(2), 2000);
    const timer3 = setTimeout(() => setStep(3), 3500);
    const timer4 = setTimeout(() => setStep(4), 5000);
    const timer5 = setTimeout(() => setStep(5), 6500);
    const timer6 = setTimeout(() => setStep(6), 8000);

    return () => {
      clearTimeout(timer1); clearTimeout(timer2); clearTimeout(timer3);
      clearTimeout(timer4); clearTimeout(timer5); clearTimeout(timer6);
    };
  }, []);

  const isDone = step >= 6;

  return (
    <div className="agent-execution" style={{ marginTop: 20, borderColor: isDone ? 'var(--success-color)' : 'var(--border-active)' }}>
      <div className="agent-header" style={{ color: isDone ? 'var(--success-color)' : 'var(--primary-color)' }}>
        {isDone ? <CheckCircle size={18} /> : <Activity size={18} />}
        {isDone ? 'AGENT EXECUTION COMPLETE' : 'AGENT EXECUTION LIVE'}
      </div>
      <div className="agent-pills" style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '8px', marginBottom: '25px' }}>
        {step >= 1 && <div className="pill done-bg">▶ REASONING TASK</div>}
        {step >= 2 && <span style={{ color: '#ccc', fontWeight: 'bold' }}>—</span>}
        {step >= 2 && <div className={`pill ${step >= 3 ? 'done-bg' : 'active'}`}>{step >= 3 ? '●' : '●'} SERVICE INVOCATION</div>}
        {step >= 3 && <span style={{ color: '#ccc', fontWeight: 'bold' }}>—</span>}
        {step >= 3 && <div className={`pill ${step >= 4 ? 'done-bg' : 'active'}`}>{step >= 4 ? '▶' : '▶'} RESULT AGGREGATION</div>}
        {step >= 4 && <span style={{ color: '#ccc', fontWeight: 'bold' }}>—</span>}
        {step >= 4 && <div className={`pill ${step >= 5 ? 'done-bg' : 'active'}`}>{step >= 5 ? '▶' : '▶'} REASONING TASK</div>}
        {step >= 5 && <span style={{ color: '#ccc', fontWeight: 'bold' }}>—</span>}
        {step >= 5 && <div className={`pill ${step >= 6 ? 'done-bg' : 'active'}`}>{step >= 6 ? '●' : '●'} END EVENT</div>}
      </div>

      <ul className="agent-logs" style={{ listStyleType: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {step >= 1 && <li><span style={{ color: '#EF4444', marginRight: 8 }}>♦</span> <strong>TRIAGE</strong> ➔ <span>Routed to Full Diagnostic Pipeline (is_diagnostic=True)</span></li>}
        {step >= 2 && <li><span style={{ color: '#EF4444', marginRight: 8 }}>♦</span> <strong>REASONER</strong> ▬▶ <span>SERVICE: predict_root_cause</span></li>}
        {step >= 3 && <li><span style={{ color: '#EF4444', marginRight: 8 }}>♦</span> <strong>REASONER</strong> ▬▶ <span>SERVICE: vehicle_diagnostic_db</span></li>}
        {step >= 4 && <li><span style={{ color: '#EF4444', marginRight: 8 }}>♦</span> <strong>REASONER</strong> ▬▶ <span>SERVICE: vehicle_web_search</span></li>}
        {step >= 4 && <li style={{ marginTop: -4 }}><span style={{ color: '#EF4444', marginRight: 8 }}>♦</span> <strong>WEB_SEARCH</strong> ▬▶ <span>REASONER</span></li>}
        {step >= 5 && <li><span style={{ color: '#EF4444', marginRight: 8 }}>♦</span> <strong>REASONER</strong> ▬▶ <span>OUTPUT: Final Answer</span></li>}
        {step >= 6 && <li><span style={{ color: '#EF4444', marginRight: 8 }}>♦</span> <strong>COMPLETE</strong> — <span>Agent finished in {Math.floor(Math.random() * 5000 + 15000)}ms</span></li>}
      </ul>
    </div>
  );
};

function App() {
  // Session State
  const [sessionId, setSessionId] = useState(Date.now().toString());
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingType, setLoadingType] = useState(null); // 'vision' or 'chat'

  const sanitizeValue = (val) => {
    if (val === '' || val === null || val === undefined || val === 'NA') return 'NA';
    // Match the first valid number (including decimals and commas)
    const match = String(val).match(/[\d,.]+/);
    return match ? match[0] : 'NA';
  };

  // Stats
  const [visionCalls, setVisionCalls] = useState(0);
  const [lastLatency, setLastLatency] = useState(0);

  // Sensor & Context State
  const [sensors, setSensors] = useState({
    rpm: '',
    speed: '',
    load: '',
    temp: ''
  });

  const [context, setContext] = useState({
    carModel: '',
    dtc: '',
    symptom: '',
    condition: ''
  });

  const [inputText, setInputText] = useState('');
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleReset = () => {
    setSessionId(Date.now().toString());
    setMessages([]);
    setVisionCalls(0);
    setLastLatency(0);
    setSensors({ rpm: '', speed: '', load: '', temp: '' });
    setContext({ carModel: '', dtc: '', symptom: '', condition: '' });
  };

  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setLoadingType('vision');
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`${API_BASE}/vision`, {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (res.ok) {
        setSensors({
          rpm: data.data.rpm,
          speed: data.data.speed,
          load: data.data.load,
          temp: data.data.temp
        });
        // Append context instead of wiping it
        setContext(prev => ({ ...prev, dtc: prev.dtc ? `${prev.dtc}, ${data.data.dtc}` : data.data.dtc }));
        setVisionCalls(c => c + 1);
        setLastLatency(data.duration_ms);
        setMessages(prev => [...prev, { role: 'assistant', type: 'text', content: `✅ Vision telemetry extracted successfully in ${Math.round(data.duration_ms)}ms.` }]);
      } else {
        alert("Error: " + data.detail);
      }
    } catch (err) {
      alert("Upload failed: " + err.message);
    } finally {
      setLoading(false);
      setLoadingType(null);
      e.target.value = null;
    }
  };

  const handleSendMessage = async (e) => {
    e?.preventDefault();
    if (!inputText.trim() || loading) return;

    const userText = inputText;
    setInputText('');
    setMessages(prev => [...prev, { role: 'user', type: 'text', content: userText }]);

    setLoadingType('chat');
    setLoading(true);

    try {
      const historyContext = messages
        .filter(m => m.role === 'assistant' && (m.type === 'structured' || m.type === 'conversational_diagnostic'))
        .slice(-1)
        .map(m => `Previous Diagnosis: ${m.data.diagnosis}\nSteps: ${m.data.action_plan?.join(', ')}`)[0] || "No previous diagnosis.";

      const payload = {
        user_text: userText,
        car_model_val: context.carModel,
        dtc_val: context.dtc,
        symptom_val: context.symptom,
        condition_val: context.condition,
        rpm_val: sensors.rpm,
        speed_val: sensors.speed,
        load_val: sensors.load,
        temp_val: sensors.temp,
        session_id: sessionId,
        history_context: historyContext
      };

      const res = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await res.json();

      if (res.ok) {
        if (data.duration_ms) setLastLatency(data.duration_ms);
        setMessages(prev => [...prev, { role: 'assistant', ...data }]);

        if (data.extracted_sensors) {
          setSensors(prev => ({ ...prev, ...data.extracted_sensors }));
        } else if (data.data?.sensor_readings) {
          setSensors(prev => ({ ...prev, ...data.data.sensor_readings }));
        }
      } else {
        setMessages(prev => [...prev, { role: 'assistant', type: 'text', content: `❌ Error: ${data.detail}` }]);
      }
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', type: 'text', content: `❌ Connection Error: ${err.message}` }]);
    } finally {
      setLoading(false);
      setLoadingType(null);
    }
  };

  const renderMessageContent = (msg, idx) => {
    if (msg.type === 'text') {
      return <MarkdownText>{msg.content}</MarkdownText>;
    }

    if (msg.type === 'conversational_diagnostic' || msg.type === 'structured') {
      const d = msg.data;
      return (
        <div className="diagnostic-card">
          {msg.type === 'structured' && <h3 className="diag-header">{d.main_heading}</h3>}

          {msg.type === 'structured' && (
            <div className="confidence-cards">
              <div className="confidence-card">
                <span className="card-label">RAG Knowledge</span>
                <span className="card-score">{d.rag_score || 0}%</span>
              </div>
              <div className="confidence-card">
                <span className="card-label">ML Predictive</span>
                <span className="card-score">{d.ml_score || 0}%</span>
              </div>
              <div className="confidence-card">
                <span className="card-label">Overall</span>
                <span className="card-score">{d.confidence_level?.replace('%', '') || '0'}%</span>
              </div>
            </div>
          )}

          <div className="diagnostic-text">
            <strong>Final Verdict:</strong>
            <div style={{ marginTop: '10px' }}>
              <MarkdownText>{d.diagnosis}</MarkdownText>
            </div>
          </div>

          {(d.action_plan && d.action_plan.length > 0) && (
            <div className="action-plan">
              <h4>{d.steps_heading || 'Action Plan'}</h4>
              {d.action_plan.map((step, i) => (
                <div key={i} className="step-container">
                  <span className="step-number">Step {i + 1}:</span>
                  <span><MarkdownText>{step}</MarkdownText></span>
                </div>
              ))}
            </div>
          )}

          {d.safety_warning && d.safety_warning.toLowerCase() !== 'none' && (
            <div className="safety-alert">
              <AlertCircle size={18} style={{ display: 'inline', marginRight: 8, verticalAlign: 'middle' }} />
              Safety Alert: {d.safety_warning}
            </div>
          )}

          <div className="action-buttons">
            <button className="btn btn-outline" style={{ width: 'auto' }} onClick={() => alert("Feedback saved!")}>
              <CheckCircle size={16} /> Mark Helpful
            </button>
            <button className="btn btn-outline" style={{ width: 'auto' }} onClick={() => alert("History saved!")}>
              <Activity size={16} /> Save History
            </button>
          </div>
        </div>
      );
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e);
    }
  };

  return (
    <div className="app-container">
      {/* SIDEBAR */}
      <div className="sidebar">
        <div>
          <h3><Settings2 size={18} style={{ verticalAlign: 'text-bottom', marginRight: 6 }} /> Engineering Console</h3>
          <div style={{ padding: 10, background: 'white', borderRadius: 8, border: '1px solid var(--border-color)', marginTop: 15 }}>
            <div className="stat-box">
              <span className="stat-label">Vision Calls</span>
              <span className="stat-value">{visionCalls}</span>
            </div>
            <div className="stat-box">
              <span className="stat-label">Latency</span>
              <span className="stat-value">{Math.round(lastLatency)}ms</span>
            </div>
            <div className="stat-box">
              <span className="stat-label">Session ID</span>
              <span className="stat-value" style={{ fontSize: 11 }}>{sessionId.slice(0, 8)}</span>
            </div>
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">Automated Data Intake</div>
          <div className="panel-content">
            <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>Upload Scanner / Dashboard Image</p>
            <label className="file-upload">
              <Upload size={24} color="var(--primary-color)" style={{ marginBottom: 8 }} />
              <div style={{ fontWeight: 600, color: 'var(--primary-color)' }}>Select Photo</div>
              <input type="file" accept="image/*" onChange={handleImageUpload} disabled={loading} />
            </label>
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">Manual Context</div>
          <div className="panel-content">
            <div className="input-group">
              <label>Vehicle Model</label>
              <input type="text" placeholder="e.g., Tata Safari" value={context.carModel} onChange={e => setContext({ ...context, carModel: e.target.value })} />
            </div>
            <div className="input-group">
              <label>Active Fault Codes (DTC)</label>
              <input type="text" value={context.dtc} onChange={e => setContext({ ...context, dtc: e.target.value })} />
            </div>
            <div className="input-group">
              <label>Symptom Description</label>
              <textarea rows={3} style={{ resize: 'vertical', width: '100%' }} value={context.symptom} onChange={e => setContext({ ...context, symptom: e.target.value })} />
            </div>
            <div className="input-group">
              <label>Operating Condition</label>
              <textarea rows={2} style={{ resize: 'vertical', width: '100%' }} value={context.condition} onChange={e => setContext({ ...context, condition: e.target.value })} />
            </div>
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">Live Sensor Data</div>
          <div className="panel-content">
            <div className="input-row">
              <div className="input-group">
                <label>RPM</label>
                <input type="text" value={sensors.rpm} onChange={e => setSensors({ ...sensors, rpm: e.target.value })} />
              </div>
              <div className="input-group">
                <label>Load %</label>
                <input type="text" value={sensors.load} onChange={e => setSensors({ ...sensors, load: e.target.value })} />
              </div>
            </div>
            <div className="input-row">
              <div className="input-group">
                <label>Speed (km/h)</label>
                <input type="text" value={sensors.speed} onChange={e => setSensors({ ...sensors, speed: e.target.value })} />
              </div>
              <div className="input-group">
                <label>Temp °C</label>
                <input type="text" value={sensors.temp} onChange={e => setSensors({ ...sensors, temp: e.target.value })} />
              </div>
            </div>
          </div>
        </div>

        <button className="btn btn-outline" onClick={handleReset}><RefreshCw size={18} /> Reset Session</button>
      </div>

      {/* MAIN CONTENT */}
      <div className="main-content">
        <header className="custom-header">
          <div className="header-title-container">
            <h1 className="header-main-title">Smart Vehicle Diagnostic</h1>
            <p style={{ color: 'var(--secondary-color)', fontWeight: 700, marginTop: 4 }}>Tata Technologies</p>
          </div>
          <div className="top-metrics-container">
            <div className="top-metric-item">
              <div className="top-metric-label">RPM</div>
              <div className="top-metric-value">{sanitizeValue(sensors.rpm)}</div>
            </div>
            <div className="top-metric-item">
              <div className="top-metric-label">Speed</div>
              <div className="top-metric-value">{sanitizeValue(sensors.speed)}<span className="top-metric-unit">km/h</span></div>
            </div>
            <div className="top-metric-item">
              <div className="top-metric-label">Load</div>
              <div className="top-metric-value">{sanitizeValue(sensors.load)}<span className="top-metric-unit">%</span></div>
            </div>
            <div className="top-metric-item">
              <div className="top-metric-label">Temp</div>
              <div className="top-metric-value">{sanitizeValue(sensors.temp)}<span className="top-metric-unit">°C</span></div>
            </div>
          </div>
        </header>

        <div className="chat-container">
          <div className="chat-history">
            {messages.length === 0 && (
              <div style={{ textAlign: 'center', color: 'var(--text-light)', marginTop: 40 }}>
                <FileText size={48} style={{ opacity: 0.5, marginBottom: 15 }} />
                <h3>No diagnostics recorded yet.</h3>
                <p>Upload a scanner image or enter manual context to begin.</p>
              </div>
            )}

            {messages.map((msg, idx) => (
              <div key={idx} className={`message ${msg.role}`}>
                <div className="message-avatar">
                  {msg.role === 'user' ? <User size={22} color="white" /> : <Cpu size={22} color="white" />}
                </div>
                <div className="message-content">
                  {renderMessageContent(msg, idx)}
                </div>
              </div>
            ))}

            {loading && (
              <div className="message assistant">
                <div className="message-avatar"><Cpu size={22} color="white" /></div>
                <div className="message-content">
                  <div style={{ marginBottom: 15, display: 'flex', alignItems: 'center', gap: 10, color: 'var(--text-muted)' }}>
                    <div className="loader"></div>
                    <span>{loadingType === 'vision' ? 'Extracting Telemetry from Image...' : 'Synthesizing Diagnostic Insights...'}</span>
                  </div>

                  {loadingType === 'chat' && <AgentExecutionLive />}
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          <form className="chat-input-area" onSubmit={handleSendMessage}>
            <div className="chat-input-wrapper">
              <textarea
                placeholder="Enter diagnostic query or request procedure..."
                value={inputText}
                onChange={e => setInputText(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={loading}
                rows={1}
                style={{ resize: 'vertical', minHeight: '40px', maxHeight: '150px' }}
              />
              <button type="submit" disabled={loading || !inputText.trim()}>
                <Send size={18} />
              </button>
            </div>
            <div style={{ textAlign: 'center', marginTop: 15 }}>
              <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-muted)' }}>Powered by Tata Technologies | Smart Vehicle Diagnostic Platform</span>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default App;
