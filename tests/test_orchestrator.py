import pytest
from core.orchestrator import Orchestrator
from unittest.mock import MagicMock

def test_orchestrator_sequential_flow(mocker):
    # Mock repositories and engines
    mock_repo = MagicMock()
    mock_attack = MagicMock()
    mock_defense = MagicMock()
    
    # Mocking the initialization of Orchestrator components
    mocker.patch('core.orchestrator.Repository', return_value=mock_repo)
    mocker.patch('core.orchestrator.AttackEngine', return_value=mock_attack)
    mocker.patch('core.orchestrator.DefenseEngine', return_value=mock_defense)
    
    # Setup mock returns
    mock_testbed = MagicMock(id=1)
    mock_session = MagicMock(id=101)
    mock_repo.get_latest_testbed.return_value = mock_testbed
    mock_repo.create_session.return_value = mock_session
    mock_attack.run_script.return_value = ("Attack Output", 0)
    mock_defense.run_script.return_value = ("Defense Findings", 0)
    
    orch = Orchestrator()
    orch.run_sequential_cycle("nmap", "127.0.0.1", "", "suricata")
    
    # Verify sequence: Attack called, then Defense
    mock_attack.run_script.assert_called_once_with("nmap", "127.0.0.1", "")
    mock_defense.run_script.assert_called_once_with("suricata", 101)
    
    # Verify data commit
    assert mock_repo.log_attack.called
    assert mock_repo.log_defense.called
