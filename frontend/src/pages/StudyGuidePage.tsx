import { useEffect, useMemo, useState } from "react";
import { api } from "../api";
import { PageHeader } from "../components/ui/PageHeader";
import { ProgressRing } from "../components/ui/ProgressRing";
import { IconBook, IconSpark } from "../components/ui/Icons";
import type { GuideQuizTier, ImportanceTier, StudyGuideData, TopicCoverage } from "../types";

interface StudyGuidePageProps {
  onStartGuideQuiz: (importance: ImportanceTier, domain?: number, questionCount?: number) => void;
  onStartTopicDrill?: (topicId: string) => void;
  onOpenFlashcards?: (domain: number, topicId: string) => void;
  initialDomainFilter?: number;
}

const TIER_META: Record<
  ImportanceTier,
  { marker: string; label: string; variant: string; order: number }
> = {
  must: { marker: "🔴", label: "Must Know", variant: "must", order: 1 },
  high: { marker: "🟡", label: "High Value", variant: "high", order: 2 },
  good: { marker: "🟢", label: "Good to Reinforce", variant: "good", order: 3 },
};

function tierProgressLabel(tier: GuideQuizTier) {
  const answered = tier.answered_count ?? 0;
  const total = tier.question_count;
  const remaining = tier.remaining_count ?? Math.max(0, total - answered);
  return `${answered}/${total} answered · ${remaining} left`;
}

function TierQuizButton({
  tier,
  domainLabel,
  onStart,
}: {
  tier: GuideQuizTier;
  domainLabel?: string;
  onStart: () => void;
}) {
  const meta = TIER_META[tier.importance as ImportanceTier] ?? TIER_META.high;
  if (tier.question_count === 0) return null;
  const progressPct = tier.question_count
    ? Math.round(((tier.answered_count ?? 0) / tier.question_count) * 100)
    : 0;

  return (
    <button
      type="button"
      className={`guide-tier-btn guide-tier-btn--${meta.variant}`}
      onClick={onStart}
      title={tier.study_hint}
    >
      <span className="guide-tier-btn-marker">{meta.marker}</span>
      <span className="guide-tier-btn-copy">
        <span className="guide-tier-btn-label">{meta.label}</span>
        <span className="guide-tier-btn-meta">
          {tier.question_count} question{tier.question_count !== 1 ? "s" : ""}
          {domainLabel ? ` · ${domainLabel}` : " · all domains"}
        </span>
        <span className="guide-tier-btn-progress">
          <span className="guide-tier-progress-bar" aria-hidden>
            <span className="guide-tier-progress-fill" style={{ width: `${progressPct}%` }} />
          </span>
          {tierProgressLabel(tier)}
        </span>
      </span>
      <span className="guide-tier-btn-go">Start →</span>
    </button>
  );
}

