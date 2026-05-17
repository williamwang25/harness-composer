from __future__ import annotations

import os
from collections import Counter
from pathlib import Path

from minisweagent.harness_composer.profiler.schema import RepoTaskProfile, RepoScale, TaskType, VerificationType

_IGNORED_DIRS = {
    ".git",
    ".hg",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "site-packages",
    "venv",
}

_LANGUAGE_EXTENSIONS = {
    ".py": "python",
    ".pyi": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".kt": "kotlin",
    ".kts": "kotlin",
    ".rb": "ruby",
    ".php": "php",
    ".c": "c",
    ".cc": "cpp",
    ".cpp": "cpp",
    ".h": "c",
    ".hpp": "cpp",
}


class RepoTaskProfiler:
    """Deterministic repo/task profiler for the Harness Composer router."""

    def __init__(self, *, max_files: int = 20000):
        self.max_files = max_files

    def profile(self, repo_path: str | Path, task: str = "") -> RepoTaskProfile:
        root = Path(repo_path).resolve()
        files = self._iter_files(root)
        rel_files = [self._safe_relative(file, root) for file in files]
        manifests = {name for name in self._candidate_names(rel_files)}
        extension_counts = Counter(file.suffix.lower() for file in rel_files)
        language_counts: Counter[str] = Counter()
        for suffix, count in extension_counts.items():
            if language := _LANGUAGE_EXTENSIONS.get(suffix):
                language_counts[language] += count
        language = self._primary_language(language_counts, manifests)
        build_system = self._detect_build_system(manifests)
        test_framework = self._detect_test_framework(rel_files, manifests, language)
        likely_test_command = self._likely_test_command(language, build_system, test_framework, manifests)
        task_type = self._detect_task_type(task)
        verification_type = self._detect_verification_type(task, test_framework)
        repo_scale = self._repo_scale(len(rel_files))
        context_risk = self._context_risk(rel_files, manifests, repo_scale)

        return RepoTaskProfile(
            repo_path=str(root),
            task_preview=task.strip()[:240],
            language=language,
            languages=list(language_counts.keys()),
            build_system=build_system,
            test_framework=test_framework,
            repo_scale=repo_scale,
            task_type=task_type,
            verification_type=verification_type,
            likely_test_command=likely_test_command,
            context_risk=context_risk,
            evidence={
                "file_count": len(rel_files),
                "extension_counts": dict(extension_counts.most_common(20)),
                "language_counts": dict(language_counts.most_common()),
                "manifests": sorted(manifests),
                "test_file_count": self._count_test_files(rel_files),
            },
        )

    def _iter_files(self, root: Path) -> list[Path]:
        files: list[Path] = []
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [name for name in dirnames if name not in _IGNORED_DIRS]
            for filename in filenames:
                files.append(Path(dirpath) / filename)
                if len(files) >= self.max_files:
                    return files
        return files

    @staticmethod
    def _safe_relative(path: Path, root: Path) -> Path:
        try:
            return path.relative_to(root)
        except ValueError:
            return path

    @staticmethod
    def _candidate_names(files: list[Path]) -> list[str]:
        return [file.name for file in files] + [str(file).replace("\\", "/") for file in files]

    @staticmethod
    def _primary_language(language_counts: Counter[str], manifests: set[str]) -> str:
        if "package.json" in manifests:
            if language_counts.get("typescript", 0) >= language_counts.get("javascript", 0):
                return "typescript" if language_counts.get("typescript", 0) else "javascript"
            return "javascript"
        manifest_language = {
            "pyproject.toml": "python",
            "setup.py": "python",
            "setup.cfg": "python",
            "go.mod": "go",
            "Cargo.toml": "rust",
            "pom.xml": "java",
            "build.gradle": "java",
            "Gemfile": "ruby",
        }
        for manifest, language in manifest_language.items():
            if manifest in manifests:
                return language
        return language_counts.most_common(1)[0][0] if language_counts else "unknown"

    @staticmethod
    def _detect_build_system(manifests: set[str]) -> str:
        checks = [
            ("pyproject.toml", "pyproject"),
            ("setup.py", "setup.py"),
            ("setup.cfg", "setup.cfg"),
            ("package.json", "package.json"),
            ("go.mod", "go.mod"),
            ("Cargo.toml", "cargo"),
            ("pom.xml", "maven"),
            ("build.gradle", "gradle"),
            ("Makefile", "make"),
        ]
        for filename, build_system in checks:
            if filename in manifests:
                return build_system
        return "unknown"

    @staticmethod
    def _detect_test_framework(files: list[Path], manifests: set[str], language: str) -> str:
        normalized = {str(file).replace("\\", "/") for file in files}
        names = {file.name for file in files}
        if language == "python":
            if {"pytest.ini", "tox.ini", "conftest.py"} & names or any(
                part.startswith("tests/test_") or part.endswith("_test.py") for part in normalized
            ):
                return "pytest"
            if any(part.endswith("_test.py") for part in normalized):
                return "pytest"
            if any(part.startswith("test") and part.endswith(".py") for part in names):
                return "unittest"
        if language in {"javascript", "typescript"}:
            if "package.json" in manifests:
                if any("jest" in part.lower() for part in normalized):
                    return "jest"
                return "npm"
        if language == "go" and any(part.endswith("_test.go") for part in normalized):
            return "go test"
        if language == "rust" and "Cargo.toml" in manifests:
            return "cargo test"
        return "unknown"

    @staticmethod
    def _likely_test_command(language: str, build_system: str, test_framework: str, manifests: set[str]) -> str:
        if test_framework == "pytest":
            return "pytest -q"
        if test_framework == "unittest":
            return "python -m unittest"
        if language in {"javascript", "typescript"} and "package.json" in manifests:
            return "npm test"
        if language == "go":
            return "go test ./..."
        if language == "rust":
            return "cargo test"
        if build_system == "make":
            return "make test"
        return ""

    @staticmethod
    def _detect_task_type(task: str) -> TaskType:
        lowered = task.lower()
        if any(word in lowered for word in ["run command", "terminal", "shell", "command line", "execute"]):
            return "terminal_task"
        if any(word in lowered for word in ["doc", "readme", "documentation"]):
            return "docs"
        if any(word in lowered for word in ["test", "coverage", "regression"]):
            return "test_update"
        if any(word in lowered for word in ["add", "implement", "feature", "support"]):
            return "feature"
        if any(word in lowered for word in ["bug", "fix", "error", "fail", "issue", "traceback", "exception"]):
            return "bug_fix"
        return "unknown"

    @staticmethod
    def _detect_verification_type(task: str, test_framework: str) -> VerificationType:
        lowered = task.lower()
        if any(word in lowered for word in ["lint", "ruff", "flake8", "mypy", "eslint"]):
            return "lint"
        if any(word in lowered for word in ["integration", "e2e", "end-to-end"]):
            return "integration_test"
        if test_framework != "unknown" or any(word in lowered for word in ["test", "pytest", "unit"]):
            return "unit_test"
        if "manual" in lowered:
            return "manual"
        return "unknown"

    @staticmethod
    def _repo_scale(file_count: int) -> RepoScale:
        if file_count < 50:
            return "tiny"
        if file_count < 300:
            return "small"
        if file_count < 2500:
            return "medium"
        return "large"

    @staticmethod
    def _context_risk(files: list[Path], manifests: set[str], repo_scale: RepoScale) -> list[str]:
        risks: list[str] = []
        normalized = [str(file).replace("\\", "/").lower() for file in files]
        if repo_scale in {"medium", "large"}:
            risks.append("large_repo")
        if any(name.endswith((".ipynb", ".csv", ".jsonl", ".parquet", ".sqlite", ".db")) for name in normalized):
            risks.append("data_or_notebook_files")
        if any(name.endswith((".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".tar.gz")) for name in normalized):
            risks.append("binary_or_archive_files")
        if {"tox.ini", "noxfile.py", "docker-compose.yml"} & manifests:
            risks.append("custom_test_environment")
        if any("generated" in name or name.endswith(".min.js") for name in normalized):
            risks.append("generated_files")
        return risks

    @staticmethod
    def _count_test_files(files: list[Path]) -> int:
        return sum(1 for file in files if file.name.startswith("test_") or file.name.endswith("_test.py"))
