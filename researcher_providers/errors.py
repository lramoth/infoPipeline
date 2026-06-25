"""Shared Researcher-stage exceptions."""

from __future__ import annotations

from diagnostics import DiagnosticError


class ResearcherError(DiagnosticError):
    """Raised when configured research cannot produce usable output."""
