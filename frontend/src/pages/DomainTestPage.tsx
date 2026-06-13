import { useEffect, useState } from "react";
import { api } from "../api";
import { PageHeader } from "../components/ui/PageHeader";
import { IconTarget } from "../components/ui/Icons";
import type { DomainInfo } from "../types";

interface DomainTestPageProps {
  onStart: (domain: number, count: number) => void;
  onOpenHub: (domain: number) => void;
}

export function DomainTestPage({ onStart, onOpenHub }: DomainTestPageProps) {
  const [domains, setDomains] = useState<DomainInfo[]>([]);
  const [selected, setSelected] = useState<number | null>(null);
  const [count, setCount] = useState(20);

  useEffect(() => {
    api.domains().then(setDomains).catch(() => {});
  }, []);

  return (
    <div className="page-enter">
      <div className="card card-spotlight">
        <PageHeader
          eyebrow="8 ISC2 domains"
          title="Domain modules"
          subtitle="Each domain includes lessons, flashcards, practice quizzes, and mastery analytics."
        />
        <div className="form-group" style={{ maxWidth: 200 }}>
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

      <div className="domain-grid domain-grid--modern">
        {domains.map((d) => (
          <button
            key={d.id}
            type="button"
            className={`domain-card domain-card--selectable ${selected === d.id ? "selected" : ""}`}
            onClick={() => {
              setSelected(d.id);
              onOpenHub(d.id);
            }}
          >
            <span className="domain-card-num">D{d.id}</span>
            <h3>{d.name}</h3>
            <div className="weight">{(d.weight * 100).toFixed(0)}% exam weight</div>
          </button>
        ))}
      </div>

      {selected && (
        <div className="card domain-start-bar">
          <button type="button" className="btn btn-primary btn-lg btn-block" onClick={() => onStart(selected, count)}>
            <IconTarget size={18} />
            Start Domain {selected} — {count} questions
          </button>
        </div>
      )}
    </div>
  );
}
