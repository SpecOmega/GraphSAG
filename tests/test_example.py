import asyncio

from examples.secure_transfer_agent import run_demo


def test_secure_transfer_example_authorizes_only_bound_execution():
    result = asyncio.run(run_demo())

    assert result["principal_id"] == "agent:payments"
    assert result["decision"] == "ALLOW"
    assert result["audit_chain_valid"] is True
    assert result["execution"] == "authorized"
    assert result["provenance_nodes"] == 4
