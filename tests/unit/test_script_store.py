from datetime import date

from podcat.scripts.models import Version
from podcat.scripts.store import ScriptStore
from podcat.tracking import frontmatter
from scriptfixtures import head_result


def _version(n=1):
    h = head_result()
    return Version(version=n, lines=h["lines"], scenes=h["scenes"], news_image=h["news_image"], endings=h["endings"])


def test_ids_versions_and_notes_kept(tmp_path):
    store = ScriptStore(tmp_path / "tracking")
    sid = store.new_id(date(2026, 11, 27), "daily", "2026-11-27-hacker-frigoriferi")
    assert sid == "2026-11-27-daily-hacker-frigoriferi"
    meta = {"id": sid, "story_id": "s", "kind": "daily", "date": "2026-11-27", "status": "draft", "versions": []}
    meta = store.add_version(meta, _version(1), "corpo", "write", 0.04, "riassunto")
    path = store.index_path(sid)
    path.write_text(path.read_text() + "\nNota di Marco.\n")
    meta = store.add_version(meta, _version(2), "corpo 2", "revise", 0.02, "riassunto 2")
    assert meta["current_version"] == 2 and meta["cost_usd"] == 0.06
    assert [v["cause"] for v in meta["versions"]] == ["write", "revise"]
    assert "Nota di Marco." in path.read_text()
    assert store.read_version(sid).version == 2
    assert store.read_version(sid, 1).version == 1
    assert store.new_id(date(2026, 11, 27), "daily", "2026-11-27-hacker-frigoriferi").endswith("-2")


def test_find_and_recent_skip_discarded(tmp_path):
    store = ScriptStore(tmp_path / "tracking")
    for i, status in enumerate(["approved", "discarded", "review"]):
        meta = {"id": f"s{i}", "story_id": f"st{i}", "kind": "daily", "date": f"2026-11-2{i}", "status": status,
                "versions": [{"created_at": f"2026-11-2{i}T08:00"}], "current_version": 1}
        frontmatter.write(store.index_path(f"s{i}"), frontmatter.Document(meta=meta))
    assert store.find("st1", "daily") is None
    assert store.find("st2", "daily")["id"] == "s2"
    assert [m["id"] for m in store.recent()] == ["s2", "s0"]
    assert [m["id"] for m in store.recent(before={"date": "2026-11-22", "versions": [{"created_at": "2026-11-22T07:00"}]})] == ["s0"]
