"""Build study guide MCQs — delegates to study_guide_bank (150+ direct CISSP format)."""

from app.data.cheat_sheet.study_guide_bank import build_study_guide_questions

build_knowledge_questions = build_study_guide_questions

__all__ = ["build_knowledge_questions", "build_study_guide_questions"]
