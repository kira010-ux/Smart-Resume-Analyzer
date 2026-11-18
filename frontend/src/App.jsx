import { useEffect, useState } from "react";
import { analyzeMatch, getHistory } from "./api";

const emptyResult = null;

function InputPanel({ label, eyebrow, text, setText, file, setFile }) {
  const [mode, setMode] = useState("paste");

  return (
    <section className="input-panel">
      <div className="panel-heading">
        <div>
          <span className="eyebrow">{eyebrow}</span>
          <h2>{label}</h2>
        </div>
        <span className="panel-index">{label === "Resume" ? "01" : "02"}</span>
      </div>
      <div className="mode-switch" role="tablist" aria-label={`${label} input mode`}>
        <button className={mode === "paste" ? "active" : ""} onClick={() => setMode("paste")} type="button">Paste text</button>
        <button className={mode === "upload" ? "active" : ""} onClick={() => setMode("upload")} type="button">Upload file</button>
      </div>
      {mode === "paste" ? (
        <textarea
          value={text}
          onChange={(event) => setText(event.target.value)}
          placeholder={label === "Resume" ? "Paste your experience, skills, and achievements..." : "Paste the role requirements and responsibilities..."}
          aria-label={label}
        />
      ) : (
        <label className="dropzone">
          <span className="upload-mark">+</span>
          <strong>{file ? file.name : "Choose a document"}</strong>
          <small>PDF, DOCX, or TXT · max 5 MB</small>
          <input type="file" accept=".pdf,.docx,.txt" onChange={(event) => setFile(event.target.files?.[0] || null)} />
        </label>
      )}
    </section>
  );
}

function SkillList({ title, skills, tone, emptyLabel }) {
  return (
    <div className="skill-group">
      <div className="skill-group-title"><span className={`status-dot ${tone}`} />{title}<span className="skill-count">{skills.length}</span></div>
      <div className="skill-tags">
        {skills.length ? skills.map((skill) => <span className={`skill-tag ${tone}`} key={skill}>{skill}</span>) : <span className="empty-skills">{emptyLabel}</span>}
      </div>
    </div>
  );
}

function ResumeAnnotations({ annotations = [] }) {
  const counts = annotations.reduce((summary, annotation) => {
    summary[annotation.label] = (summary[annotation.label] || 0) + 1;
    return summary;
  }, {});

  return (
    <section className="annotation-section">
      <div className="annotation-heading">
        <div><span className="eyebrow">Resume signal map</span><h2>What stands out</h2></div>
        <div className="annotation-legend"><span className="legend-item matched">Positive signal {counts.matched || 0}</span><span className="legend-item low-relevance">Low relevance {counts.low_relevance || 0}</span><span className="legend-item neutral">Context {counts.neutral || 0}</span></div>
      </div>
      <p className="annotation-intro">Green highlights support the target role. Red highlights may be worth shortening or reframing. Missing skills appear in the skill-gap list above.</p>
      <div className="annotated-resume">
        {annotations.length ? annotations.map((annotation, index) => (
          <span className={`annotation ${annotation.label}`} key={`${annotation.text}-${index}`} title={annotation.reason}>
            {annotation.text}{index < annotations.length - 1 ? " " : ""}
          </span>
        )) : <span className="empty-skills">No readable resume sections were found.</span>}
      </div>
    </section>
  );
}

