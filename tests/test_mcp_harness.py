import asyncio

from portfolio_lab.evaluate import scenarios
from portfolio_lab.mcp_probe import probe


def test_mcp_sdk_round_trip_over_stdio():
    result = asyncio.run(probe())
    assert result["status"] == "passed" and result["invalid_tenant_rejected"]


def test_harness_acceptance_criteria_pass():
    report = scenarios()
    assert report["passed"] == report["total"] and report["total"] > 0
    assert not report["llm_executed"] and not report["production_validated"]
