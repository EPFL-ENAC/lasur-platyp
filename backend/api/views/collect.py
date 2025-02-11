import datetime
from fastapi import APIRouter, Depends, HTTPException
from api.db import get_session, AsyncSession
from api.models.query import ParticipantData
from api.services.participants import ParticipantService
from api.services.campaigns import CampaignService

router = APIRouter()


@router.get("/participant/{token}", response_model=ParticipantData, response_model_exclude_none=True)
async def get(token: str, session: AsyncSession = Depends(get_session)) -> ParticipantData:
    """Get a participant by token and return its data if the status is still not completed"""
    participant = await ParticipantService(session).get_by_token(token)
    if participant.status == "completed":
        raise HTTPException(
            status_code=400, detail="Participant has already completed the survey")
    campaign = await CampaignService(session).get(participant.campaign_id)
    if campaign.start_date is not None and campaign.start_date > datetime.now():
        raise HTTPException(
            status_code=400, detail="Campaign has not started yet")
    if campaign.end_date is not None and campaign.end_date < datetime.now():
        raise HTTPException(
            status_code=400, detail="Campaign has already ended")
    data = participant.data
    data["workplace"] = {
        "address": campaign.address,
        "lon": campaign.lon,
        "lat": campaign.lat
    }
    return ParticipantData(data=data)
