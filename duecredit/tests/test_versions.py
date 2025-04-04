# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
from __future__ import annotations

from os import linesep

import pytest

from .._version import __version__
from ..versions import ExternalVersions, Version


# just to ease testing
def cmp(a, b):
    return (a > b) - (a < b)


def test_external_versions_basic():
    ev = ExternalVersions()
    assert ev._versions == {}
    assert ev["duecredit"] == Version(__version__)
    # and it could be compared
    assert ev["duecredit"] >= Version(__version__)
    assert ev["duecredit"] > Version("0.1")
    assert list(ev.keys()) == ["duecredit"]
    assert "duecredit" in ev
    assert "unknown" not in ev

    # Version might remove training .0
    version_str = (
        str(ev["duecredit"]) if isinstance(ev["duecredit"], Version) else __version__
    )
    assert ev.dumps() == f"Versions: duecredit={version_str}"

    # For non-existing one we get None
    assert ev["duecreditnonexisting"] is None

    # and nothing gets added to _versions for nonexisting
    assert set(ev._versions.keys()) == {"duecredit"}

    # but if it is a module without version, we get it set to UNKNOWN
    assert ev["os"] == ev.UNKNOWN
    # And get a record on that inside
    assert ev._versions.get("os") == ev.UNKNOWN
    # And that thing is "True", i.e. present
    assert ev["os"]
    # but not comparable with anything besides itself (was above)
    with pytest.raises(TypeError):
        cmp(ev["os"], "0")

    # assert_raises(TypeError, assert_greater, ev['os'], '0')

    # And we can get versions based on modules themselves
    from duecredit.tests import mod

    assert ev[mod] == Version(mod.__version__)

    # Check that we can get a copy of the versions
    versions_dict = ev.versions
    versions_dict["duecredit"] = "0.0.1"
    assert versions_dict["duecredit"] == "0.0.1"
    assert ev["duecredit"] == Version(__version__)


def test_external_versions_unknown() -> None:
    assert str(ExternalVersions.UNKNOWN) == "UNKNOWN"


def _test_external(ev, modname: str) -> None:
    try:
        exec(f"import {modname}", globals(), locals())
    except ImportError:
        modname = pytest.importorskip(modname)
    except Exception as e:
        pytest.skip(f"External {modname} fails to import: {e}")
    assert ev[modname] is not ev.UNKNOWN
    assert ev[modname] > Version("0.0.1")
    assert Version("1000000.0") > ev[modname]  # unlikely in our lifetimes


@pytest.mark.parametrize(
    "modname",
    [
        "scipy",
        "numpy",
        "mvpa2",
        "sklearn",
        "statsmodels",
        "pandas",
        "matplotlib",
        "psychopy",
    ],
)
def test_external_versions_popular_packages(modname: str) -> None:
    ev = ExternalVersions()

    _test_external(ev, modname)

    # more of a smoke test
    assert linesep not in ev.dumps()
    assert ev.dumps(indent=True).endswith(linesep)