function Results({ result, onReset }) {
  const score = result.match_score;
  const scoreTone = score >= 70 ? "high" : score >= 40 ? "medium" : "low";
  const required = result.job_required_skill_count;
  const found = result.matched_skills.length;
  const progress = required ? Math.round((found / required) * 100) : 0;

  return (
    <section className="results-section" aria-live="polite">
      <div className="results-header"><div><span className="eyebrow">Analysis complete</span><h2>Your match snapshot</h2></div><button className="text-button" onClick={onReset} type="button">Start over <span>↗</span></button></div>
      <div className="score-layout">
        <div className={`score-ring ${scoreTone}`} style={{ "--score": `${score * 3.6}deg` }}><div className="score-inner"><strong>{score}</strong><span>match score</span></div></div>
        <div className="score-copy"><span className={`score-label ${scoreTone}`}>{scoreTone === "high" ? "Strong alignment" : scoreTone === "medium" ? "Promising alignment" : "Room to grow"}</span><h3>{found} of {required} required skills found</h3><div className="progress-track"><div style={{ width: `${progress}%` }} /></div><p>Use the gaps below to sharpen your application for this role.</p></div>
      </div>
      <div className="skills-grid"><SkillList title="Matched skills" skills={result.matched_skills} tone="matched" emptyLabel="No direct matches found" /><SkillList title="Skill gaps" skills={result.missing_skills} tone="missing" emptyLabel="No gaps found" /></div>
      <ResumeAnnotations annotations={result.resume_annotations} />
      <p className="results-advice">We recommend reviewing and editing the highlighted sections to improve your chances of reaching your goal.</p>
    </section>
  );
}

function History({ entries, onSelect }) {
  if (!entries.length) return null;

  return (
    <section className="history-section">
      <div className="history-heading"><div><span className="eyebrow">Saved locally</span><h2>Recent analyses</h2></div><span className="history-count">{entries.length} saved</span></div>
      <div className="history-list">
        {entries.map((entry) => (
          <button className="history-item" key={entry.id} onClick={() => onSelect(entry)} type="button">
            <span className="history-date">{new Date(entry.timestamp).toLocaleDateString(undefined, { month: "short", day: "numeric" })}</span>
            <span className="history-skills">{entry.matched_skills.length} of {entry.job_required_skill_count} skills matched</span>
            <strong>{entry.match_score}%</strong><span className="history-arrow">↗</span>
          </button>
        ))}
      </div>
    </section>
  );
}

export default function App() {
  const [resumeText, setResumeText] = useState("");
  const [jobText, setJobText] = useState("");
  const [resumeFile, setResumeFile] = useState(null);
  const [jobFile, setJobFile] = useState(null);
  const [result, setResult] = useState(emptyResult);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    getHistory().then(setHistory).catch(() => setHistory([]));
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const nextResult = await analyzeMatch({ resumeText, jobText, resumeFile, jobFile });
      setResult(nextResult);
      setHistory((entries) => [{ ...nextResult, timestamp: new Date().toISOString() }, ...entries].slice(0, 25));
    } catch (submissionError) {
      setError(submissionError.message);
    } finally {
      setLoading(false);
    }
  }

  function reset() {
    setResult(null);
    setError("");
  }

  function selectHistory(entry) {
    setResult(entry);
    setError("");
  }

  return <main className="page-shell">
    <header className="site-header"><a className="brand" href="/">SM<span>/</span>RA</a><span className="header-note">Career intelligence / 01</span></header>
    <div className="content-wrap">
      <section className="intro"><span className="eyebrow">Resume intelligence</span><h1>Find the signal<br /><em>in your next move.</em></h1><p>Compare your experience to what the role actually asks for. Get a clear score, a grounded skills read, and your next best edits.</p></section>
      {!result ? <>
        <form onSubmit={handleSubmit}>
        <div className="input-grid"><InputPanel label="Resume" eyebrow="Your experience" text={resumeText} setText={setResumeText} file={resumeFile} setFile={setResumeFile} /><InputPanel label="Job Description" eyebrow="Target role" text={jobText} setText={setJobText} file={jobFile} setFile={setJobFile} /></div>
        {error && <div className="error-message" role="alert">{error}</div>}
        <div className="form-footer"><span>Private by design · files are analyzed locally through your API</span><button className="primary-button" disabled={loading} type="submit">{loading ? "Analyzing..." : "Analyze match"}<span>→</span></button></div>
        </form>
        <History entries={history} onSelect={selectHistory} />
      </> : <Results result={result} onReset={reset} />}
    </div>
    <footer><span>SMART RESUME ANALYZER</span><span>Built for better applications</span></footer>
  </main>;
}
