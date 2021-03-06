# -*- coding: utf-8 -*-

from baseframe import __
import baseframe.forms as forms

__all__ = ['LineItemForm', 'BuyerForm', 'OrderSessionForm']


def truncate(length):
    """
    Return a function that truncates data to the given length.
    To be used as part of the filters argument.
    Eg:
    field = forms.StringField(__("Some field"), filters=[truncate(25)])
    """
    def _inner(data):
        return unicode(data[:length])
    return _inner


class LineItemForm(forms.Form):
    quantity = forms.IntegerField(__("Quantity"), validators=[forms.validators.DataRequired()])
    item_id = forms.StringField(__("Item Id"), validators=[forms.validators.DataRequired()])

    @classmethod
    def process_list(cls, line_items_json):
        """
        Returns a list of LineItemForm objects,
        returns an empty array if validation fails on any object
        """
        line_item_forms = []

        for line_item_dict in line_items_json:
            # Since some requests are cross-domain, other checks
            # have been introduced to ensure against CSRF, such as
            # a white-list of allowed origins and XHR only requests
            line_item_form = cls.from_json(line_item_dict, meta={'csrf': False})
            if not line_item_form.validate():
                return []
            line_item_forms.append(line_item_form)
        return line_item_forms


class BuyerForm(forms.Form):
    email = forms.EmailField(__("Email"), validators=[forms.validators.DataRequired(), forms.validators.Length(max=254)])
    fullname = forms.StringField(__("Full name"), validators=[forms.validators.DataRequired(), forms.validators.Length(max=80)])
    phone = forms.StringField(__("Phone number"), validators=[forms.validators.Length(max=16)])
    company = forms.StringField(__("Company"), validators=[forms.validators.DataRequired(), forms.validators.Length(max=80)])


class OrderSessionForm(forms.Form):
    utm_campaign = forms.StringField(__("UTM Campaign"), filters=[truncate(250)])
    utm_source = forms.StringField(__("UTM Source"), filters=[truncate(250)])
    utm_medium = forms.StringField(__("UTM Medium"), filters=[truncate(250)])
    utm_term = forms.StringField(__("UTM Term"), filters=[truncate(250)])
    utm_content = forms.StringField(__("UTM Content"), filters=[truncate(250)])
    utm_id = forms.StringField(__("UTM Id"), filters=[truncate(250)])
    gclid = forms.StringField(__("Gclid"), filters=[truncate(250)])
    referrer = forms.StringField(__("Referrer"), filters=[truncate(2083)])
