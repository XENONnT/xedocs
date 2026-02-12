from __future__ import annotations

import os
import sqlite3
import datetime as dt
from bson import BSON
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Type, Set
import json

import xedocs
from xedocs._settings import settings
from xedocs.utils import Database  # xedocs Database wrapper


# ---------- helpers ----------

# BSON decoding and decompression helper
_DCTX = None


def _decode_doc_bson_z(b: bytes) -> Dict[str, Any]:
    """Decode a compressed BSON blob produced by the dump script.

    The dumper stores BSON compressed with either zstd or zlib.
    We select the decompressor via OFFLINE_COMP (default: zstd).
    """
    global _DCTX
    comp = os.environ.get("OFFLINE_COMP", "zstd").strip() or "zstd"
    data = bytes(b)

    if comp == "zstd":
        if _DCTX is None or _DCTX[0] != "zstd":
            import zstandard as zstd  # type: ignore
            _DCTX = ("zstd", zstd.ZstdDecompressor())
        data = _DCTX[1].decompress(data)

    elif comp == "zlib":
        # zlib is stateless
        import zlib
        data = zlib.decompress(data)

    return BSON(data).decode()
def _to_utc_ns(t: dt.datetime) -> int:
    if t.tzinfo is None:
        t = t.replace(tzinfo=dt.timezone.utc)
    return int(t.timestamp() * 1e9)

def _from_utc_ns(x: int) -> dt.datetime:
    return dt.datetime.fromtimestamp(x / 1e9, tz=dt.timezone.utc)

def _normalize_time_label(labels: Dict[str, Any]) -> Dict[str, Any]:
    # mimic xedocs logic: allow run_id instead of time
    labels = dict(labels)
    if "run_id" in labels and "time" not in labels:
        run_id = labels.pop("run_id")
        labels["time"] = settings.run_id_to_time(run_id)
    if "run_id" in labels and "time" in labels:
        labels.pop("run_id", None)
    if "time" in labels and isinstance(labels["time"], dt.datetime):
        labels["time_ns"] = _to_utc_ns(settings.clock.normalize_tz(labels["time"]))
        labels.pop("time")
    return labels

def _normalize_interval_label(labels: Dict[str, Any]) -> Dict[str, Any]:
    labels = dict(labels)
    if "run_id" in labels and "time" not in labels:
        run_id = labels.pop("run_id")
        labels["time"] = settings.run_id_to_interval(run_id)
    if "time" in labels:
        iv = labels["time"]
        # TimeInterval has .left/.right, might be naive; normalize to UTC
        left = settings.clock.normalize_tz(iv.left)
        right = settings.clock.normalize_tz(iv.right)
        labels["time_left_ns"] = _to_utc_ns(left)
        labels["time_right_ns"] = _to_utc_ns(right)
        labels.pop("time")
    labels.pop("run_id", None)
    return labels



