import enum
import logging
import traceback
from typing import Any

from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse

from model.context import NetContext
from model.endpoints.execute.request import ExecuteRequest
from model.endpoints.execute.response import create_response
from model.extree import ExecutionTree
from model.extree.node import Snapshot
from model.region import RegionType
from strategy.execution import get_choices
from utils import logging_utils
from utils.settings import settings

from simulator.src.paco.parser.region_module import RegionModule, RegionModuleNode, build_region_module

api = FastAPI(title=settings.title, version=settings.version, docs_url=settings.docs_url, redoc_url=None)

logger = logging_utils.get_logger(__name__)


@api.exception_handler(404)
@api.get("/")
def root():
    return RedirectResponse("/docs/", status_code=status.HTTP_303_SEE_OTHER)


class ActivityState(enum.IntEnum):
    WILL_NOT_BE_EXECUTED = -1
    WAITING = 0
    ACTIVE = 1
    COMPLETED = 2
    COMPLETED_WITHOUT_PASSING_OVER = 3


def _maybe_build_region_module(region: Any) -> Any:
    if isinstance(region, dict):
        return build_region_module(region)
    return region


def _as_region_node(region: Any) -> Any:
    if isinstance(region, RegionModule):
        return region.root
    if isinstance(region, RegionModuleNode):
        return region
    return region


def parse(region, activated_nodes_ids: list[str | int]):
    region_node = _as_region_node(_maybe_build_region_module(region))

    if not isinstance(activated_nodes_ids, set):
        activated_nodes_ids = {str(_id) for _id in activated_nodes_ids if _id is not None}

    if region_node.type != RegionType.SEQUENTIAL and str(region_node.id) not in activated_nodes_ids:
        return []

    if not region_node.children:
        return [region_node]

    active_regions = []
    for child in region_node.children:
        active_regions.extend(parse(child, activated_nodes_ids))

    return active_regions


@api.post("/execute")
def execute(data: ExecuteRequest):
    try:
        region, net, im, fm, extree, decisions = data.to_object()
        region = _maybe_build_region_module(region)
        logger.info("Request received:")
        if not net:
            logger.info("No net defined. Creating new context and execution tree.")
            ctx = NetContext.from_region(region)
            net = ctx.net
            im = ctx.initial_marking
            fm = ctx.final_marking
            extree = ExecutionTree.from_context(ctx)
        else:
            if decisions is None:
                decisions = []
            if not all(decisions):
                raise ValueError("One or more decisions are not valid transitions in the Petri net.")

            logger.info("Net defined, using provided markings and execution tree.")
            ctx = NetContext(region=region, net=net, im=im, fm=fm)
            logger.info("Strategy Type: %s", type(ctx.strategy))
            current_marking = extree.current_node.snapshot.marking
            logger.info("Current marking: %s", current_marking)

            logger.info("Consuming decisions: %s", decisions)
            new_marking, probability, impacts, execution_time, choices, fired_transitions = ctx.strategy.consume(
                ctx, current_marking, decisions
            )

            decision_ids = [transition.name for transition in decisions]

            status = {}
            for active in parse(region, [t.get_region_id() for t in fired_transitions]):
                status[active.id] = ActivityState.ACTIVE

            choices_node_id = [place.entry_id for place in get_choices(ctx, new_marking).keys()]

            print("execute:", status, decisions, choices_node_id)
            new_snapshot = Snapshot(
                marking=new_marking,
                probability=probability,
                impacts=impacts,
                time=execution_time,
                status=status,
                decisions=decision_ids,
                choices=choices_node_id,
            )

            extree.add_snapshot(ctx, new_snapshot)

        return create_response(region, net, im, fm, extree).model_dump(
            exclude_unset=True, exclude_none=True, exclude_defaults=True
        )
    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return {
            "type": "error",
            "message": str(e),
            "traceback": traceback.format_tb(e.__traceback__),
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(api, host=settings.host, port=settings.port)
