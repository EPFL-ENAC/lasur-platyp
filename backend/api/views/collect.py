import datetime
import secrets
from fastapi import APIRouter, Depends, HTTPException
from api.db import get_session, AsyncSession
from api.models.domain import Campaign, CaseReport
from api.models.query import CaseReportDraft, CaseReportRead
from api.services.participants import ParticipantService
from api.services.campaigns import CampaignService
from api.services.case_reports import CaseReportService

router = APIRouter()


@router.get("/case-report/{tokenOrSlug}", response_model=CaseReportDraft, response_model_exclude_none=True)
async def get(tokenOrSlug: str, session: AsyncSession = Depends(get_session)) -> CaseReportDraft:
    """Get a case report by participant token or campaign slug"""

    # 1. if this is a slug, then create an empty participant
    campaign = None
    try:
        campaign = await CampaignService(session).get_by_slug(tokenOrSlug)
    except:
        campaign = None

    if campaign is not None:
        _check_campaign(campaign)
        # this is a campaign's slug then initialize a new case report
        data = {
            "workplace": {
                "address": campaign.address,
                "lon": campaign.lon,
                "lat": campaign.lat
            }
        }
        return CaseReportDraft(token=secrets.token_urlsafe(16), data=data)

    # 2. this is a participant's token: try to get the case report in case it was already saved
    cr = None
    try:
        cr = CaseReportService(session).get_by_token(tokenOrSlug)
    except:
        cr = None  # 404 if not found
    if cr is not None:
        campaign = await CampaignService(session).get(cr.campaign_id)
        _check_campaign(campaign)
        return cr

    # 3. this is a participant's token: initialize a new case report
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


@router.post("/case-report/{tokenOrSlug}", response_model=CaseReportRead, response_model_exclude_none=True)
async def createOrUpdate(
    tokenOrSlug: str,
    item: CaseReportDraft,
    session: AsyncSession = Depends(get_session)
) -> CaseReportRead:
    """Create or update a case report"""
    if tokenOrSlug is None:
        raise HTTPException(
            status_code=400, detail="Missing token or slug")
    campaign = None
    if tokenOrSlug != item.token:
        # this is a campaign's slug
        campaign = await CampaignService(session).get_by_slug(tokenOrSlug)
    else:
        # this is a participant's token
        participant = await ParticipantService(session).get_by_token(tokenOrSlug)
        campaign = CampaignService(session).get(participant.campaign_id)
    return await CaseReportService(session).createOrUpdate(item, campaign)


@router.get("/typo/{token}", response_model=CaseReportRead, response_model_exclude_none=True)
async def getTypo(token: str, session: AsyncSession = Depends(get_session)) -> CaseReportRead:
    """Get modal typology by case report token"""
    return await CaseReportService(session).get_by_token(token)


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
