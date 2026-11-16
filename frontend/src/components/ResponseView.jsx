import { Link } from 'react-router-dom';
import Disclaimer from './Disclaimer.jsx';

const CONFIDENCE = {
  insufficient: ['Not enough information', 'warn'],
  low: ['Low confidence', 'warn'],
  medium: ['Based on stored references', ''],
};

// Renders a structured assistant answer (SRS §3.1 layout): explanation, procedure,
// sources, uncertainty notes and the mandatory disclaimer. Text is rendered through
// React (auto-escaped) – never via innerHTML (NFR-SEC-06).
export default function ResponseView({ message }) {
  const [label, tone] = CONFIDENCE[message.confidence] || ['', ''];
  return (
    <div className="card">
      <div className="row spread">
        <strong>Assistant</strong>
        <span className="row">
          {message.domain && <span className="badge">{message.domain}</span>}
          {label && <span className={`badge ${tone}`}>{label}</span>}
        </span>
      </div>

      <p>{message.text}</p>

      {message.procedure && (
        <>
          <div className="section-title">What you will need</div>
          <ul className="steps">{message.procedure.prerequisites.map((p) => <li key={p}>{p}</li>)}</ul>
          <div className="section-title">Procedure</div>
          <ol className="steps">{message.procedure.steps.map((s) => <li key={s}>{s}</li>)}</ol>
        </>
      )}

      {message.sources?.length > 0 && (
        <>
          <div className="section-title">Sources</div>
          {message.sources.map((s) => (
            <div className="source" key={s.id}>
              <a href={s.link} target="_blank" rel="noopener noreferrer">{s.title}</a>
              <span className="muted" style={{ fontSize: '.85rem' }}>{s.source}</span>
              <span className={`badge ${s.status}`}>{s.status}</span>
            </div>
          ))}
        </>
      )}

      {message.template && (
        <p style={{ marginTop: '.9rem' }}>📄 Related template: <Link to={`/templates?open=${message.template.id}`}>{message.template.name}</Link></p>
      )}

      {message.notes?.length > 0 && (
        <div className="alert warn" style={{ marginTop: '.9rem' }}>
          {message.notes.map((n) => <div key={n}>⚠️ {n}</div>)}
        </div>
      )}

      <div style={{ marginTop: '.9rem' }}>
        <Disclaimer>{message.disclaimer}</Disclaimer>
      </div>
      {(message.confidence === 'insufficient' || message.confidence === 'low' || message.domain === 'Family' || message.domain === 'Criminal') && (
        <p className="muted" style={{ fontSize: '.85rem', marginBottom: 0 }}>
          This situation may need case-specific advice – consider speaking to a qualified lawyer or your State Legal Services Authority.
        </p>
      )}
    </div>
  );
}
