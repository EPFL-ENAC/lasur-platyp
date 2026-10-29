from enacit4r_sql.models.query import ListResult
from enacit4r_auth.models.auth import AppUser, AppUserDraft, AppUserPassword


class AppUserListItem(AppUser):
    # identity providers (e.g. github, google) the user signs in with, no password then
    identity_providers: list[str] = []


class AppUserResult(ListResult):
    data: list[AppUserListItem] = []
