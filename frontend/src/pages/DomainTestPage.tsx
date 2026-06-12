import { useEffect, useState } from "react";
import { api } from "../api";
import type { DomainInfo } from "../types";

interface DomainTestPageProps {
  onStart: (domain: number, count: number) => void;
}

export function DomainTestPage({ onStart }: DomainTestPageProps) {
  const [domains, setDomains] = useState<DomainInfo[]>([]);
  const [selected, setSelected] = useState<number | null>(null);
  const [count, setCount] = useState(20);

  useEffect(() => {
    api.domains().then(setDomains).catch(() => {});
  }, []);

  return (
    <>
      <div className="card">
        <h2>Domain Mastery Test</h2>
        <p className="sub">Focus on one of the 8 CISSP domains. Choose a domain and question count.</p>
        <div className="form-group">
          <label htmlFor="domain-count">Questions per session</label>
          <input
            id="domain-count"
            type="number"
            min={5}
            max={50}
            value={count}
            onChange={(e) => setCount(Number(e.target.value))}
          />
        </div>
      </div>

      <div className="domain-grid">
        {domains.map((d) => (
          <div
            key={d.id}
            className="domain-card"
            style={{ borderColor: selected === d.id ? "var(--accent)" : undefined }}
            onClick={() => setSelected(d.id)}
            onKeyDown={(e) => e.key === "Enter" && setSelected(d.id)}
            role="button"
            tabIndex={0}
          >
            <h3>Domain {d.id}: {d.name}</h3>
            <div className="weight">Exam weight: {(d.weight * 100).toFixed(0)}%</div>
          </div>
        ))}
      </div>

      {selected && (
        <div className="card" style={{ marginTop: "1rem" }}>
          <button type="button" className="btn btn-primary" onClick={() => onStart(selected, count)}>
            Start Domain {selected} Test ({count} questions)
          </button>
        </div>
      )}
    </>
  );
}
