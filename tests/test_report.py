# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/nedbat/coveragepy/blob/master/NOTICE.txt

"""Tests for helpers in report.py"""

from __future__ import annotations

from typing import IO, Iterable, List, Optional

import pytest

from coverage.exceptions import CoverageException
from coverage.report import render_report
from coverage.types import TMorf

from tests.coveragetest import CoverageTest


class FakeReporter:
    """A fake implementation of a one-file reporter."""

    report_type = "fake report file"

    def __init__(self, output: str = "", error: bool = False) -> None:
        self.output = output
        self.error = error
        self.morfs: Optional[Iterable[TMorf]] = None

    def report(self, morfs: Optional[Iterable[TMorf]], outfile: IO[str]) -> float:
        """Fake."""
        self.morfs = morfs
        outfile.write(self.output)
        if self.error:
            raise CoverageException("You asked for it!")
        return 17.25


class RenderReportTest(CoverageTest):
    """Tests of render_report."""

    def test_stdout(self) -> None:
        fake = FakeReporter(output="Hello!\n")
        msgs: List[str] = []
        res = render_report("-", fake, [pytest, "coverage"], msgs.append)
        assert res == 17.25
        assert fake.morfs == [pytest, "coverage"]
        assert self.stdout() == "Hello!\n"
        assert not msgs

    def test_file(self) -> None:
        fake = FakeReporter(output="Gréètings!\n")
        msgs: List[str] = []
        res = render_report("output.txt", fake, [], msgs.append)
        assert res == 17.25
        assert self.stdout() == ""
        with open("output.txt", "rb") as f:
            assert f.read().rstrip() == b"Gr\xc3\xa9\xc3\xa8tings!"
        assert msgs == ["Wrote fake report file to output.txt"]

    def test_exception(self) -> None:
        fake = FakeReporter(error=True)
        msgs: List[str] = []
        with pytest.raises(CoverageException, match="You asked for it!"):
            render_report("output.txt", fake, [], msgs.append)
        assert self.stdout() == ""
        self.assert_doesnt_exist("output.txt")
        assert not msgs