# ---------- core accessor ----------
@dataclass
class SQLiteAccessor:
    schema: Type[Any]
    conn: sqlite3.Connection
    table: str
    _columns: Set[str] = field(default_factory=set, init=False, repr=False)

    def __post_init__(self) -> None:
        # Cache the actual columns available in this sqlite table.
        # This lets us ignore query labels that are not stored in the DB
        # (e.g. URLConfig hints like fmt=...), mimicking the mongo backend.
        rows = self.conn.execute(f'PRAGMA table_info("{self.table}")').fetchall()
        # PRAGMA table_info returns rows where index 1 is the column name
        self._columns = {r[1] for r in rows}

    def _filter_labels_to_known_columns(self, labels: Dict[str, Any]) -> Dict[str, Any]:
        """Drop labels that are not real columns in this sqlite table.

        This is important because straxen/xedocs URLConfig sometimes passes
        extra hints (e.g. fmt=...) that are not stored as fields in Mongo.
        The mongo backend effectively ignores them; our sqlite backend should too.
        """
        return {k: v for k, v in labels.items() if k in self._columns}

    def _extra_label_cols(self) -> List[str]:
        # everything except time/version/value-ish fields
        # you can refine per schema if needed
        return [c for c in self.schema.__fields__.keys()
                if c not in ("time", "value", "created_date", "comments", "version")]

    def _where_from_labels(self, labels: Dict[str, Any]) -> tuple[list[str], list[Any]]:
        """Build SQL WHERE fragments and params from labels.

        - Scalars become `col = ?`
        - list/tuple/set become `col IN (?,?,...)` (empty list -> no matches)
        """
        where: list[str] = []
        params: list[Any] = []
        for k, v in labels.items():
            if isinstance(v, (list, tuple, set)):
                vv = list(v)
                if len(vv) == 0:
                    # Empty IN should match nothing
                    where.append("1 = 0")
                    continue
                qs = ",".join(["?"] * len(vv))
                where.append(f'"{k}" IN ({qs})')
                params.extend(vv)
            else:
                where.append(f'"{k}" = ?')
                params.append(v)
        return where, params

    def find_docs(self, limit: int = 1, sort: Any = None, **labels) -> List[Any]:
        """Find documents for this schema.

        The straxen URLConfig/xedocs protocol often passes `run_id` instead of an
        explicit `time`/`time interval`. In the mongo backend, xedocs resolves
        `run_id -> time` (midpoint) for sampled corrections and `run_id -> interval`
        for interval corrections.

        For the SQLite backend we emulate this behavior with a robust dispatch:

        - If the user provided an explicit interval-like object (has .left/.right):
          do interval query.
        - If the user provided an explicit datetime: do sampled query.
        - If only `run_id` is provided: try interval first, then fall back to sampled.
          (This matches typical xedocs usage where some corrections are interval-based
          and others are sampled.)
        - Otherwise, fall back to plain equality.

        Notes about `sort` / list-style access:
        - When straxen uses `?as_list=True&sort=pmt`, it expects *many* docs (e.g.
          one per PMT), not a single document. Therefore, if `sort` is provided and
          the caller did not override `limit`, we return *all* matching docs ordered
          by the sort column.
        """

        if self.table == "context_configs" and limit == 1 and sort is None:
            limit = 0  # 0 => no LIMIT in our SQL
            sort = "config_name"

        # If sort is provided and limit is left at default, treat this as "return all"
        if sort is not None and limit == 1:
            limit = 0  # 0 means "no LIMIT" in our SQL builders below

        # Explicit time provided by caller
        if "time" in labels:
            t = labels["time"]
            if hasattr(t, "left") and hasattr(t, "right"):
                return self._find_time_interval(limit=limit, sort=sort, **labels)
            if isinstance(t, dt.datetime):
                return self._find_time_sampled(limit=limit, sort=sort, **labels)

        # Only run_id provided: try interval first, then sampled
        if "run_id" in labels:
            out = self._find_time_interval(limit=limit, sort=sort, **labels)
            if out:
                return out
            return self._find_time_sampled(limit=limit, sort=sort, **labels)

        # If the caller already normalized to ns fields, route accordingly
        if "time_left_ns" in labels or "time_right_ns" in labels:
            return self._find_time_interval(limit=limit, sort=sort, **labels)
        if "time_ns" in labels:
            return self._find_time_sampled(limit=limit, sort=sort, **labels)

        return self._find_plain(limit=limit, sort=sort, **labels)

    def _find_plain(self, limit: int = 1, sort: Any = None, **labels) -> List[Any]:
        labels = self._filter_labels_to_known_columns(labels)
        where, params = self._where_from_labels(labels)
        sql = f'SELECT doc_bson_z FROM "{self.table}"'
        if where:
            sql += " WHERE " + " AND ".join(where)
        if sort is not None:
            sql += f' ORDER BY "{sort}" ASC'
        if limit and int(limit) > 0:
            sql += " LIMIT ?"
            params.append(int(limit))
        rows = self.conn.execute(sql, params).fetchall()
        out = []
        for r in rows:
            doc = _decode_doc_bson_z(r["doc_bson_z"])
            out.append(self.schema(**doc))
        return out

    def _find_time_sampled(self, limit: int = 1, sort: Any = None, **labels) -> List[Any]:
        labels = _normalize_time_label(labels)
        labels = self._filter_labels_to_known_columns(labels)
        t_ns = labels.pop("time_ns", None)
        if t_ns is None:
            raise ValueError("TimeSampledCorrection requires run_id or time")

        version = labels.get("version")
        if version is None:
            raise ValueError("Missing required label: version")

        # Build equality filters
        where, params = self._where_from_labels(labels)
        where.insert(0, '"version" = ?')
        params.insert(0, version)

        base = f'FROM "{self.table}" WHERE ' + " AND ".join(where)

        # exact match fast path
        row = self.conn.execute(
            f"SELECT doc_bson_z, time_ns, value_num, value_json {base} AND time_ns = ? LIMIT 1",
            params + [t_ns],
        ).fetchone()

        chosen_time_ns: Optional[int] = None
        if row is not None:
            chosen_time_ns = int(row["time_ns"])
        else:
            # prev / next
            prev = self.conn.execute(
                f"SELECT doc_bson_z, time_ns, value_num, value_json {base} AND time_ns <= ? ORDER BY time_ns DESC LIMIT 1",
                params + [t_ns],
            ).fetchone()
            nxt = self.conn.execute(
                f"SELECT doc_bson_z, time_ns, value_num, value_json {base} AND time_ns >= ? ORDER BY time_ns ASC LIMIT 1",
                params + [t_ns],
            ).fetchone()

            if prev is None and nxt is None:
                return []
            if prev is None:
                chosen_time_ns = int(nxt["time_ns"])
            elif nxt is None:
                chosen_time_ns = int(prev["time_ns"])
            else:
                # If both exist, choose the closer one in time (no interpolation for list-style queries)
                tp = int(prev["time_ns"])
                tn = int(nxt["time_ns"])
                chosen_time_ns = tp if (t_ns - tp) <= (tn - t_ns) else tn

        # If sort is requested (e.g. as_list=True&sort=pmt), return one doc per sort key.
        # Many xedocs collections (e.g. pmt_gains) have time sampling that is NOT synchronized
        # across the sort key. Correct behavior: for each sort value, pick the latest sample
        # with time_ns <= requested time.
        if sort is not None:
            # Build equality filters (excluding time_ns)
            where2, params2 = self._where_from_labels(labels)
            where2.insert(0, '"version" = ?')
            params2.insert(0, version)

            where_sql = " AND ".join(where2)

            # Sort ordering (PMT is stored as TEXT in your dump)
            order_sort = f'"{sort}"'
            if str(sort) in ("pmt",):
                order_sort = f'CAST("{sort}" AS INTEGER)'

            # Window function: latest row per sort key at/before t_ns
            sql = (
                "WITH ranked AS ("
                f'  SELECT doc_bson_z, "{sort}" AS sort_key, time_ns,'
                f'         ROW_NUMBER() OVER (PARTITION BY "{sort}" ORDER BY time_ns DESC) AS rn'
                f'  FROM "{self.table}"'
                f'  WHERE {where_sql} AND time_ns <= ?'
                ") "
                "SELECT doc_bson_z "
                "FROM ranked "
                "WHERE rn = 1 "
                f"ORDER BY {order_sort} ASC"
            )

            rows = self.conn.execute(sql, params2 + [t_ns]).fetchall()

            # Apply limit (if any) after ranking
            if limit and int(limit) > 0:
                rows = rows[: int(limit)]

            out = []
            for r in rows:
                # depending on row factory / query shape, r may be a tuple or sqlite3.Row
                blob = r[0] if not isinstance(r, sqlite3.Row) else r["doc_bson_z"]
                doc = _decode_doc_bson_z(blob)
                out.append(self.schema(**doc))
            return out

        # Scalar-style query: decode the chosen doc and (optionally) interpolate numeric values.
        # If we had an exact match, just return it.
        if row is not None:
            doc = _decode_doc_bson_z(row["doc_bson_z"])
            return [self.schema(**doc)]

        # For scalar queries, reuse prev/nxt logic and keep old interpolation behavior.
        prev = self.conn.execute(
            f"SELECT doc_bson_z, time_ns, value_num, value_json {base} AND time_ns <= ? ORDER BY time_ns DESC LIMIT 1",
            params + [t_ns],
        ).fetchone()
        nxt = self.conn.execute(
            f"SELECT doc_bson_z, time_ns, value_num, value_json {base} AND time_ns >= ? ORDER BY time_ns ASC LIMIT 1",
            params + [t_ns],
        ).fetchone()

        if prev is None and nxt is None:
            return []
        if prev is None:
            doc = _decode_doc_bson_z(nxt["doc_bson_z"])
            return [self.schema(**doc)]
        if nxt is None:
            doc = _decode_doc_bson_z(prev["doc_bson_z"])
            return [self.schema(**doc)]

        # Interpolate numeric value if possible
        tp = int(prev["time_ns"])
        tn = int(nxt["time_ns"])

        def _row_value_num(r: sqlite3.Row) -> Optional[float]:
            # Prefer value_num (fast), then try value_json, finally fall back to decoding BSON
            vn = r["value_num"]
            if vn is not None:
                try:
                    return float(vn)
                except Exception:
                    return None
            vj = r["value_json"]
            if vj:
                try:
                    vv = json.loads(vj)
                    if isinstance(vv, (int, float)):
                        return float(vv)
                except Exception:
                    pass
            try:
                d = _decode_doc_bson_z(r["doc_bson_z"])
                vv = d.get("value")
                if isinstance(vv, (int, float)):
                    return float(vv)
            except Exception:
                pass
            return None

        vp = _row_value_num(prev)
        vn = _row_value_num(nxt)

        # If non-numeric, just take prev
        if vp is None or vn is None:
            doc = _decode_doc_bson_z(prev["doc_bson_z"])
            return [self.schema(**doc)]

        if tn == tp:
            v = vp
        else:
            w = (t_ns - tp) / (tn - tp)
            v = vp + w * (vn - vp)

        # Start from prev doc, then override time/value
        out = _decode_doc_bson_z(prev["doc_bson_z"])
        out["time"] = _from_utc_ns(t_ns)
        out["value"] = v
        return [self.schema(**out)]

    def _find_time_interval(self, limit: int = 1, sort: Any = None, **labels) -> List[Any]:
        labels = _normalize_interval_label(labels)
        labels = self._filter_labels_to_known_columns(labels)
        left = labels.pop("time_left_ns", None)
        right = labels.pop("time_right_ns", None)
        if left is None or right is None:
            raise ValueError("TimeIntervalCorrection requires run_id or time interval")

        version = labels.get("version")
        if version is None:
            raise ValueError("Missing required label: version")

        where, params = self._where_from_labels(labels)
        where.insert(0, '"version" = ?')
        params.insert(0, version)

        base = f'FROM "{self.table}" WHERE ' + " AND ".join(where)

        sql_cover = (
            f'SELECT doc_bson_z {base} '
            f'AND time_left_ns <= ? AND time_right_ns >= ? '
        )
        if sort is not None:
            sql_cover += f' ORDER BY "{sort}" ASC'
        else:
            sql_cover += ' ORDER BY time_left_ns DESC'
        if limit and int(limit) > 0:
            sql_cover += ' LIMIT ?'
            rows = self.conn.execute(sql_cover, params + [left, right, int(limit)]).fetchall()
        else:
            rows = self.conn.execute(sql_cover, params + [left, right]).fetchall()
        if rows:
            out = []
            for r in rows:
                doc = _decode_doc_bson_z(r["doc_bson_z"])
                out.append(self.schema(**doc))
            return out

        sql_overlap = (
            f'SELECT doc_bson_z {base} '
            f'AND time_left_ns <= ? AND time_right_ns >= ? '
        )
        if sort is not None:
            sql_overlap += f' ORDER BY "{sort}" ASC'
        else:
            sql_overlap += ' ORDER BY time_left_ns DESC'
        if limit and int(limit) > 0:
            sql_overlap += ' LIMIT ?'
            rows = self.conn.execute(sql_overlap, params + [right, left, int(limit)]).fetchall()
        else:
            rows = self.conn.execute(sql_overlap, params + [right, left]).fetchall()
        out = []
        for r in rows:
            doc = _decode_doc_bson_z(r["doc_bson_z"])
            out.append(self.schema(**doc))
        return out


