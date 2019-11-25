# -*- coding: utf-8 -*-
#

from datetime import timedelta
from dataclasses import dataclass
from typing import List, Any
import aiohttp_jinja2
import jinja2
from wtforms.csrf.session import SessionCSRF
from .classbased import admin_register, admin_dashboard

__version__ = "0.4.0"

__all__ = ("apply_admin", "register_admin")


@dataclass
class PukhlyaAdmin:
    pk_name: str = "id"
    list_columns: List[str] = None
    search_columns: List[str] = None
    edit_columns: List[str] = None
    model: Any = None


def register_admin(
    model, list_columns=None, search_columns=None, edit_columns=None, pk_name="id"
):
    item = PukhlyaAdmin(
        pk_name=pk_name,
        list_columns=list_columns,
        search_columns=search_columns,
        edit_columns=edit_columns,
        model=model,
    )

    return item


def apply_admin(*, app, config, path="/admin/", secret=None, meta=None):

    aiohttp_jinja2.setup(
        app,
        app_key="pukhlya_jinja",
        loader=jinja2.PackageLoader("pukhlya", "templates"),
    )

    if meta is None:
        assert secret is not None

        class Meta:
            csrf = True
            csrf_secret = secret
            csrf_class = SessionCSRF
            csrf_time_limit = timedelta(minutes=20)

    for item in config:
        assert isinstance(item, PukhlyaAdmin)
        admin_register(
            app,
            item.model,
            prefix=path,
            primary=item.pk_name,
            list_columns=item.list_columns,
            search_columns=item.search_columns,
            edit_columns=item.edit_columns,
            meta=Meta,
        )

    admin_dashboard(app)
