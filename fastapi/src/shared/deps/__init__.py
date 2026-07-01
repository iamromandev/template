"""Dependency-injection layer — shared FastAPI dependencies only.

Module-specific ``get_<module>_service()`` factories live in each
module's ``service/__init__.py``. This package only exposes the
cross-cutting concerns (auth, cache, pagination, sorting, shared
singletons).
"""

from src.shared.deps.auth import get_current_user_id as get_current_user_id
from src.shared.deps.auth import require_user_id as require_user_id
from src.shared.deps.cache import get_cache as get_cache
from src.shared.deps.common import PaginationParams as PaginationParams
from src.shared.deps.common import SortParams as SortParams
from src.shared.deps.common import pagination_params as pagination_params
from src.shared.deps.common import sort_params as sort_params
from src.shared.deps.container import get_event_bus as get_event_bus
