from pydantic import BaseModel


class SettingsRead(BaseModel):
    zoho_client_id:    str
    zoho_client_secret: str   # masked on read
    zoho_refresh_token: str   # masked on read
    zoho_org_id:       str
    zoho_region:       str
    input_folder:      str
    output_folder:     str
    db_path:           str
    default_item_rate: float
    default_customer:  str
    watch_enabled:     bool
    last_watch_event:  str | None

    model_config = {"from_attributes": True}


class SettingsUpdate(BaseModel):
    zoho_client_id:     str | None = None
    zoho_client_secret: str | None = None
    zoho_refresh_token: str | None = None
    zoho_org_id:        str | None = None
    zoho_region:        str | None = None
    input_folder:       str | None = None
    output_folder:      str | None = None
    db_path:            str | None = None
    default_item_rate:  float | None = None
    default_customer:   str | None = None
    watch_enabled:      bool | None = None
