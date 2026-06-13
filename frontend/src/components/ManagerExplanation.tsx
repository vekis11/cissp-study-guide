import { useEffect, useMemo, useState } from "react";
import { formatChoiceLabel } from "../utils/questionFormat";
import type { ExplanationSection } from "../types";

interface ManagerExplanationProps {
  isCorrect: boolean;
  correctChoice?: string;
  selectedChoice?: string | null;
  isMultiSelect?: boolean;
  managerBrief: string;
  explanationSections?: ExplanationSection[];
  referenceSections?: ExplanationSection[];
  trap?: string;
  approachTips?: string[];
  fallbackExplanation?: string;
  collapsible?: boolean;
  defaultExpanded?: boolean;
}

function parseBriefFallback(brief: string): ExplanationSection[] {
  if (!brief.trim()) return [];
  return brief.split(/\n\n+/).map((block, i) => {
    const nl = block.indexOf("\n");
    if (nl === -1) {
      return { key: `block-${i}`, title: "Explanation", body: block.trim() };
    }
    return {
      key: `block-${i}`,
      title: block.slice(0, nl).trim(),
      body: block.slice(nl + 1).trim(),
    };
  });
}

function sectionClass(key: string, isCorrect: boolean): string {
  if (key === "your_answer") {
    return isCorrect
      ? "explanation-block explanation-block--success"
      : "explanation-block explanation-block--your-pick";
  }
  if (key === "correct_answer") return "explanation-block explanation-block--answer";
  if (key === "distractors") return "explanation-block explanation-block--distractors";
  if (key === "domain" || key === "principle") return "explanation-block explanation-block--meta";
  if (key === "manager_lens") return "explanation-block explanation-block--lens";
  if (key === "watch_out") return "explanation-block explanation-block--watch-out";
  return "explanation-block";
}

function DistractorBody({ body }: { body: string }) {
  const blocks = body.split(/\n\n+/);
  return (
    <div className="distractor-briefs">
      {blocks.map((block) => {
        const nl = block.indexOf("\n");
        if (nl === -1) return <p key={block.slice(0, 8)} className="distractor-brief">{block}</p>;
        const letter = block.slice(0, nl).trim();
        const lines = block.slice(nl + 1).split("\n");
        return (
          <div key={letter} className="distractor-brief">
            <strong className="distractor-letter">{letter}</strong>
            {lines.map((line) => (
              <p key={line.slice(0, 20)} className="distractor-line">
                {line}
              </p>
            ))}
          </div>
        );
      })}
    </div>
  );
}

function SectionBlock({ section, isCorrect }: { section: ExplanationSection; isCorrect: boolean }) {
  return (
    <article className={sectionClass(section.key, isCorrect)}>
      <h4 className="explanation-block-title">{section.title}</h4>
      {section.key === "distractors" ? (
        <DistractorBody body={section.body} />
      ) : (
        <p className="explanation-block-body">{section.body}</p>
      )}
    </article>
  );
}

export function ManagerExplanation({
  isCorrect,
  correctChoice,
  selectedChoice,
  isMultiSelect = false,
  managerBrief,
  explanationSections,
  referenceSections,
  trap,
  fallbackExplanation,
  collapsible = false,
  defaultExpanded = false,
}: ManagerExplanationProps) {
  const brief = managerBrief || fallbackExplanation || "";
  const mainSections = useMemo(() => {
    if (explanationSections && explanationSections.length > 0) return explanationSections;
    return parseBriefFallback(brief);
  }, [brief, explanationSections]);

  const refSections = useMemo(() => referenceSections ?? [], [referenceSections]);

  const [expanded, setExpanded] = useState(defaultExpanded);
  const [referenceOpen, setReferenceOpen] = useState(false);

  useEffect(() => {
    setExpanded(defaultExpanded);
  }, [brief, correctChoice, isCorrect, defaultExpanded, mainSections.length]);

  if (mainSections.length === 0 && refSections.length === 0) return null;

  const body = (
    <div className={`manager-explanation ${isCorrect ? "correct-msg" : "incorrect-msg"}`}>
      <div className="manager-explanation-header">
        {isCorrect ? (
          <strong className="explanation-status explanation-status--ok">Correct</strong>
        ) : (
          <div className="explanation-status explanation-status--review">
            <strong>Not quite</strong>
            <span className="explanation-status-detail">
              Best answer{isMultiSelect ? "s" : ""}: {formatChoiceLabel(correctChoice ?? "")}
              {selectedChoice && selectedChoice !== correctChoice && (
                <> · You picked {formatChoiceLabel(selectedChoice)}</>
              )}
            </span>
          </div>
        )}
      </div>

      {mainSections.length > 0 && (
        <div className="explanation-blocks">
          {mainSections.map((section) => (
            <SectionBlock key={section.key} section={section} isCorrect={isCorrect} />
          ))}
        </div>
      )}

      {refSections.length > 0 && (
        <details
          className="explanation-reference"
          open={referenceOpen}
          onToggle={(e) => setReferenceOpen((e.target as HTMLDetailsElement).open)}
        >
          <summary>Reference</summary>
          <div className="explanation-blocks explanation-blocks--reference">
            {refSections.map((section) => (
              <SectionBlock key={section.key} section={section} isCorrect={isCorrect} />
            ))}
          </div>
        </details>
      )}

      {refSections.length === 0 && trap && (
        <p className="manager-trap-line">
          <strong>Easy mistake:</strong> {trap.replace(/^The trap:\s*/i, "")}
        </p>
      )}
    </div>
  );

  if (!collapsible) return body;

  return (
    <div className="manager-explanation-wrap">
      <button
        type="button"
        className={`explanation-toggle ${expanded ? "expanded" : ""}`}
        onClick={() => setExpanded((v) => !v)}
        aria-expanded={expanded}
      >
        <span>{expanded ? "Hide explanation" : "See explanation"}</span>
        <span className="explanation-toggle-icon" aria-hidden="true">
          {expanded ? "▲" : "▼"}
        </span>
      </button>
      {expanded && body}
    </div>
  );
}
