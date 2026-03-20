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

        snapshot.validator.validate_queries(self._queries_model)
        umlsl_evaluator = UMLSLEvaluator(snapshot)

        for query in list(self._queries_model.queries.values()):
            if not self._is_current(generation):
                return

            self._queries_model.notify(
                UMLSLQueriesEventType.UMLSL_QUERY_LOADING,
                {"query": query, "is_loading": True},
            )
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
                    return
                if (
                        query.holding != new_query_params.holding
                        or query.latex != new_query_params.latex
                        or query.assigned_car_uid != new_query_params.assigned_car_uid
                ):
                    self._queries_model.update_umlsl_query(query, new_query_params)
            except Exception as exc:
                self._queries_model.notify(
                    UMLSLQueriesEventType.UMLSL_QUERY_WARNING,
                    query
                    # {"query": query, "error": exc},
                )
            finally:
                if self._is_current(generation):
                    self._queries_model.notify(
                        UMLSLQueriesEventType.UMLSL_QUERY_LOADING,
                        query
                        # {"query": query, "is_loading": False},
                    )

    def _is_current(self, generation: int) -> bool:
        with self._lock:
            return generation == self._generation
