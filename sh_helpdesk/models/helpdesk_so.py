# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api, _
import random
import datetime
from odoo.exceptions import UserError
from odoo.tools import email_re


class HelpdeskSO(models.Model):
    _name = 'sh.helpdesk.so'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = "Helpdesk Sale Order"

    


