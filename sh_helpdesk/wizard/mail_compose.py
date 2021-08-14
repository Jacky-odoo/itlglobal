# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api
import re


class MailComposeWizard(models.TransientModel):
    _inherit = 'mail.compose.message'

    sh_quick_reply_template_id = fields.Many2one(
        'sh.quick.reply', string='Quick Reply Template')
    body_str = fields.Html('Body')

    @api.onchange('sh_quick_reply_template_id')
    def onchange_sh_quick_reply_template_id(self):
        body_str = self.body
        if not self.body_str:
            self.body_str = body_str
        if not self.sh_quick_reply_template_id:
            self.body = self.body_str
        else:
            if 'div class="predefined"' in body_str:
                tag_1 = 'div class="predefined"'
                tag_2 = "div"
                reg_str = "<" + tag_1 + ">(.*?)</" + tag_2 + ">"
                res = re.findall(reg_str, body_str.strip())
                if len(res) > 0:
                    original_split_str = '<div class="predefined">' + \
                        str(res[0]) + '</div>'
                    original_splited_str = body_str.split(original_split_str)
                    original_joined_str = original_splited_str[0] + \
                        '<div class="predefined"></div>' + \
                        original_splited_str[1]
                    body_str = original_joined_str
                if self.sh_quick_reply_template_id:
                    joined_str = ''
                    splited_str = body_str.split(
                        '<div class="predefined"></div>')
                    if len(splited_str) > 1:
                        joined_str = splited_str[0] + '<div class="predefined">'+str(
                            self.sh_quick_reply_template_id.sh_description) + '</div>'+splited_str[1]
                        self.body = joined_str
                    elif len(splited_str) == 1:
                        joined_str = splited_str[0] + '<div class="predefined">'+str(
                            self.sh_quick_reply_template_id.sh_description) + '</div>'
                        self.body = joined_str
