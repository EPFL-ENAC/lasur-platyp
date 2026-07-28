from api.db import AsyncSession


class EntityService:

    def __init__(self, session: AsyncSession):
        self.session = session

    def merge_ids_filter(self, existing_ids: int | list | dict | None, permitted_ids: list) -> dict:
        """Merge existing filter ids with permitted ids"""
        if existing_ids is None:
            return permitted_ids
        # Handle different types of existing_ids
        if isinstance(existing_ids, dict) and "$in" in existing_ids:
            existing_ids = existing_ids["$in"]
        elif isinstance(existing_ids, dict) and "$eq" in existing_ids:
            existing_ids = [existing_ids["$eq"]]
        elif isinstance(existing_ids, int):
            existing_ids = [existing_ids]
        return list(set(existing_ids) & set(permitted_ids))
