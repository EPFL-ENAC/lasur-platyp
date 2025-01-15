from typing import List, Optional, Dict
from sqlmodel import Field
from sqlalchemy.dialects.postgresql import JSONB as JSON
from api.models.domain import FormBase, FormRevisionBase, CompanyBase, CampaignBase, ParticipantBase, CaseReportBase, DataEntryBase
from enacit4r_sql.models.query import ListResult

class FormRead(FormBase):
    id: int
    
class FormResult(ListResult):
    data: List[FormRead] = []
    
class FormRevisionRead(FormRevisionBase):
    id: int

class CompanyRead(CompanyBase):
    id: int

class CampaignRead(CampaignBase):
    id: int

class ParticipantRead(ParticipantBase):
    id: int

class CaseReportRead(CaseReportBase):
    id: int
    data: JSON

class DataEntryRead(DataEntryBase):
    id: int
    data: JSON