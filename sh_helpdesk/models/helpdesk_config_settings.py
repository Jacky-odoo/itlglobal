# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    category = fields.Boolean('Category')
    sub_category = fields.Boolean('Sub Category')
    customer_rating = fields.Boolean('Customer Rating')
    auto_close_ticket = fields.Boolean('Auto Close Ticket')
    close_days = fields.Integer('No of Days')
    new_stage_id = fields.Many2one(
        'helpdesk.stages', string="Draft/New Stage")
    done_stage_id = fields.Many2one('helpdesk.stages', string="Resolved Stage")
    cancel_stage_id = fields.Many2one('helpdesk.stages', string="Cancel Stage")
    allocation_mail_template_id = fields.Many2one(
        'mail.template', string='Ticket Allocation To User Mail Template')
    reply_mail_template_id = fields.Many2one(
        'mail.template', string='Ticket Reply Mail Template')
    dashboard_filter = fields.Many2many(
        'helpdesk.stages', 'rel_company_stage_counter', string="Dashbaord Filter", required=True)
    dashboard_tables = fields.Many2many(
        'helpdesk.stages', 'rel_company_stage_tables', string="Dashbaord Tables", required=True)
    reopen_stage_id = fields.Many2one(
        'helpdesk.stages', string="Re-Opened Stage")
    close_stage_id = fields.Many2one('helpdesk.stages', string="Closed Stage")
    sh_default_team_id = fields.Many2one(
        'helpdesk.team', string="Default Team")
    sh_default_user_id = fields.Many2one(
        'res.users', string="Default Assign User")
    sh_display_multi_user = fields.Boolean('Display Multi Users ?')
    sh_configure_activate = fields.Boolean(
        'Manage Products')
    sh_display_ticket_reminder = fields.Boolean('Ticket Reminder ?')


class HelpdeskSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.company)
    category = fields.Boolean(
        string='Category', related='company_id.category', readonly=False)
    sub_category = fields.Boolean(
        string='Sub Category', related='company_id.sub_category', readonly=False)
    customer_rating = fields.Boolean(
        string='Customer Rating', related='company_id.customer_rating', readonly=False)
    auto_close_ticket = fields.Boolean(
        string='Auto Close Ticket', related='company_id.auto_close_ticket', readonly=False)
    close_days = fields.Integer(
        string='No of Days', related='company_id.close_days', readonly=False)
    new_stage_id = fields.Many2one('helpdesk.stages', string="Draft/New Stage",
                                   related='company_id.new_stage_id', readonly=False)
    done_stage_id = fields.Many2one(
        'helpdesk.stages', string="Resolved Stage", related='company_id.done_stage_id', readonly=False)
    cancel_stage_id = fields.Many2one(
        'helpdesk.stages', string="Cancel Stage", related='company_id.cancel_stage_id', readonly=False)
    allocation_mail_template_id = fields.Many2one(
        'mail.template', string='Ticket Allocation To User Mail Template', related='company_id.allocation_mail_template_id', readonly=False)
    reply_mail_template_id = fields.Many2one(
        'mail.template', string='Ticket Reply Mail Template', related='company_id.reply_mail_template_id', readonly=False)
    dashboard_filter = fields.Many2many('helpdesk.stages', 'rel_company_stage_counter',
                                        string="Dashbaord Filter", related="company_id.dashboard_filter", readonly=False, required=True)
    dashboard_tables = fields.Many2many('helpdesk.stages', 'rel_company_stage_tables',
                                        string="Dashbaord Tables", related="company_id.dashboard_tables", readonly=False, required=True)
    reopen_stage_id = fields.Many2one(
        'helpdesk.stages', string="Re-Opened Stage", readonly=False, related='company_id.reopen_stage_id')
    close_stage_id = fields.Many2one(
        'helpdesk.stages', string="Closed Stage", readonly=False, related='company_id.close_stage_id')
    sh_default_team_id = fields.Many2one(
        'helpdesk.team', string="Default Team", readonly=False, related='company_id.sh_default_team_id')
    sh_default_user_id = fields.Many2one(
        'res.users', string="Default Assign User", readonly=False, related='company_id.sh_default_user_id')
    sh_display_multi_user = fields.Boolean(
        'Display Multi Users ?', related='company_id.sh_display_multi_user', readonly=False)
    sh_configure_activate = fields.Boolean(
        'Manage Products', related='company_id.sh_configure_activate', readonly=False)
    sh_display_ticket_reminder = fields.Boolean('Ticket Reminder ?',related='company_id.sh_display_ticket_reminder',readonly=False)

    @ api.onchange('sh_default_team_id')
    def onchange_sh_default_team_id(self):
        if self.sh_default_team_id:
            domain = {}
            domain = {'sh_default_user_id': [
                ('id', 'in', self.sh_default_team_id.team_members.ids)]}
            return {'domain': domain}
