from fastapi import APIRouter, Depends

from app.application.use_cases.full_process import FullProcessUseCase
from app.application.use_cases.parse_itinerary import ParseItineraryUseCase
from app.application.use_cases.resolve_places import ResolvePlacesUseCase
from app.core.config import Settings, get_settings
from app.domain.models.itinerary import TravelRequest
from app.domain.models.workflow import FullProcessResponse
from app.domain.services.geojson_builder import GeoJSONBuilder
from app.domain.services.sequence_builder import SequenceBuilder
from app.infrastructure.geocoding.provider_factory import build_geocoder_provider
from app.infrastructure.llm.provider_factory import build_llm_provider
from app.infrastructure.routing.provider_factory import build_routing_provider

router = APIRouter(prefix="/workflows", tags=["workflows"])


def get_full_process_use_case(settings: Settings = Depends(get_settings)) -> FullProcessUseCase:
    return FullProcessUseCase(
        parser=ParseItineraryUseCase(build_llm_provider(settings)),
        resolver=ResolvePlacesUseCase(build_geocoder_provider(settings)),
        sequence_builder=SequenceBuilder(),
        routing_provider=build_routing_provider(settings),
        geojson_builder=GeoJSONBuilder(),
    )


@router.post("/full-process", response_model=FullProcessResponse)
async def full_process(
    request: TravelRequest,
    use_case: FullProcessUseCase = Depends(get_full_process_use_case),
) -> FullProcessResponse:
    return await use_case.execute(request)
