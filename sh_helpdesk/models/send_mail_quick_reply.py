# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields


class SendQuickReply(models.Model):
    _name = 'sh.quick.reply'
    _description = 'Quick Reply'

    name = fields.Char('Title', required=True)
    sh_user_id = fields.Many2one(
        'res.users', string='User', required=True, default=lambda self: self.env.user.id)
    active = fields.Boolean(default=True)
    sh_description = fields.Html('Body')
