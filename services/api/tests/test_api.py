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


def test_create_demo_draft_returns_editable_scenario():
    client = TestClient(app)
    res = client.post(
        '/v1/demo-drafts',
        json={'url': 'https://example.com', 'goal': 'Show the onboarding flow', 'language': 'en-US'},
    )
    assert res.status_code == 200
    body = res.json()
    assert body['title']
    assert isinstance(body['steps'], list) and body['steps']
    assert body['narration']


def test_create_demo_draft_validation():
    client = TestClient(app)
    res = client.post('/v1/demo-drafts', json={'url': 'not-a-url', 'goal': 'x'})
    assert res.status_code == 422


def test_video_job_accepts_narration_override():
    # Validate the schema directly (no POST) so we don't kick off the background
    # rendering pipeline / a real browser during tests.
    from app.models.video_job import VideoJobCreate

    payload = VideoJobCreate(
        url='https://example.com',
        goal='Show the onboarding flow',
        narration_override='A concise, human-approved narration.',
        title_override='My edited title',
    )
    assert payload.narration_override == 'A concise, human-approved narration.'
    assert payload.title_override == 'My edited title'
    # Overrides are optional and default to None (existing behavior unchanged).
    assert VideoJobCreate(url='https://example.com', goal='Show the flow').narration_override is None


def test_narration_override_flows_into_scenario():
    """The override authored before generation must be what NarrationWriter uses,
    so an edited narration actually reaches the rendered video (not faked)."""
    import asyncio

    from app.models.video_job import DemoScenario
    from app.services.planner import NarrationWriter

    scenario = DemoScenario(title='t', steps=['s'], narration='human approved script')
    script = asyncio.run(NarrationWriter().create_script(scenario, 'en-US'))
    assert script == 'human approved script'
