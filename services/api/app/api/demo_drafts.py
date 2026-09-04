from fastapi import APIRouter

from app.models.video_job import DemoDraft, DemoDraftRequest, VideoJobCreate
from app.services.planner import NarrationWriter, ScenarioPlanner

router = APIRouter(prefix="/v1/demo-drafts", tags=["demo-drafts"])


@router.post("", response_model=DemoDraft)
async def create_demo_draft(payload: DemoDraftRequest) -> DemoDraft:
    """Produce an editable scenario + narration draft for a URL and goal.

    This is a lightweight, read-only planning step: it reuses the existing
    ScenarioPlanner and NarrationWriter but does NOT open a browser, record, or
    render. The WebMCP `create_demo` tool calls this so a human/agent can start
    from a real draft and refine the narration before triggering generation.
    """
    request = VideoJobCreate(url=payload.url, goal=payload.goal, language=payload.language)
    scenario = await ScenarioPlanner().create_scenario(request)
    narration = await NarrationWriter().create_script(scenario, payload.language)
    return DemoDraft(title=scenario.title, steps=scenario.steps, narration=narration)