# ---------- DataLocation ----------
class SQLiteCorrections:
    """
    Minimal xedocs DataLocation for corrections stored in sqlite.

    Required env or args:
      - sqlite_path: path to corrections sqlite
    """
    def __init__(self, sqlite_path: str):
        self.sqlite_path = sqlite_path
        self.conn = sqlite3.connect(sqlite_path)
        self.conn.row_factory = sqlite3.Row

    def data_accessor(self, schema):
        table = schema._ALIAS  # keep table name equal to alias
        return SQLiteAccessor(schema=schema, conn=self.conn, table=table)

    def get_datasets(self):
        import xedocs

        # xedocs has had a few different public import surfaces for schemas_by_category.
        try:
            from xedocs import schemas_by_category  # type: ignore
        except Exception:  # pragma: no cover
            from xedocs.xedocs import schemas_by_category  # type: ignore

        dsets = {}

        # corrections schemas
        corr = schemas_by_category().get("corrections", {})

        # Also add context configs schema (needed by straxen.apply_xedocs_configs)
        context_cfg_schema = xedocs.find_schema("context_configs")

        schemas = dict(corr)
        schemas["context_configs"] = context_cfg_schema

        for _, schema in schemas.items():
            dsets[schema._ALIAS] = self.data_accessor(schema)

        return Database(dsets)