export function StudyGuidePage({
  onStartGuideQuiz,
  onStartTopicDrill,
  onOpenFlashcards,
  initialDomainFilter,
}: StudyGuidePageProps) {
  const [data, setData] = useState<StudyGuideData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [domainFilter, setDomainFilter] = useState<number | "all">(initialDomainFilter ?? "all");
  const [openDomain, setOpenDomain] = useState<number | null>(null);
  const [showReference, setShowReference] = useState(false);

  useEffect(() => {
    api.studyGuide().then(setData).catch((e) => setError(e instanceof Error ? e.message : "Failed to load"));
  }, []);

  const coverageByTopic = useMemo(() => {
    const map = new Map<string, TopicCoverage>();
    data?.coverage.forEach((c) => map.set(c.topic_id, c));
    return map;
  }, [data]);

  if (error) {
    return <div className="card error-msg">{error}</div>;
  }

  if (!data) {
    return <div className="loading">Loading study guide...</div>;
  }

  const { catalog, summary, quiz_groups } = data;
  const visibleDomains = quiz_groups.by_domain.filter(
    (d) => domainFilter === "all" || d.domain === domainFilter
  );

  return (
    <div className="study-guide-page page-enter">
      <section className="card card-spotlight study-guide-hero">
        <div className="study-guide-hero-row">
          <div>
            <PageHeader
              eyebrow="Exam-focused study path"
              title="CISSP Study Guide"
              subtitle="Knowledge-check quizzes weighted toward direct CBK recall, with one manager scenario per topic — grouped by Must Know, High Value, and Good to Reinforce."
            />
          </div>
          <div className="study-guide-hero-ring">
            <ProgressRing
              value={summary.fully_tested}
              max={summary.total_topics}
              label="Topics covered"
              sublabel={`${summary.fully_tested}/${summary.total_topics}`}
              size={112}
            />
          </div>
        </div>
      </section>

      <section className="card guide-path-card">
        <div className="guide-path-header">
          <IconSpark size={20} />
          <div>
            <h2>Recommended exam path</h2>
            <p className="sub">
              Run these in order across the full exam — same priority as the cheat sheet: red first, then yellow,
              then green. Progress shows how many tier questions you have answered vs remaining.
            </p>
          </div>
        </div>
        <div className="guide-exam-path">
          {quiz_groups.exam_path.map((tier) => (
            <TierQuizButton
              key={tier.importance}
              tier={tier}
              onStart={() => onStartGuideQuiz(tier.importance as ImportanceTier, undefined, tier.question_count)}
            />
          ))}
        </div>
      </section>

      <section className="card">
        <h2>Domain quizzes by priority</h2>
        <p className="sub">
          Each button runs a <strong>knowledge-check weighted</strong> set for every topic in that tier (
          {summary.knowledge_per_topic ?? 1} knowledge + {summary.scenarios_per_topic ?? 1} scenario per topic).
          Domain 1 (16% weight) is your highest-yield starting point.
        </p>
        <div className="domain-filter-row">
          <button
            type="button"
            className={`btn btn-sm ${domainFilter === "all" ? "btn-primary" : "btn-secondary"}`}
            onClick={() => setDomainFilter("all")}
          >
            All domains
          </button>
          {catalog.domain_weights.map((d) => (
            <button
              key={d.domain}
              type="button"
              className={`btn btn-sm ${domainFilter === d.domain ? "btn-primary" : "btn-secondary"}`}
              onClick={() => setDomainFilter(d.domain)}
            >
              D{d.domain} ({d.weight_percent}%)
            </button>
          ))}
        </div>
      </section>

      {visibleDomains.map((domainGroup) => (
        <section key={domainGroup.domain} className="card guide-domain-quiz-card">
          <div className="guide-domain-quiz-head">
            <div>
              <span className="guide-domain-num">Domain {domainGroup.domain}</span>
              <h2>{domainGroup.domain_name}</h2>
              <p className="sub">{domainGroup.weight_percent}% of the exam</p>
            </div>
          </div>

          <div className="guide-domain-tiers">
            {domainGroup.tiers.map((tier) => (
              <TierQuizButton
                key={tier.importance}
                tier={tier}
                domainLabel={`D${domainGroup.domain}`}
                onStart={() =>
                  onStartGuideQuiz(
                    tier.importance as ImportanceTier,
                    domainGroup.domain,
                    tier.question_count
                  )
                }
              />
            ))}
          </div>

          <details className="guide-tier-topics">
            <summary>What&apos;s in each tier ({domainGroup.tiers.reduce((n, t) => n + t.topic_count, 0)} topics)</summary>
            {domainGroup.tiers.map((tier) => {
              const meta = TIER_META[tier.importance as ImportanceTier];
              return (
                <div key={tier.importance} className="guide-tier-topic-block">
                  <h4>
                    {meta.marker} {meta.label}{" "}
                    <span className="guide-tier-topic-progress">({tierProgressLabel(tier)})</span>
                  </h4>
                  <ul>
                    {(tier.topic_titles ?? []).map((title) => (
                      <li key={title}>{title}</li>
                    ))}
                  </ul>
                </div>
              );
            })}
          </details>
        </section>
      ))}

      <section className="card">
        <button
          type="button"
          className="guide-reference-toggle"
          onClick={() => setShowReference((v) => !v)}
          aria-expanded={showReference}
        >
          <span>
            <IconBook size={18} />
            {showReference ? "Hide" : "Show"} full reference notes
          </span>
          <span aria-hidden>{showReference ? "▲" : "▼"}</span>
        </button>

        {showReference && (
          <div className="guide-reference-body">
            <p className="sub">{catalog.how_to_use}</p>
            <ul className="importance-legend">
              {catalog.importance_legend.map((item) => (
                <li key={item.marker}>
                  <strong>
                    {TIER_META[item.marker as ImportanceTier]?.marker ?? "•"} {item.label}
                  </strong>
                  — {item.description}
                </li>
              ))}
            </ul>

            {catalog.domains
              .filter((d) => domainFilter === "all" || d.domain === domainFilter)
              .map((domain) => {
                const tiers = (["must", "high", "good"] as ImportanceTier[]).map((imp) => ({
                  imp,
                  sections: domain.sections.filter((s) => s.importance === imp),
                }));

                return (
                  <div key={domain.domain} className="guide-ref-domain">
                    <button
                      type="button"
                      className="guide-ref-domain-head"
                      onClick={() => setOpenDomain(openDomain === domain.domain ? null : domain.domain)}
                    >
                      <span>
                        Domain {domain.domain}: {domain.name}
                      </span>
                      <span aria-hidden>{openDomain === domain.domain ? "▲" : "▼"}</span>
                    </button>

                    {openDomain === domain.domain &&
                      tiers.map(({ imp, sections }) =>
                        sections.length === 0 ? null : (
                          <div key={imp} className="guide-ref-tier">
                            <h3>
                              {TIER_META[imp].marker} {TIER_META[imp].label}
                            </h3>
                            {sections.map((section) => {
                              const cov = coverageByTopic.get(section.topic_id);
                              return (
                                <div key={section.topic_id} className="study-topic study-topic--compact">
                                  <div className="study-topic-header-static">
                                    <span>{section.title}</span>
                                    {cov?.fully_tested && (
                                      <span className="coverage-ok">✓ quiz linked</span>
                                    )}
                                  </div>
                                  <p className="study-ref-content">{section.content}</p>
                                  <div className="topic-action-row">
                                    {onStartTopicDrill && (
                                      <button
                                        type="button"
                                        className="btn btn-secondary btn-sm"
                                        onClick={() => onStartTopicDrill(section.topic_id)}
                                      >
                                        Mini-quiz
                                      </button>
                                    )}
                                    {onOpenFlashcards && (
                                      <button
                                        type="button"
                                        className="btn btn-secondary btn-sm"
                                        onClick={() => onOpenFlashcards(domain.domain, section.topic_id)}
                                      >
                                        Flashcard
                                      </button>
                                    )}
                                  </div>
                                  {section.scenarios?.map((sc) => (
                                    <div key={sc.prompt} className="scenario-box">
                                      <strong>Scenario:</strong> {sc.prompt}
                                      <div className="scenario-answer">
                                        <strong>Answer:</strong> {sc.answer}
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              );
                            })}
                          </div>
                        )
                      )}
                  </div>
                );
              })}
          </div>
        )}
      </section>

      <div className="card mindset-card">
        <div className="mindset-header">
          <IconBook size={20} />
          <h2>Manager mindset</h2>
        </div>
        <p>{catalog.manager_mindset}</p>
        {catalog.final_reminders && (
          <ul>
            {catalog.final_reminders.map((r) => (
              <li key={r}>{r}</li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
