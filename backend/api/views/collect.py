from datetime import datetime
import secrets
from typing import Dict
from fastapi import APIRouter, Depends, HTTPException
from api.db import get_session, AsyncSession
from api.models.domain import Campaign
from api.models.query import RecordDraft, RecordRead, RecordComments, CampaignInfo
from api.services.participants import ParticipantService
from api.services.campaigns import CampaignService
from api.services.companies import CompanyService
from api.services.actions import CompanyActionService
from api.services.records import RecordService
from api.services.modal_typo import ModalTypoService

router = APIRouter()


@router.get("/info/{tokenOrSlug}", response_model=CampaignInfo, response_model_exclude_none=True)
async def get_info(tokenOrSlug: str, session: AsyncSession = Depends(get_session)) -> CampaignInfo:
    """Get campaign info by participant token or campaign slug"""
    if tokenOrSlug is None:
        raise HTTPException(
            status_code=400, detail="Missing token or slug")
    try:
        campaign = await CampaignService(session).get_by_slug(tokenOrSlug)
    except:
        campaign = None
    if not campaign:
        try:
            cr = await RecordService(session).get_by_token(tokenOrSlug)
            if cr:
                campaign = await CampaignService(session).get(cr.campaign_id)
        except:
            campaign = None
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    company = await CompanyService(session).get(campaign.company_id)
    return CampaignInfo(
        name=campaign.name,
        company_name=company.name,
        contact_email=campaign.contact_email if campaign.contact_email else company.contact_email,
        contact_name=campaign.contact_name if campaign.contact_name else company.contact_name,
        info_url=campaign.info_url if campaign.info_url else company.info_url,
        workplaces=campaign.workplaces
    )


@router.get("/record/{tokenOrSlug}", response_model=RecordDraft, response_model_exclude_none=True)
async def get(tokenOrSlug: str, session: AsyncSession = Depends(get_session)) -> RecordDraft:
    """Get a record by participant token or campaign slug"""

    # 1. if this is a slug, then create an empty participant
    campaign = None
    try:
        campaign = await CampaignService(session).get_by_slug(tokenOrSlug)
    except:
        campaign = None

    if campaign is not None:
        _check_campaign(campaign)
        # this is a campaign's slug then initialize a new record
        data = {
            "workplace": {
                "address": campaign.address,
                "lon": campaign.lon,
                "lat": campaign.lat
            }
        }
        return RecordDraft(token=secrets.token_urlsafe(16), data=data)

    # 2. this is a participant's token: try to get the record in case it was already saved
    cr = None
    try:
        cr = await RecordService(session).get_by_token(tokenOrSlug)
    except:
        cr = None  # 404 if not found
    if cr is not None:
        campaign = await CampaignService(session).get(cr.campaign_id)
        _check_campaign(campaign)
        return cr

    # 3. this is a participant's token: initialize a new record
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
    return RecordDraft(token=tokenOrSlug, data=data)


@router.post("/record/{tokenOrSlug}", response_model=RecordRead, response_model_exclude_none=True)
async def createOrUpdate(
    tokenOrSlug: str,
    item: RecordDraft,
    session: AsyncSession = Depends(get_session)
) -> RecordRead:
    """Create or update a record"""
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
        campaign = await CampaignService(session).get(participant.campaign_id)
    return await RecordService(session).createOrUpdate(item, campaign)


@router.put("/record/{token}/comments", response_model=RecordRead, response_model_exclude_none=True)
async def saveComments(
    token: str,
    data: RecordComments,
    session: AsyncSession = Depends(get_session)
) -> RecordRead:
    """Update a record comments"""
    if token is None:
        raise HTTPException(
            status_code=400, detail="Missing token")
    recordService = RecordService(session)
    record = await recordService.get_by_token(token)
    record.comments = data.comments
    return await recordService.update(record.id, record)


@router.get("/record/{token}/typo")
async def getTypo(token: str, locale: str = "en", session: AsyncSession = Depends(get_session)) -> Dict:
    """Get modal typology by record token"""
    if token is None:
        raise HTTPException(
            status_code=400, detail="Missing token")
    recordService = RecordService(session)
    record = await recordService.get_by_token(token)
    response = {}
    service = ModalTypoService()
    reco = service.get_recommendation_multi(record)
    response["reco"] = reco
    reco_pro = None
    if "scores" in reco:
        reco_pro = service.get_recommendation_pro(record, reco["scores"])
        response["reco_pro"] = reco_pro
    if "reco_dt2" in reco and reco_pro is not None:
        company = await CompanyService(session).get(record.company_id)
        campaign = await CampaignService(session).get(record.campaign_id)
        custom_actions = await CompanyActionService(session).get_company_actions(company.id)
        actions = service.get_recommendation_employer_actions(
            company, campaign, custom_actions, locale, reco["reco_dt2"], reco_pro["reco_pros"])
        response["reco_actions"] = actions
    record.typo = response
    record.comments = None  # clear comments
    await recordService.update(record.id, record)
    return response


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
