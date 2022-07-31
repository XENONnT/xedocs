import datetime
import pydantic
import rframe

try:
    import utilix

    uconfig = utilix.uconfig
    from utilix import xent_collection

except ImportError:
    uconfig = None

    def xent_collection(**kwargs):
        raise RuntimeError("utilix not configured")


from pydantic import validator
from typing import Literal

from .base_analysis import BaseAnalysisSchema
from ..._settings import settings


RSE_TYPE = Literal[
    "SURFSARA_USERDISK",
    "SDSC_USERDISK",
    "LNGS_USERDISK",
    "UC_OSG_USERDISK",
    "UC_DALI_USERDISK",
    "CNAF_USERDISK",
]


def xeauth_user():
    if uconfig is None:
        return "unknown"
    return uconfig.get("xeauth", "api_user", fallback="unknown")


class ProcessingRequest(BaseAnalysisSchema):
    """Schema definition for a processing request"""

    _ALIAS = "processing_requests"

    data_type: str = rframe.Index()
    lineage_hash: str = rframe.Index()
    run_id: str = rframe.Index()
    destination: RSE_TYPE = rframe.Index(default="UC_DALI_USERDISK")
    user: str = pydantic.Field(default_factory=xeauth_user)
    request_date: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.utcnow
    )

    priority: int = -1

    comments: str = ""

    def pre_update(self, datasource, new):
        if new.user != self.user:
            raise ValueError(new.user)
        if new.run_id != self.run_id:
            raise ValueError(new.run)

    def latest_context(self):
        import utilix
        import pymongo

        contexts = utilix.xent_collection("contexts")
        ctx = contexts.find_one(
            {f"hashes.{self.data_type}": self.lineage_hash},
            projection={"context": "$name", "env": "$tag", "_id": 0},
            sort=[("date_added", pymongo.DESCENDING)],
        )

        return dict(ctx)
