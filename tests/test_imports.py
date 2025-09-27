"""
Basic tests for an application.

This ensures all modules are importable and that the config is valid.
"""

def test_import_app():
    from sia_local_control_ui.application import SiaLocalControlUiApplication
    assert SiaLocalControlUiApplication

def test_config():
    from sia_local_control_ui.app_config import SiaLocalControlUiConfig

    config = SiaLocalControlUiConfig()
    assert isinstance(config.to_dict(), dict)

def test_ui():
    from sia_local_control_ui.app_ui import SiaLocalControlUiUI
    assert SiaLocalControlUiUI

def test_state():
    from sia_local_control_ui.app_state import SiaLocalControlUiState
    assert SiaLocalControlUiState