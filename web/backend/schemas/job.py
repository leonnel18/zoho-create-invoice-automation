from pydantic import BaseModel


class JobRead(BaseModel):
    id:              int
    triggered_by:    str
    status:          str
    pdf_filename:    str | None
    log_output:      str | None
    invoices_pushed: int
    errors:          int
    started_at:      str
    finished_at:     str | None

    model_config = {"from_attributes": True}


class JobStarted(BaseModel):
    job_id: int
    message: str = "Pipeline started"
