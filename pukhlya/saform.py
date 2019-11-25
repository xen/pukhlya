# -*- coding: utf-8 -*-
#
from collections import OrderedDict

import sqlalchemy as sa
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.sql.schema import Column
from sqlalchemy_utils import types
from wtforms import Form, BooleanField, Field, FloatField, PasswordField, TextAreaField
from wtforms.widgets import CheckboxInput, TextArea
from wtforms_components import (
    ColorField,
    DateField,
    DateIntervalField,
    DateTimeField,
    DateTimeIntervalField,
    DateTimeLocalField,
    DecimalField,
    DecimalIntervalField,
    EmailField,
    IntegerField,
    IntIntervalField,
    SelectField,
    StringField,
    TimeField,
)
from wtforms_components.widgets import (
    ColorInput,
    DateInput,
    DateTimeInput,
    DateTimeLocalInput,
    EmailInput,
    NumberInput,
    TextInput,
    TimeInput,
)


TYPE_MAP = OrderedDict(
    (
        (sa.types.UnicodeText, TextAreaField),
        (sa.types.BigInteger, IntegerField),
        (sa.types.SmallInteger, IntegerField),
        (sa.types.Text, TextAreaField),
        (sa.types.Boolean, BooleanField),
        (sa.types.Date, DateField),
        (sa.types.DateTime, DateTimeField),
        (sa.types.Enum, SelectField),
        (sa.types.Float, FloatField),
        (sa.types.Integer, IntegerField),
        (sa.types.Numeric, DecimalField),
        (sa.types.Unicode, StringField),
        (sa.types.String, StringField),
        (sa.types.Time, TimeField),
        (types.ArrowType, DateTimeField),
        (types.ChoiceType, SelectField),
        (types.ColorType, ColorField),
        (types.DateRangeType, DateIntervalField),
        (types.DateTimeRangeType, DateTimeIntervalField),
        (types.EmailType, EmailField),
        (types.IntRangeType, IntIntervalField),
        (types.NumericRangeType, DecimalIntervalField),
        (types.PasswordType, PasswordField),
        (types.ScalarListType, StringField),
        (types.URLType, StringField),
        (types.UUIDType, StringField),
    )
)

WIDGET_MAP = OrderedDict(
    (
        (BooleanField, CheckboxInput),
        (ColorField, ColorInput),
        (DateField, DateInput),
        (DateTimeField, DateTimeInput),
        (DateTimeLocalField, DateTimeLocalInput),
        (DecimalField, NumberInput),
        (EmailField, EmailInput),
        (FloatField, NumberInput),
        (IntegerField, NumberInput),
        (TextAreaField, TextArea),
        (TimeField, TimeInput),
        (StringField, TextInput),
    )
)


def generate_form(model, only=None, meta=None):
    """
    Generate WTForm based on SQLAlchemy table
    :param model: SQLAlchemy sa.Table
    :param only: list or set of columns that should be used in final form
    :param meta: Meta class with settings for form
    :return: WTForm object
    """
    fields = OrderedDict()
    if meta:
        fields["Meta"] = meta

    for name, column in model.__dict__["columns"].items():
        if only:
            if not name in only:
                continue
        if not isinstance(column, Column):
            continue
        fields[name] = TYPE_MAP[column.type.__class__](
            name, render_kw={"placeholder": name}
        )
    form = type("Add{}Form".format(model.name.capitalize()), (Form,), fields)
    return form


if __name__ == "__main__":
    import sqlalchemy as sa

    meta = sa.MetaData()
    model = sa.Table(
        "tablename",
        meta,
        sa.Column("id", sa.Integer, nullable=False),
        sa.Column("title", sa.String()),
        sa.PrimaryKeyConstraint("id", name="tablename_id_idx"),
    )
    form = generate_form(model)
    print(form)
