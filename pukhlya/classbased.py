# -*- coding: utf-8 -*-
#
import sqlalchemy as sa
from aiohttp.web import View
from aiohttp_jinja2 import render_template, template
from aiohttp_session import get_session
from .saform import generate_form
from sqlalchemy import func, select
import sqlalchemy.sql.sqltypes as types
import copy


class AdminListView(View):
    model = None
    search_form = None
    list_columns = None
    views = {}

    async def get(self):
        async with self.request.app["db"].acquire() as conn:
            rows = await conn.fetch(self.model.select().limit(10))
            # self.request.app.router['research.view'].url()

            data = {
                "model": self.model,
                "list_columns": self.list_columns,
                "rows": rows,
                "views": self.views,
            }

            return render_template(
                "pukhlya/list.html", self.request, data, app_key="pukhlya_jinja"
            )

    async def post(self):
        data = await self.request.post()

        return render_template(
            "pukhlya/list.html", self.request, data, app_key="pukhlya_jinja"
        )


class AdminAddView(View):
    model = None
    add_form = None
    views = {}

    async def get(self):
        session = await get_session(self.request)
        form = self.add_form(meta={"csrf_context": session})
        result = {"form": form, "views": self.views}

        return render_template(
            "pukhlya/add.html", self.request, result, app_key="pukhlya_jinja"
        )

    async def post(self):
        session = await get_session(self.request)
        data = await self.request.post()
        form = self.add_form(data, meta={"csrf_context": session})

        result = {"form": form, "views": self.views}

        if form.validate():
            async with self.request.app["db"].acquire() as conn:
                values = {
                    key: form[key].data
                    for key in form._fields.keys()
                    if not key in ["csrf_token",]
                }
                ins = self.model.insert().values(**values)
                await conn.execute(ins)
                result["done"] = True

        return render_template(
            "pukhlya/add.html", self.request, result, app_key="pukhlya_jinja"
        )


def typify(col, val):
    if type(col.type) == types.Integer:
        return int(val)
    return val


class AdminEditView(View):
    model = None
    edit_form = None
    edit_columns = None

    async def get(self):
        async with self.request.app["db"].acquire() as conn:
            session = await get_session(self.request)
            item_id = self.request.match_info["id"]
            item = await conn.fetchrow(
                self.model.select().where(
                    self.model.c.id == typify(self.model.c.id, item_id)
                )
            )
            data = await self.request.post()
            form = self.edit_form(data, item, meta={"csrf_context": session})
            result = {"form": form, "views": self.views, "item_id": item_id}
            return render_template(
                "pukhlya/edit.html", self.request, result, app_key="pukhlya_jinja"
            )

    async def post(self):
        session = await get_session(self.request)
        item_id = self.request.match_info["id"]
        data = await self.request.post()
        form = self.edit_form(data, meta={"csrf_context": session})

        result = {"form": form, "views": self.views, "item_id": item_id}

        if form.validate():
            async with self.request.app["db"].acquire() as conn:
                values = {
                    key: form[key].data
                    for key in form._fields.keys()
                    if not key in ["csrf_token",]
                }
                query = await conn.fetchrow(
                    self.model.update()
                    .returning(self.model.c.id)
                    .where(self.model.c.id == item_id)
                    .values(**values)
                )
                result["done"] = True

        return render_template(
            "pukhlya/edit.html", self.request, result, app_key="pukhlya_jinja"
        )


def admin_register(
    app,
    model,
    prefix="/admin/",
    primary="id",
    list_columns=None,
    search_columns=None,
    edit_columns=None,
    meta=None,
):

    name = model.name
    # names for views
    views = {
        "list": "admin.{}.list".format(name),
        "add": "admin.{}.add".format(name),
        "edit": "admin.{}.edit".format(name),
        "dashboard": "admin.dashboard",
        "breadcrumb": [
            {"title": "Dashboard", "url": "admin.dashboard"},
            {"title": "Список", "url": "admin.{}.list".format(name)},
        ],
    }

    # list form
    search_form = None
    if search_columns:
        search_form = generate_form(model, search_columns)

    list_params = {
        "model": model,
        "search_form": search_form,
        # first 3 columns from table use as list
        "list_columns": list_columns or model.__dict__["columns"].keys()[0:3],
        "views": views,
    }
    list_view = type(
        "Admin{}List".format(model.name.capitalize()), (AdminListView,), list_params
    )
    app.router.add_route(
        "*", "{}{}".format(prefix, name), list_view, name=views["list"]
    )

    add_views = copy.deepcopy(views)
    add_views["breadcrumb"].append(
        {"title": "Добавить", "url": "admin.{}.add".format(name)}
    )

    add_params = {
        "model": model,
        "add_form": generate_form(model, only=edit_columns, meta=meta),
        "add_columns": edit_columns,
        "views": add_views,
    }

    add_view = type(
        "Admin{}Add".format(model.name.capitalize()), (AdminAddView,), add_params
    )
    app.router.add_route(
        "*", "{}{}/add".format(prefix, name), add_view, name=views["add"]
    )

    edit_views = copy.deepcopy(views)
    edit_views["breadcrumb"].append(
        {"title": "Редактировать", "url": "admin.{}.edit".format(name)}
    )

    edit_params = {
        "model": model,
        "edit_form": generate_form(model, only=edit_columns, meta=meta),
        "edit_columns": edit_columns,
        "views": edit_views,
    }

    edit_view = type(
        "Admin{}Edit".format(model.name.capitalize()), (AdminEditView,), edit_params
    )
    app.router.add_route(
        "*", "{}{}/{{id}}".format(prefix, name), edit_view, name=views["edit"]
    )

    # make list of all admin views
    if not app.get("admin"):
        app["admin"] = []
    app["admin"].append((views["list"], model))


@template("pukhlya/dashboard.html", app_key="pukhlya_jinja")
async def admin_dashboard_view(request):
    # TODO: not implemented
    # session = await get_session(request)
    # session['last_visit'] = time.time()
    elements = []
    async with request.app["db"].acquire() as conn:
        for view, model in request.app.get("admin"):
            item = await conn.fetchrow(select([func.count(model.c.id).label("count"),]))
            elements.append({"view": view, "count": item["count"], "name": model.name})
    return {"elements": elements}


def admin_dashboard(app, prefix="/admin/"):
    app.router.add_route("GET", prefix, admin_dashboard_view, name="admin.dashboard")
