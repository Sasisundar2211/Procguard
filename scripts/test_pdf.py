from app.services.pdf import render_timeline_pdf
from app.schemas import BatchTimelineResponse, StageTimeline, Marker
import uuid
from datetime import datetime

# Mock data
timeline = BatchTimelineResponse(
    batch_id=uuid.uuid4(),
    procedure_id=uuid.uuid4(),
    procedure_version=1,
    time_axis={"unit": "days", "range": [0, 70]},
    stages=[
        StageTimeline(
            stage_id="S1", label="Stage 1", 
            expected_window=(0, 5), actual_window=(0, 5), 
            status="ON_TIME", markers=[]
        )
    ],
    legend_counts={},
    delay_buckets=[],
    delayed_batches=[]
)

class MockLog:
    def __init__(self):
        self.timestamp = datetime.now()
        self.actor = "test_actor"
        self.action = "test_action"
        self.result = "SUCCESS"
        self.expected_state = "START"
        self.actual_state = "END"

logs = [MockLog()]

print("Rendering PDF...")
pdf = render_timeline_pdf(timeline, logs)
print(f"Success! PDF size: {len(pdf)} bytes")
