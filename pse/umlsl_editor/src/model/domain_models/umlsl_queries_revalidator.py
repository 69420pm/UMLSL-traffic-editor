from __future__ import annotations

from dataclasses import dataclass
from threading import Lock, Thread
from typing import TYPE_CHECKING, Optional

from pse.umlsl_editor.src.model.entities.umlsl_query import UMLSLQueryParams
from pse.umlsl_editor.src.model.helper.event_types import UMLSLQueriesEventType
from pse.umlsl_editor.src.query.evaluator import UMLSLEvaluator

if TYPE_CHECKING:
    from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_model import (
        TrafficSnapshotModel,
    )
    from pse.umlsl_editor.src.model.domain_models.umlsl_queries_model import (
        UMLSLQueriesModel,
    )


@dataclass
class UMLSLQueriesRevalidator:
    _queries_model: "UMLSLQueriesModel"

    def __init__(self, queries_model: "UMLSLQueriesModel") -> None:
        self._queries_model = queries_model
        self._lock = Lock()
        self._generation = 0
        self._pending_snapshot: Optional["TrafficSnapshotModel"] = None
        self._worker: Optional[Thread] = None
        self._loading_generation_by_query: dict[str, int] = {}

    def revalidate_async(self, snapshot: "TrafficSnapshotModel") -> None:
        with self._lock:
            self._generation += 1
            self._pending_snapshot = snapshot
            if self._worker is None or not self._worker.is_alive():
                self._worker = Thread(target=self._worker_loop, daemon=True)
                self._worker.start()

    def _worker_loop(self) -> None:
        while True:
            with self._lock:
                snapshot = self._pending_snapshot
                generation = self._generation
                self._pending_snapshot = None
            if snapshot is None:
                return
            self._run_revalidation(snapshot, generation)

    def _run_revalidation(
            self, snapshot: "TrafficSnapshotModel", generation: int
    ) -> None:
        if not self._is_current(generation):
            return

        self._queries_model.notify(
            UMLSLQueriesEventType.UMLSL_QUERIES_REVALIDATION_STARTED,
        )
        canceled = False
        try:
            snapshot.validator.validate_queries(self._queries_model)
            umlsl_evaluator = UMLSLEvaluator(snapshot)

            for query in list(self._queries_model.queries.values()):
                if not self._is_current(generation):
                    self._cancel_generation(generation)
                    canceled = True
                    break

                self._set_loading(query, True, generation)
                try:
                    ego = snapshot.get_cars().get(query.assigned_car_uid)
                    evaluate_ego_lane_only = query.should_only_evaluate_on_cars_lane
                    holding = umlsl_evaluator.parse_ast(query.latex, ego).evaluate(
                        evaluate_ego_lane_only
                    )
                    new_query_params = UMLSLQueryParams(
                        latex=query.latex,
                        holding=holding,
                        should_only_evaluate_on_cars_lane=evaluate_ego_lane_only,
                        assigned_car_uid=ego.uid,
                    )
                    if not self._is_current(generation):
                        self._cancel_generation(generation)
                        canceled = True
                        break
                    if (
                            query.holding != new_query_params.holding
                            or query.latex != new_query_params.latex
                            or query.assigned_car_uid != new_query_params.assigned_car_uid
                    ):
                        self._queries_model.update_umlsl_query(query, new_query_params)
                # except Exception as exc:
                #     self._queries_model.notify(
                #         UMLSLQueriesEventType.UMLSL_QUERY_WARNING,
                #         {"query": query, "error": exc},
                #     )
                finally:
                    self._set_loading(query, False, generation)
        finally:
            self._queries_model.notify(
                UMLSLQueriesEventType.UMLSL_QUERIES_REVALIDATION_FINISHED,
            )

    def _set_loading(self, query, is_loading: bool, generation: int) -> None:
        with self._lock:
            if is_loading:
                self._loading_generation_by_query[query.uid] = generation
            else:
                if self._loading_generation_by_query.get(query.uid) != generation:
                    return
                del self._loading_generation_by_query[query.uid]
        self._queries_model.notify(
            UMLSLQueriesEventType.UMLSL_QUERY_LOADING,
            {"query": query, "is_loading": is_loading},
        )

    def _cancel_generation(self, generation: int) -> None:
        with self._lock:
            to_clear = [
                uid
                for uid, gen in self._loading_generation_by_query.items()
                if gen == generation
            ]
            for uid in to_clear:
                del self._loading_generation_by_query[uid]
        for uid in to_clear:
            query = self._queries_model.queries.get(uid)
            if query is not None:
                self._queries_model.notify(
                    UMLSLQueriesEventType.UMLSL_QUERY_LOADING,
                    {"query": query, "is_loading": False},
                )

    def _is_current(self, generation: int) -> bool:
        with self._lock:
            return generation == self._generation
