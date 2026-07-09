from fastapi.testclient import TestClient
from app.main import app


def test_healthz():
    client = TestClient(app)
    res = client.get('/healthz')
    assert res.status_code == 200
    assert res.json()['status'] == 'ok'


def test_create_video_job_validation():
    client = TestClient(app)
    res = client.post('/v1/video-jobs', json={'url': 'not-a-url', 'goal': 'x'})
    assert res.status_code == 422
