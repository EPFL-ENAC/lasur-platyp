from fastapi import APIRouter, Depends, Query, HTTPException
from api.db import get_session, AsyncSession
from api.auth import kc_service, User
from api.models.query import Stats, CampaignStats, LocationFilter, ComparisonRequest, ComparisonResult, ComparisonStats
from api.services.records import RecordService
from api.services.campaigns import CampaignService
from api.services.stats.stats import StatsService
from api.services.stats.longitudinal import LongitudinalService
from enacit4r_sql.utils.query import validate_params, ValidationError, paramAsDict

router = APIRouter()

PRIVACY_LIMIT = 5  # Minimum number of records required to compute statistics


@router.get("/all", response_model_exclude_none=True)
async def compute_all_statistics(
    filter: str = Query(None),
    user: User = Depends(kc_service.get_user_info()),
    session: AsyncSession = Depends(get_session),
) -> Stats:
    """Query all type of all statistics in records"""
    try:
        filter_dict = paramAsDict(filter)
        workplace_filter = filter_dict.get('workplace_location', None)
        if 'workplace_location' in filter_dict:
            del filter_dict['workplace_location']
        validated = validate_params(filter_dict, None, None, None)
        service = RecordService(session)
        df = await service.get_dataframe(validated["filter"], flat=True, user=user, special_permissions="read-aggregated")
        if workplace_filter:
            workplace_filter = LocationFilter.model_validate(
                workplace_filter, by_alias=True)
            df = service.filter_by_workplace_location(df, workplace_filter)

        if len(df) < PRIVACY_LIMIT:
            raise HTTPException(
                status_code=400, detail="Not enough records to compute statistics")

        return StatsService().compute_stats(df)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"{e}")


@router.post("/compare", response_model_exclude_none=True)
async def compare_statistics(
    request: ComparisonRequest,
    user: User = Depends(kc_service.get_user_info()),
    session: AsyncSession = Depends(get_session),
) -> ComparisonResult:
    """Compute side-by-side statistics for multiple campaign groups"""
    if len(request.groups) < 2:
        raise HTTPException(
            status_code=400, detail="At least 2 groups are required for comparison")
    try:
        filter_dict = dict(request.filter) if request.filter else {}
        workplace_filter = filter_dict.get('workplace_location', None)
        if 'workplace_location' in filter_dict:
            del filter_dict['workplace_location']
        validated = validate_params(filter_dict, None, None, None)

        service = RecordService(session)
        df = await service.get_dataframe(validated["filter"], flat=True, user=user, special_permissions="read-aggregated")
        if workplace_filter:
            workplace_filter = LocationFilter.model_validate(
                workplace_filter, by_alias=True)
            df = service.filter_by_workplace_location(df, workplace_filter)

        if request.mode == "longitudinal":
            df = LongitudinalService.filter_longitudinal(df, request.groups)

        warnings = []
        survived_groups = []
        for group in request.groups:
            group_df = df[df['campaign_id'].isin(group.campaign_ids)]
            if len(group_df) < PRIVACY_LIMIT:
                warnings.append(group.name)
                continue
            survived_groups.append(group)

        stats_service = StatsService()
        comparison_stats = []
        for group in survived_groups:
            group_df = df[df['campaign_id'].isin(group.campaign_ids)]
            stats = stats_service.compute_stats(group_df)
            comparison_stats.append(ComparisonStats(
                **stats.model_dump(),
                name=group.name,
                campaign_ids=group.campaign_ids
            ))

        mode_transitions = None
        if request.mode == "longitudinal":
            survived_campaign_ids = [
                campaign_id
                for group in survived_groups
                for campaign_id in group.campaign_ids
            ]
            transitions_df = df[df['campaign_id'].isin(
                survived_campaign_ids)]
            mode_transitions = LongitudinalService.compute_mode_transitions(
                transitions_df, request.groups)

        return ComparisonResult(
            groups=comparison_stats,
            mode_transitions=mode_transitions,
            warnings=warnings or None
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"{e}")


@router.get("/campaign/{id}", response_model_exclude_none=True)
async def compute_campaign_statistics(
    id: int,
    user: User = Depends(kc_service.get_user_info()),
    session: AsyncSession = Depends(get_session),
) -> CampaignStats:
    """Compute statistics for a campaign"""
    campaign = await CampaignService(session).get(id, user, special_permissions="read-aggregated")
    service = RecordService(session)
    df = await service.get_dataframe(
        {"campaign_id": id}, flat=True, user=user, special_permissions="read-aggregated")
    stats_service = StatsService()
    return stats_service.compute_campaign_stats(campaign, df)
