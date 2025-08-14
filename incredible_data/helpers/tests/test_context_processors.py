from incredible_data.helpers.context_processors import ProjectInfo


class DummySettings:
    VERSION = "1.2.3"
    BUILD_NUMBER = "456"


def test_project_info_from_settings(monkeypatch):
    monkeypatch.setattr("django.conf.settings.VERSION", DummySettings.VERSION)
    monkeypatch.setattr("django.conf.settings.BUILD_NUMBER", DummySettings.BUILD_NUMBER)
    info = ProjectInfo.from_settings()
    assert info.version == DummySettings.VERSION
    assert info.commit_hash == DummySettings.BUILD_NUMBER
    assert info.full_version == f"{DummySettings.VERSION}+{DummySettings.BUILD_NUMBER}"
