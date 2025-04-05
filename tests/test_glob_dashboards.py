import json
from pathlib import Path


def create_dashboard_files(base_path: Path, count: int = 3) -> list[Path]:
    dashboards_dir = base_path / "dashboards"
    dashboards_dir.mkdir(parents=True, exist_ok=True)

    files = []
    for i in range(count):
        dashboard_data = {"uid": f"uid-{i}", "title": f"Team Dashboard {i}"}
        file_path = dashboards_dir / f"db{i}.json"
        file_path.write_text(json.dumps(dashboard_data), encoding="utf-8")
        files.append(file_path)
    return files


def test_globbed_dashboard_files_created(tmp_path):
    dashboard_files = create_dashboard_files(tmp_path)

    assert len(dashboard_files) == 3
    for i, f in enumerate(dashboard_files):
        assert f.exists()
        data = json.loads(f.read_text())
        assert data["uid"] == f"uid-{i}"
        assert data["title"] == f"Team Dashboard {i}"
