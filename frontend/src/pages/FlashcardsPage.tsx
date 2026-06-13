import { useEffect, useState } from "react";
import { api } from "../api";
import { PageHeader } from "../components/ui/PageHeader";
import type { Flashcard } from "../types";

interface FlashcardsPageProps {
  domain?: number;
  topicId?: string;
  onBack: () => void;
}

export function FlashcardsPage({ domain, topicId, onBack }: FlashcardsPageProps) {
  const [cards, setCards] = useState<Flashcard[]>([]);
  const [index, setIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .flashcards({ domain, topic_id: topicId })
      .then((c) => {
        setCards(c);
        setIndex(0);
        setFlipped(false);
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load flashcards"));
  }, [domain, topicId]);

  if (error) return <div className="error-msg">{error}</div>;
  if (cards.length === 0) return <div className="loading">Loading flashcards…</div>;

  const card = cards[index];

  return (
    <div className="page-enter">
      <button type="button" className="btn btn-secondary btn-sm" style={{ marginBottom: "1rem" }} onClick={onBack}>
        ← Back
      </button>

      <PageHeader
        eyebrow={card.domain_name}
        title="Flashcards"
        subtitle={`${index + 1} of ${cards.length} · tap card to flip`}
      />

      <button
        type="button"
        className={`flashcard ${flipped ? "flashcard--flipped" : ""}`}
        onClick={() => setFlipped((f) => !f)}
      >
        <div className="flashcard-inner">
          <div className="flashcard-face flashcard-front">
            <span className="tag">{card.importance}</span>
            <p>{card.front}</p>
          </div>
          <div className="flashcard-face flashcard-back">
            <p>{card.back}</p>
          </div>
        </div>
      </button>

      <div className="flashcard-nav">
        <button
          type="button"
          className="btn btn-secondary"
          disabled={index === 0}
          onClick={() => {
            setIndex((i) => i - 1);
            setFlipped(false);
          }}
        >
          Previous
        </button>
        <button
          type="button"
          className="btn btn-primary"
          disabled={index >= cards.length - 1}
          onClick={() => {
            setIndex((i) => i + 1);
            setFlipped(false);
          }}
        >
          Next
        </button>
      </div>
    </div>
  );
}
