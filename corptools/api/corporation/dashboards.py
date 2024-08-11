import logging
from typing import List

from ninja import NinjaAPI

from django.db.models import Sum
from django.utils import timezone

from allianceauth.services.hooks import get_extension_logger

from corptools import models
from corptools.api import schema
from corptools.task_helpers.update_tasks import fetch_location_name

logger = get_extension_logger(__name__)


class DashboardApiEndpoints:

    tags = ["Dashboards"]

    def __init__(self, api: NinjaAPI):
        @api.get(
            "dashboard/gates",
            response={200: List, 403: schema.Message},
            tags=self.tags
        )
        def get_dashboard_gates(request):
            perms = (
                request.user.has_perm('corptools.own_corp_manager')
                | request.user.has_perm('corptools.alliance_corp_manager')
                | request.user.has_perm('corptools.state_corp_manager')
                | request.user.has_perm('corptools.global_corp_manager')
                | request.user.has_perm('corptools.holding_corp_structures')
            )

            if not perms:
                logging.error(
                    f"Permission Denied for {request.user} to view structures!")
                return 403, {"message": "Permission Denied!"}

            output = []
            structures = models.Structure.get_visible(request.user).select_related(
                "corporation__corporation", "system_name"
            ).prefetch_related('structureservice_set').filter(type_id=35841)

            ozone = models.CorpAsset.objects.filter(
                type_id=16273,
                location_flag="StructureFuel"
            ).values("location_id").annotate(total=Sum('quantity'))
            levels = {}
            for o in ozone:
                if o["location_id"] not in levels:
                    levels[o["location_id"]] = 0
                levels[o["location_id"]] += o["total"]

            second_systems = set()
            output = {}
            now = timezone.now()
            for s in structures:
                split = s.name.split(" » ")
                from_sys = split[0]
                to_sys = split[1].split(" - ")[0]
                logger.warning(f"CT_JB: `{from_sys}` `{to_sys}`")
                days = 0
                if s.fuel_expires:
                    days = (s.fuel_expires - now).days
                active = False
                for ss in s.structureservice_set.all():
                    if ss.name == "Jump Gate Access" and ss.state == "online":
                        active = True
                if from_sys in second_systems:
                    output[to_sys]["end"] = {
                        "system_name": s.system_name.name,
                        "system_id": s.system_name_id,
                        "ozone": levels.get(s.structure_id),
                        "known": True,
                        "active": active,
                        "expires": days,
                        "name": s.name
                    }
                else:
                    output[from_sys] = {}
                    output[from_sys]["start"] = {
                        "system_name": s.system_name.name,
                        "system_id": s.system_name_id,
                        "ozone": levels.get(s.structure_id),
                        "known": True,
                        "active": active,
                        "expires": days,
                        "name": s.name
                    }
                    output[from_sys]["end"] = {
                        "known": False, "active": False}
                    second_systems.add(to_sys)

            return list(output.values())

        @api.get(
            "dashboard/sov",
            response={200: List, 403: str},
            tags=self.tags
        )
        def get_dashboard_sov(request):
            perms = (
                request.user.has_perm('corptools.holding_corp_assets')
            )

            if not perms:
                logging.error(
                    f"Permission Denied for {request.user} to view Sov Structures!")
                return 403, "Permission Denied!"

            types = [32458]

            assets = models.CorpAsset.get_visible(request.user).filter(
                type_id__in=types,
                location_type="solar_system").select_related(
                "type_name",
                "location_name",
                "location_name__system",
                "location_name__system__constellation",
                "location_name__system__constellation__region",
                "type_name__group__category"
            )

            asset_locations = models.CorpAsset.get_visible(request.user).filter(
                location_id__in=assets.values("item_id")).select_related(
                "type_name"
            )

            location_names = {}

            for a in assets:
                if not a.location_name_id:
                    location = fetch_location_name(
                        a.location_id, a.location_type, 0)
                    a.location_name = location
                loc_id = a.item_id
                if loc_id not in location_names:
                    location_names[loc_id] = {
                        "system": {
                            "name": a.location_name.location_name,
                            "const": a.location_name.system.constellation.name,
                            "rgn": a.location_name.system.constellation.region.name
                        },
                        "upgrades": []
                    }

            for a in asset_locations:
                location_names[a.location_id]["upgrades"].append({
                    "id": a.type_name.type_id,
                    "name": a.type_name.name,
                    "active": a.location_flag
                })

            return list(location_names.values())
