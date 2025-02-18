import datetime
import secrets
from fastapi import APIRouter, Depends, HTTPException
from api.db import get_session, AsyncSession
from api.models.domain import Campaign
from api.models.query import CaseReportDraft
from api.services.participants import ParticipantService
from api.services.campaigns import CampaignService

router = APIRouter()


@router.get("/participant/{tokenOrSlug}", response_model=CaseReportDraft, response_model_exclude_none=True)
async def get(tokenOrSlug: str, session: AsyncSession = Depends(get_session)) -> CaseReportDraft:
    """Get a case report by participant token or campaign slug"""
    campaign = None
    try:
        campaign = await CampaignService(session).get_by_slug(tokenOrSlug)
    except:
        campaign = None

    if campaign is not None:
        _check_campaign(campaign)
        # this is a campaign's slug then create an empty participant
        data = {
            "workplace": {
                "address": campaign.address,
                "lon": campaign.lon,
                "lat": campaign.lat
            }
        }
        return CaseReportDraft(token=secrets.token_urlsafe(16), data=data)

    # this is a participant's token
    participant = await ParticipantService(session).get_by_token(tokenOrSlug)
    if participant.status == "completed":
        raise HTTPException(
            status_code=400, detail="Participant has already completed the survey")
    campaign = await CampaignService(session).get(participant.campaign_id)
    _check_campaign(campaign)
    data = participant.data
    data["workplace"] = {
        "address": campaign.address,
        "lon": campaign.lon,
        "lat": campaign.lat
    }
    return CaseReportDraft(token=tokenOrSlug, data=data)


def _check_campaign(campaign: Campaign):
    """Check if campaign has a valid time frame

    Args:
        campaign (Campaign): The campaign to check

    Raises:
        HTTPException: 400 if campaign has not started yet
        HTTPException: 400 if campaign has already ended
    """
    if campaign.start_date is not None and campaign.start_date > datetime.now():
        raise HTTPException(
            status_code=400, detail="Campaign has not started yet")
    if campaign.end_date is not None and campaign.end_date < datetime.now():
        raise HTTPException(
            status_code=400, detail="Campaign has already ended")
