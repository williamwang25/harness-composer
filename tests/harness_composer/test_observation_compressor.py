from minisweagent.harness_composer.runtime.observation_compressor import compress_output


def test_compresses_long_pytest_output_preserving_failure_markers():
    text = "\n".join(
        [
            "line before",
            *[f"noise {i}" for i in range(1000)],
            "=================================== FAILURES ===================================",
            "E   AssertionError: expected 1",
            "FAILED tests/test_demo.py::test_demo - AssertionError",
            "short test summary info",
        ]
    )

    compressed, stats = compress_output(text, strategy="traceback_assertion_only", max_chars=1200)

    assert stats.compressed
    assert stats.original_chars > stats.compressed_chars
    assert "AssertionError" in compressed
    assert "short test summary info" in compressed
