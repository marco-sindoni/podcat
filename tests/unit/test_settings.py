from podcat.settings import load_settings


def test_podcat_key_wins_over_anthropic_key(repo, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-generic")
    assert load_settings(repo).anthropic_api_key == "sk-generic"
    monkeypatch.setenv("PODCAT_ANTHROPIC_API_KEY", "sk-podcat")
    assert load_settings(repo).anthropic_api_key == "sk-podcat"
