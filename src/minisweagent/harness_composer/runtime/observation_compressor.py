from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CompressionStats:
    compressed: bool
    original_chars: int
    compressed_chars: int
    strategy: str


_ERROR_MARKERS = (
    "Traceback (most recent call last)",
    "AssertionError",
    "FAILED",
    "ERROR",
    "FAILURES",
    "short test summary info",
    "E   ",
    "error:",
    "panic:",
)


def compress_output(
    text: str,
    *,
    strategy: str = "tail_and_error_blocks",
    max_chars: int = 6000,
    head_chars: int = 1800,
    tail_chars: int = 3000,
) -> tuple[str, CompressionStats]:
    """Compress long command output while preserving failure-heavy regions."""
    original_chars = len(text)
    if original_chars <= max_chars:
        return text, CompressionStats(False, original_chars, original_chars, strategy)

    if strategy == "traceback_assertion_only":
        compressed = _pytest_failure_summary(text, max_chars=max_chars)
    else:
        compressed = _generic_summary(text, max_chars=max_chars, head_chars=head_chars, tail_chars=tail_chars)

    header = (
        "[Harness Composer compressed observation: "
        f"strategy={strategy}, original_chars={original_chars}, kept_chars={len(compressed)}]\n"
    )
    result = header + compressed
    return result, CompressionStats(True, original_chars, len(result), strategy)


def _generic_summary(text: str, *, max_chars: int, head_chars: int, tail_chars: int) -> str:
    head = text[:head_chars].rstrip()
    tail = text[-tail_chars:].lstrip()
    error_blocks = _collect_marker_windows(text.splitlines(), marker_window=3)
    parts = [head]
    if error_blocks:
        parts.extend(["\n[error blocks]\n", error_blocks])
    parts.extend(["\n[tail]\n", tail])
    summary = "\n".join(part for part in parts if part)
    return _fit(summary, max_chars)


def _pytest_failure_summary(text: str, *, max_chars: int) -> str:
    lines = text.splitlines()
    blocks = _collect_marker_windows(lines, marker_window=6)
    summary_lines = _summary_lines(lines)
    tail = "\n".join(lines[-80:])
    parts = []
    if blocks:
        parts.extend(["[failure blocks]", blocks])
    if summary_lines:
        parts.extend(["[summary]", "\n".join(summary_lines)])
    parts.extend(["[tail]", tail])
    return _fit("\n".join(part for part in parts if part), max_chars)


def _collect_marker_windows(lines: list[str], *, marker_window: int) -> str:
    selected: list[str] = []
    seen: set[int] = set()
    for index, line in enumerate(lines):
        if any(marker in line for marker in _ERROR_MARKERS):
            start = max(0, index - marker_window)
            end = min(len(lines), index + marker_window + 1)
            for line_index in range(start, end):
                if line_index not in seen:
                    selected.append(f"{line_index + 1}: {lines[line_index]}")
                    seen.add(line_index)
            selected.append("---")
    return "\n".join(selected).strip("-\n")


def _summary_lines(lines: list[str]) -> list[str]:
    interesting = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(("FAILED ", "ERROR ", "XFAIL ", "XPASS ")) or " failed" in stripped or " passed" in stripped:
            interesting.append(line)
    return interesting[-40:]


def _fit(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    head = text[: max_chars // 2].rstrip()
    tail = text[-(max_chars // 2) :].lstrip()
    return f"{head}\n[...compressed middle...]\n{tail}"
