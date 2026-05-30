from uuid import uuid4

import structlog

from app.application.use_cases.parse_itinerary import ParseItineraryUseCase
from app.application.use_cases.resolve_places import ResolvePlacesUseCase
from app.domain.models.itinerary import TravelRequest
from app.domain.models.route import RouteCalculationRequest
from app.domain.models.workflow import ConfidenceSummary, FullProcessResponse
from app.domain.services.geojson_builder import GeoJSONBuilder
from app.domain.services.sequence_builder import SequenceBuilder
from app.infrastructure.routing.base import RoutingProvider, RoutingProviderError
from app.core.errors import AppError, ErrorCode

logger = structlog.get_logger(__name__)


class FullProcessUseCase:
    def __init__(
        self,
        parser: ParseItineraryUseCase,
        resolver: ResolvePlacesUseCase,
        sequence_builder: SequenceBuilder,
        routing_provider: RoutingProvider,
        geojson_builder: GeoJSONBuilder,
    ) -> None:
        self.parser = parser
        self.resolver = resolver
        self.sequence_builder = sequence_builder
        self.routing_provider = routing_provider
        self.geojson_builder = geojson_builder

    async def execute(self, request: TravelRequest) -> FullProcessResponse:
        request_id = uuid4()
        log = logger.bind(request_id=str(request_id))
        log.info("workflow_started")

        parsed = await self.parser.execute(request)
        resolved = await self.resolver.execute(parsed.parsed_itinerary)
        sequence = self.sequence_builder.build(parsed.parsed_itinerary, resolved.resolved_places)
        try:
            route = await self.routing_provider.calculate(
                RouteCalculationRequest(
                    sequence=sequence.sequence,
                    transport_mode=parsed.parsed_itinerary.transport.get("mode") or "driving",
                )
            )
        except RoutingProviderError as exc:
            raise AppError(
                ErrorCode.routing_failed,
                str(exc),
                recoverable=True,
                status_code=502,
            ) from exc
        geojson = self.geojson_builder.build(sequence.sequence, route.route_segments)

        warnings = [*parsed.warnings, *resolved.warnings, *sequence.warnings, *route.warnings]
        geocoding_confidence = self._average([place.confidence for place in resolved.resolved_places])
        sequencing_confidence = self._average([step.confidence for step in sequence.sequence])
        overall = self._average([parsed.confidence_score, geocoding_confidence, sequencing_confidence])

        log.info(
            "workflow_completed",
            warning_count=len(warnings),
            resolved_count=len(resolved.resolved_places),
            route_segment_count=len(route.route_segments),
        )

        return FullProcessResponse(
            request_id=request_id,
            parsed_itinerary=parsed.parsed_itinerary,
            entities=parsed.raw_entities,
            resolved_places=resolved.resolved_places,
            unresolved_places=[place.model_dump() for place in resolved.unresolved_places],
            sequence=sequence.sequence,
            route_segments=route.route_segments,
            geojson=geojson,
            warnings=warnings,
            confidence_summary=ConfidenceSummary(
                overall=round(overall, 2),
                parsing=parsed.confidence_score,
                geocoding=round(geocoding_confidence, 2),
                sequencing=round(sequencing_confidence, 2),
            ),
        )

    def _average(self, values: list[float]) -> float:
        if not values:
            return 0
        return sum(values) / len(values)
