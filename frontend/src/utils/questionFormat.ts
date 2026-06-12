import type { Question } from "../types";

export function isMultiSelectQuestion(question: Question): boolean {
  return question.question_type === "multi" || (question.select_count ?? 1) > 1;
}

export function formatChoiceLabel(letters: string): string {
  if (!letters) return "";
  return [...letters].join(", ");
}

export function parseChoiceLetters(value: string | null | undefined): Set<string> {
  const set = new Set<string>();
  if (!value) return set;
  for (const ch of value.toUpperCase()) {
    if ("ABCD".includes(ch)) set.add(ch);
  }
  return set;
}

export function serializeChoices(selected: Set<string>): string {
  return [...selected].sort().join("");
}
