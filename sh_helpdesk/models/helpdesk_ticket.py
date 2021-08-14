# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api, _
import random
import datetime
from odoo.exceptions import UserError
from odoo.tools import email_re


class HelpdeskSLAStatus(models.Model):
    _name = 'sh.helpdesk.sla.status'
    _description = "Helpdesk Ticket SLA Status"
    _table = 'sh_helpdesk_sla_status'
    _order = 'id ASC'
    _rec_name = 'sh_sla_id'

    sh_ticket_id = fields.Many2one('helpdesk.ticket', string='Ticket', required=True, ondelete='cascade', index=True)
    sh_sla_id = fields.Many2one('sh.helpdesk.sla', required=True, ondelete='cascade')
    sh_sla_stage_id = fields.Many2one('helpdesk.stages', related='sh_sla_id.sh_stage_id', store=True)
    sh_deadline = fields.Datetime("SLA Deadline", compute='_compute_sh_deadline', compute_sudo=True, store=True)
    sh_status = fields.Selection([('sla_failed', 'Failed'), ('sla_passed', 'Passed'), ('sh_partially_passed', 'Partially Passed')], string="Status")
    color = fields.Integer("Color Index", compute='_compute_sh_color')
    sh_done_sla_date = fields.Datetime('SLA Done Date')

    @api.depends('sh_ticket_id.create_date', 'sh_sla_id')
    def _compute_sh_deadline(self):
        for rec in self:
            sla_deadline = rec.sh_ticket_id.create_date
            working_schedule = rec.sh_ticket_id.team_id.sh_resource_calendar_id
            if not working_schedule:
                rec.sh_deadline = sla_deadline
                continue
            if rec.sh_sla_id.sh_days > 0:
                sla_deadline = working_schedule.plan_days(rec.sh_sla_id.sh_days + 1, sla_deadline, compute_leaves=True)
                ticket_create_dt = rec.sh_ticket_id.create_date
                sla_deadline = sla_deadline.replace(hour=ticket_create_dt.hour, minute=ticket_create_dt.minute, second=ticket_create_dt.second, microsecond=ticket_create_dt.microsecond)
            rec.sh_deadline = working_schedule.plan_hours(rec.sh_sla_id.sh_hours, sla_deadline, compute_leaves=True)
    
    @api.depends('sh_status')
    def _compute_sh_color(self):
        for rec in self:
            rec._compute_sh_deadline()
            if rec.sh_status == 'sla_failed':
                rec.color = 1
            elif rec.sh_status == 'sla_passed':
                rec.color = 10
            elif rec.sh_status == 'sh_partially_passed':
                rec.color = 4
            else:
                rec.color = 0


class HelpdeskTicket(models.Model):
    _name = 'helpdesk.ticket'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = "Helpdesk Ticket"
    _rec_name = 'name'

    def get_deafult_company(self):
        company_id = self.env.company
        return company_id

    @api.model
    def get_default_stage(self):
        company_id = self.env.company
        stage_id = self.env['helpdesk.stages'].sudo().search(
            [('id', '=', company_id.new_stage_id.id)], limit=1)
        return stage_id.id
    
    @api.model
    def default_due_date(self):
        return fields.Datetime.now()

    name = fields.Char("Name", tracking=True)
    company_id = fields.Many2one(
        'res.company', string="Company", default=get_deafult_company)
    done_stage_boolean = fields.Boolean(
        'Done Stage', compute='_compute_stage_booleans', store=True)
    cancel_stage_boolean = fields.Boolean(
        'Cancel Stage', compute='_compute_stage_booleans', store=True)
    reopen_stage_boolean = fields.Boolean(
        'Reopened Stage', compute='_compute_stage_booleans', store=True)
    closed_stage_boolean = fields.Boolean(
        'Closed Stage', compute='_compute_stage_booleans', store=True)
    open_boolean = fields.Boolean(
        'Open Ticket', compute='_compute_stage_booleans', store=True)
    cancel_button_boolean = fields.Boolean(
        "Cancel Button", compute='_compute_cancel_button_boolean', store=True)
    done_button_boolean = fields.Boolean(
        "Done Button", compute='_compute_done_button_boolean', store=True)
    state = fields.Selection([('customer_replied', 'Customer Replied'), ('staff_replied', 'Staff Replied')],
                             string="Replied Status", default='customer_replied', required=True, tracking=True)
    active = fields.Boolean(
        'Active', default=True,
        help="If unchecked, it will allow you to hide the product without removing it.")
    ticket_from_website = fields.Boolean('Ticket From Website')
    ticket_from_portal = fields.Boolean('Ticket From Portal')
    cancel_reason = fields.Char("Cancel Reason", tracking=True, translate=True)
    tag_ids = fields.Many2many('helpdesk.tags', string="Tags")
    priority = fields.Many2one(
        'helpdesk.priority', string='Priority', tracking=True)
    stage_id = fields.Many2one('helpdesk.stages', string="Stage",
                               default=get_default_stage, tracking=True)
    ticket_type = fields.Many2one(
        'helpdesk.ticket.type', string='Ticket Type', tracking=True)
    team_id = fields.Many2one(
        'helpdesk.team', string='Team', tracking=True)
    team_head = fields.Many2one(
        'res.users', "Team Head", tracking=True)
    user_id = fields.Many2one(
        'res.users', string="Assigned User", tracking=True)
    subject_id = fields.Many2one(
        'helpdesk.sub.type', string='Ticket Subject Type', tracking=True)
    category_id = fields.Many2one(
        'helpdesk.category', string="Category", tracking=True)
    sub_category_id = fields.Many2one(
        'helpdesk.subcategory', string="Sub Category")
    partner_id = fields.Many2one(
        'res.partner', string='Partner', tracking=True, required=True)
    person_name = fields.Char(string='Person Name',
                              tracking=True)
    email = fields.Char(string='Email', tracking=True)
    close_date = fields.Datetime(
        string='Close Date', tracking=True)
    close_by = fields.Many2one(
        'res.users', string='Closed By', tracking=True)
    cancel_date = fields.Datetime(
        string='Cancelled Date', tracking=True)
    cancel_by = fields.Many2one(
        'res.users', string='Cancelled By', tracking=True)
    replied_date = fields.Datetime('Replied Date', tracking=True)
    product_ids = fields.Many2many('product.product', string='Products')

    comment = fields.Text(string="Comment", tracking=True, translate=True)
    description = fields.Html('Description', tracking=True)
    color = fields.Integer(string='Color Index')
    priority_new = fields.Selection([('1', 'Very Low'), ('2', 'Low'), ('3', 'Normal'), ('4', 'High'), (
        '5', 'Very High'), ('6', 'Excellent')], string="Customer Rating", tracking=True)
    customer_comment = fields.Text(
        "Customer Comment", tracking=True)

    attachment_ids = fields.Many2many('ir.attachment',
                                      string="Attachments")
    form_url = fields.Char('Form Url', compute='_compute_form_url')
    category_bool = fields.Boolean(
        string='Category Setting', related='company_id.category', store=True)
    sub_category_bool = fields.Boolean(
        string='Sub Category Setting', related='company_id.sub_category', store=True)
    rating_bool = fields.Boolean(
        string='Rating Setting', related='company_id.customer_rating', store=True)
    ticket_allocated = fields.Boolean("Allocated")
    sh_user_ids = fields.Many2many('res.users', string="Assign Multi Users")
    sh_display_multi_user = fields.Boolean(
        compute="_compute_sh_display_multi_user")
    sh_display_product = fields.Boolean(compute='_compute_sh_display_product')
    sh_status = fields.Selection([('sla_failed', 'Failed'), ('sla_passed', 'Passed'), ('sh_partially_passed', 'Partially Passed')], string="Status")
    sh_sla_policy_ids = fields.Many2many('sh.helpdesk.sla', 'sh_helpdesk_sla_status', 'sh_ticket_id', 'sh_sla_id', string="Helpdesk SLA Policies", copy=False)
    sh_sla_status_ids = fields.One2many('sh.helpdesk.sla.status', 'sh_ticket_id', string="Helpdesk SLA Status")
    sh_sla_deadline = fields.Datetime('SLA Deadline',compute='_compute_sh_sla_deadline', store=True)
    sh_status_boolean = fields.Boolean(compute='_compute_state_boolean')
    sh_days_to_reach = fields.Float(string='SLA reached duration',compute='_compute_days_to_reach',store=True)
    sh_days_to_late = fields.Float(string='SLA late duration',compute='_compute_days_to_late',store=True)
    sh_due_date = fields.Datetime('Reminder Due Date',default=default_due_date)
    sh_ticket_alarm_ids = fields.Many2many('sh.ticket.alarm',string='Ticket Reminders')

    def _compute_days_to_reach(self):
        if self:
            for rec in self:
                sh_days_to_reach = 0.0
                if rec.sh_sla_status_ids:
                    for line in rec.sh_sla_status_ids: 
                        if line.sh_deadline and line.sh_done_sla_date:
                            delta = line.sh_done_sla_date - line.sh_deadline
                            sh_days_to_reach += delta.days
                rec.sh_days_to_reach = sh_days_to_reach
    
    def _compute_days_to_late(self):
        if self:
            for rec in self:
                sh_days_to_late = 0.0
                if rec.sh_sla_status_ids:
                    for line in rec.sh_sla_status_ids: 
                        if line.sh_deadline and line.sh_done_sla_date:
                            delta = line.sh_done_sla_date - line.sh_deadline
                            sh_days_to_late += delta.days
                rec.sh_days_to_late = sh_days_to_late

    def _compute_state_boolean(self):
        if self:
            for rec in self:
                rec.sh_status_boolean = False
                sla_passed = rec.sh_sla_status_ids.filtered(lambda x: x.sh_status == 'sla_passed')
                sla_failed = rec.sh_sla_status_ids.filtered(lambda x: x.sh_status == 'sla_failed')
                if sla_passed and sla_failed:
                    rec.sh_status = 'sh_partially_passed'
    
    @api.depends('sh_sla_status_ids.sh_deadline')
    def _compute_sh_sla_deadline(self):
        for rec in self:
            sh_deadline = False
            status_ids = rec.sh_sla_status_ids.filtered(lambda x: x.sh_status == False)
            rec.sh_sla_deadline = min(status_ids.mapped('sh_deadline')) if status_ids else sh_deadline
    
    @api.model
    def change_sh_status(self):
        self.ensure_one()
        if self.sh_sla_status_ids:
            for line in self.sh_sla_status_ids:
                if line.sh_sla_id and line.sh_sla_id.sh_sla_target_type == 'reaching_stage':
                    if line.sh_sla_id.sh_stage_id.id == self.stage_id.id:
                        line.sh_done_sla_date = fields.Datetime.now()
                        line.sh_status = False
                        self.sh_status = False
                        if line.sh_done_sla_date and line.sh_deadline:
                            line.sh_status = 'sla_passed' if line.sh_done_sla_date < line.sh_deadline else 'sla_failed'
                            self.sh_status = 'sla_passed' if line.sh_done_sla_date < line.sh_deadline else 'sla_failed'
                        else:
                            line.sh_status = False if (not line.sh_deadline or line.sh_deadline > fields.Datetime.now()) else 'sla_failed'
                            self.sh_status = False if (not line.sh_deadline or line.sh_deadline > fields.Datetime.now()) else 'sla_failed'
                elif line.sh_sla_id and line.sh_sla_id.sh_sla_target_type == 'assign_to':
                    if self.user_id or self.sh_user_ids:
                        line.sh_done_sla_date = fields.Datetime.now()
                        line.sh_status = False
                        self.sh_status = False
                        if line.sh_done_sla_date and line.sh_deadline:
                            line.sh_status = 'sla_passed' if line.sh_done_sla_date < line.sh_deadline else 'sla_failed'
                            self.sh_status = 'sla_passed' if line.sh_done_sla_date < line.sh_deadline else 'sla_failed'
                        else:
                            line.sh_status = False if (not line.sh_deadline or line.sh_deadline > fields.Datetime.now()) else 'sla_failed'
                            self.sh_status = False if (not line.sh_deadline or line.sh_deadline > fields.Datetime.now()) else 'sla_failed'

    @api.onchange('team_id','ticket_type')
    def _onchange_sh_helpdesk_policy_ids(self):
        if self:
            for rec in self:
                rec.sh_sla_policy_ids = [(6,0,rec.helpdesk_sla_create(rec.team_id.id,rec.ticket_type.id))]

    @api.depends('company_id')
    def _compute_sh_display_multi_user(self):
        if self:
            for rec in self:
                rec.sh_display_multi_user = False
                if rec.company_id and rec.company_id.sh_display_multi_user:
                    rec.sh_display_multi_user = True

    @api.depends('company_id')
    def _compute_sh_display_product(self):
        if self:
            for rec in self:
                rec.sh_display_product = False
                if rec.company_id and rec.company_id.sh_configure_activate:
                    rec.sh_display_product = True

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        """ Overrides mail_thread message_new that is called by the mailgateway
            through message_process.
            This override updates the document according to the email.
        """
        defaults = {
            'name':  msg_dict.get('subject') or _("No Subject"),
            'email': msg_dict.get('from'),
            'partner_id': msg_dict.get('author_id', False),
            'description':msg_dict.get('body'),
        }

        return super(HelpdeskTicket, self).message_new(msg_dict, custom_values=defaults)

    def _message_post_after_hook(self, message, msg_vals):
        if self.email and not self.partner_id:
            # we consider that posting a message with a specified recipient (not a follower, a specific one)
            # on a document without customer means that it was created through the chatter using
            # suggested recipients. This heuristic allows to avoid ugly hacks in JS.
            new_partner = message.partner_ids.filtered(
                lambda partner: partner.email == self.email)
            if new_partner:
                self.search([
                    ('partner_id', '=', False),
                    ('email', '=', new_partner.email),
                ]).write({'partner_id': new_partner.id})

        return super(HelpdeskTicket, self)._message_post_after_hook(message, msg_vals)

    def _compute_form_url(self):
        if self:
            base_url = self.env['ir.config_parameter'].sudo(
            ).get_param('web.base.url')
            url_str = ''
            action = self.env.ref('sh_helpdesk.helpdesk_ticket_action').id
            if base_url:
                url_str += str(base_url)+'/web#'
            for rec in self:
                url_str += 'id='+str(rec.id)+'&action='+str(action) + \
                    '&model=helpdesk.ticket&view_type=form'
                rec.form_url = url_str

    def _compute_access_url(self):
        super(HelpdeskTicket, self)._compute_access_url()
        for ticket in self:
            ticket.access_url = '/my/tickets/%s' % (ticket.id)

    def _get_report_base_filename(self):
        self.ensure_one()
        return '%s %s' % ('Ticket', self.name)

    @api.model
    def helpdesk_sla_create(self, team_id, ticket_type):
        self.ensure_one()
        sla_policy_ids_list = []
        if self.sh_sla_status_ids:
            self.sh_sla_status_ids.unlink()
        if team_id:
            sla_policy_ids = self.env['sh.helpdesk.sla'].sudo().search([('sh_team_id','=',team_id)])
            if sla_policy_ids:
                for policy_id in sla_policy_ids:
                    if policy_id.id not in sla_policy_ids_list:
                        sla_policy_ids_list.append(policy_id.id)
        if ticket_type:
            if team_id:
                sla_policy_ids = self.env['sh.helpdesk.sla'].sudo().search([('sh_ticket_type_id','=',ticket_type),('sh_team_id','=',team_id)])
                if sla_policy_ids:
                    for policy_id in sla_policy_ids:
                        if policy_id.id not in sla_policy_ids_list:
                            sla_policy_ids_list.append(policy_id.id)
            elif not team_id:
                sla_policy_ids = self.env['sh.helpdesk.sla'].sudo().search([('sh_ticket_type_id','=',ticket_type)])
                if sla_policy_ids:
                    for policy_id in sla_policy_ids:
                        if policy_id.id not in sla_policy_ids_list:
                            sla_policy_ids_list.append(policy_id.id)
        return sla_policy_ids_list

    @api.model
    def create(self, vals):
        if vals.get('partner_id') == False and vals.get('email', False):
            emails = email_re.findall(vals.get('email') or '')
            email = emails and emails[0] or ''
            name = str(vals.get('email')).split('"')
            partner_id = self.env['res.partner'].create({
                'name': name[1],
                'email': email,
                'company_type': 'person',
            })
            vals.update({
                'partner_id': partner_id.id,
                'email': email,
                'person_name': partner_id.name,
            })
        if self.env.company.sh_default_team_id and not vals.get('team_id') and not vals.get('user_id'):
            vals.update({
                'team_id': self.env.company.sh_default_team_id.id,
                'team_head': self.env.company.sh_default_team_id.team_head.id,
                'user_id': self.env.company.sh_default_user_id.id,
            })
        number = random.randrange(1, 10)
        company_id = self.env.company
        if 'company_id' in vals:
            self = self.with_company(vals['company_id'])
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'helpdesk.ticket') or _('New')
        if company_id.new_stage_id:
            vals['stage_id'] = company_id.new_stage_id.id

        vals['color'] = number
        res = super(HelpdeskTicket, self).create(vals)
        if res.sh_sla_status_ids:
            for line in res.sh_sla_status_ids:
                line.sh_status = res.sh_status
        if res.ticket_from_website and res.company_id.new_stage_id.mail_template_ids and res.partner_id:
            for template in res.company_id.new_stage_id.mail_template_ids:
                template.sudo().send_mail(res.id, force_send=True)
        else:
            if not res.ticket_from_website and res.company_id.new_stage_id.mail_template_ids and res.partner_id:
                for template in res.company_id.new_stage_id.mail_template_ids:
                    template.sudo().send_mail(res.id, force_send=True)
        if res.team_id and res.team_head and res.user_id and res.sh_user_ids:
            allocation_template = res.company_id.allocation_mail_template_id
            email_formatted = []
            if res.team_head.partner_id.email_formatted not in email_formatted:
                email_formatted.append(res.team_head.partner_id.email_formatted)
            if res.user_id.partner_id.email_formatted not in email_formatted:
                email_formatted.append(res.user_id.partner_id.email_formatted)
            for user in res.sh_user_ids:
                if user.id != res.user_id.id:
                    if user.partner_id.email_formatted not in email_formatted: 
                        email_formatted.append(user.partner_id.email_formatted)
            email_formatted_str = ','.join(email_formatted)
            email_values = {'email_from':str(res.team_head.partner_id.email_formatted),'email_to':email_formatted_str}
            if allocation_template:
                allocation_template.sudo().send_mail(res.id, force_send=True,email_values=email_values)
                res.ticket_allocated = True
        elif res.team_id and res.team_head and res.user_id and not res.sh_user_ids:
            allocation_template = res.company_id.allocation_mail_template_id
            email_formatted = []
            if res.team_head.partner_id.email_formatted not in email_formatted: 
                email_formatted.append(res.team_head.partner_id.email_formatted)
            if res.user_id.partner_id.email_formatted not in email_formatted: 
                email_formatted.append(res.user_id.partner_id.email_formatted)
            email_formatted_str = ','.join(email_formatted)
            email_values={'email_from':str(res.team_head.partner_id.email_formatted),'email_to':email_formatted_str}
            if allocation_template:
                allocation_template.sudo().send_mail(res.id, force_send=True,email_values=email_values)
                res.ticket_allocated = True
        elif res.team_id and res.team_head and not res.user_id and res.sh_user_ids:
            allocation_template = res.company_id.allocation_mail_template_id
            email_formatted = []
            for user in res.sh_user_ids:
                if user.partner_id.email_formatted not in email_formatted:
                    email_formatted.append(user.partner_id.email_formatted)
            email_formatted_str = ','.join(email_formatted)
            email_values={'email_from':str(res.team_head.partner_id.email_formatted),'email_to':email_formatted_str}
            if allocation_template:
                allocation_template.sudo().send_mail(res.id, force_send=True,email_values=email_values)
                res.ticket_allocated = True
        elif not res.team_id and not res.team_head and res.user_id and res.sh_user_ids:
            allocation_template = res.company_id.allocation_mail_template_id
            email_formatted = []
            if res.user_id.partner_id.email_formatted not in email_formatted: 
                email_formatted.append(res.user_id.partner_id.email_formatted)
            for user in res.sh_user_ids:
                if user.id != res.user_id.id:
                    if user.partner_id.email_formatted not in email_formatted: 
                        email_formatted.append(user.partner_id.email_formatted)
            email_formatted_str = ','.join(email_formatted)
            email_values={'email_from':str(res.company_id.partner_id.email_formatted),'email_to':email_formatted_str}
            if allocation_template:
                allocation_template.sudo().send_mail(res.id, force_send=True,email_values=email_values)
                res.ticket_allocated = True
        elif not res.team_id and not res.team_head and res.user_id and not res.sh_user_ids:
            allocation_template = res.company_id.allocation_mail_template_id
            allocation_template.sudo().write({
                'email_from': str(res.company_id.partner_id.email_formatted),
                'email_to': str(res.user_id.partner_id.email_formatted),
                'partner_to': str(res.user_id.partner_id.id)
            })
            email_values={'email_from':str(res.company_id.partner_id.email_formatted),'email_to':str(res.user_id.partner_id.email_formatted)}
            if allocation_template:
                allocation_template.sudo().send_mail(res.id, force_send=True,email_values=email_values)
                res.ticket_allocated = True
        elif not res.team_id and not res.team_head and not res.user_id and res.sh_user_ids:
            allocation_template = res.company_id.allocation_mail_template_id
            email_formatted = []
            for user in res.sh_user_ids:
                if user.partner_id.email_formatted not in email_formatted: 
                    email_formatted.append(user.partner_id.email_formatted)
            email_formatted_str = ','.join(email_formatted)
            email_values={'email_from':str(res.company_id.partner_id.email_formatted),'email_to':email_formatted_str}
            if allocation_template:
                allocation_template.sudo().send_mail(res.id, force_send=True,email_values=email_values)
                res.ticket_allocated = True
        res.message_subscribe(partner_ids=res.partner_id.ids)
        return res

    def write(self, vals):
        user_groups = self.env.user.groups_id.ids
        if vals.get('stage_id'):
            stage_id = self.env['helpdesk.stages'].sudo().search(
                [('id', '=', vals.get('stage_id'))], limit=1)
            if stage_id and stage_id.sh_group_ids:
                is_group_exist = False
                list_user_groups = user_groups
                list_stage_groups = stage_id.sh_group_ids.ids
                for item in list_stage_groups:
                    if item in list_user_groups:
                        is_group_exist = True
                        break
                if not is_group_exist:
                    raise UserError(
                        _('You have not access to edit this support request.'))

        if vals.get('partner_id') and self.env.company.new_stage_id.mail_template_ids:
            for rec in self:
                for template in rec.company_id.new_stage_id.mail_template_ids:
                    template.sudo().send_mail(rec.id, force_send=True)
        res = super(HelpdeskTicket, self).write(vals)
        if vals.get('team_id') and vals.get('team_head') and vals.get('user_id') and vals.get('sh_user_ids') and not vals.get('ticket_allocated'):
            allocation_template = self.env.company.allocation_mail_template_id
            team_head = self.env['res.users'].sudo().browse(
                vals.get('team_head'))
            user_id = self.env['res.users'].sudo().browse(vals.get('user_id'))
            email_formatted = []
            if team_head.partner_id.email_formatted not in email_formatted: 
                email_formatted.append(team_head.partner_id.email_formatted)
            if user_id.partner_id.email_formatted not in email_formatted: 
                email_formatted.append(user_id.partner_id.email_formatted)
            users = vals.get('sh_user_ids')[0][2]
            user_ids = self.env['res.users'].sudo().browse(users)
            for user in user_ids:
                if user.id != user_id.id:
                    if user.partner_id.email_formatted not in email_formatted: 
                        email_formatted.append(user.partner_id.email_formatted)
            email_formatted_str = ','.join(email_formatted)
            email_values = {'email_from':str(team_head.partner_id.email_formatted),'email_to':email_formatted_str}
            if allocation_template:
                for rec in self:
                    allocation_template.sudo().send_mail(rec.id, force_send=True,email_values=email_values)
                    rec.ticket_allocated = True
        elif vals.get('team_id') and vals.get('team_head') and vals.get('user_id') and not vals.get('sh_user_ids') and not vals.get('ticket_allocated'):
            allocation_template = self.env.company.allocation_mail_template_id
            team_head = self.env['res.users'].sudo().browse(
                vals.get('team_head'))
            user_id = self.env['res.users'].sudo().browse(vals.get('user_id'))
            email_formatted = []
            if team_head.partner_id.email_formatted not in email_formatted: 
                email_formatted.append(team_head.partner_id.email_formatted)
            if user_id.partner_id.email_formatted not in email_formatted: 
                email_formatted.append(user_id.partner_id.email_formatted)
            email_formatted_str = ','.join(email_formatted)
            email_values = {'email_from':str(team_head.partner_id.email_formatted),'email_to':email_formatted_str}
            if allocation_template:
                for rec in self:
                    allocation_template.sudo().send_mail(rec.id, force_send=True,email_values=email_values)
                    rec.ticket_allocated = True
        elif vals.get('team_id') and vals.get('team_head') and not vals.get('user_id') and vals.get('sh_user_ids') and not vals.get('ticket_allocated'):
            allocation_template = self.env.company.allocation_mail_template_id
            email_formatted = []
            users = vals.get('sh_user_ids')[0][2]
            user_ids = self.env['res.users'].sudo().browse(users)
            team_head = self.env['res.users'].sudo().browse(
                vals.get('team_head'))
            for user in user_ids:
                if user.partner_id.email_formatted not in email_formatted: 
                    email_formatted.append(user.partner_id.email_formatted)
            email_formatted_str = ','.join(email_formatted)
            email_values={'email_from':str(team_head.partner_id.email_formatted),'email_to':email_formatted_str}
            if allocation_template:
                for rec in self:
                    allocation_template.sudo().send_mail(rec.id, force_send=True,email_values=email_values)
                    rec.ticket_allocated = True
        elif not vals.get('team_id') and not vals.get('team_head') and vals.get('user_id') and vals.get('sh_user_ids') and not vals.get('ticket_allocated'):
            allocation_template = self.env.company.allocation_mail_template_id
            email_formatted = []
            user_id = self.env['res.users'].sudo().browse(vals.get('user_id'))
            users = vals.get('sh_user_ids')[0][2]
            user_ids = self.env['res.users'].sudo().browse(users)
            if user_id.partner_id.email_formatted not in email_formatted: 
                email_formatted.append(user_id.partner_id.email_formatted)
            for user in user_ids:
                if user.id != user_id.id:
                    if user.partner_id.email_formatted not in email_formatted: 
                        email_formatted.append(user.partner_id.email_formatted)
            email_formatted_str = ','.join(email_formatted)
            email_values={'email_from':str(self.env.company.partner_id.email_formatted),'email_to':email_formatted_str}
            if allocation_template:
                for rec in self:
                    allocation_template.sudo().send_mail(rec.id, force_send=True,email_values=email_values)
                    rec.ticket_allocated = True
        elif not vals.get('team_id') and not vals.get('team_head') and vals.get('user_id') and not vals.get('sh_user_ids') and not vals.get('ticket_allocated'):
            allocation_template = self.env.company.allocation_mail_template_id
            user_id = self.env['res.users'].sudo().browse(vals.get('user_id'))
            email_values = {'email_from':str(self.env.company.partner_id.email_formatted),'email_to':str(user_id.partner_id.email_formatted)}
            if allocation_template:
                for rec in self:
                    allocation_template.sudo().send_mail(rec.id, force_send=True,email_values=email_values)
                    rec.ticket_allocated = True
        elif not vals.get('team_id') and not vals.get('team_head') and not vals.get('user_id') and vals.get('sh_user_ids') and not vals.get('ticket_allocated'):
            allocation_template = self.env.company.allocation_mail_template_id
            users = vals.get('sh_user_ids')[0][2]
            user_ids = self.env['res.users'].sudo().browse(users)
            email_formatted = []
            for user in user_ids:
                if user.partner_id.email_formatted not in email_formatted: 
                    email_formatted.append(user.partner_id.email_formatted)
            email_formatted_str = ','.join(email_formatted)
            email_values={'email_from':str(self.env.company.partner_id.email_formatted),'email_to':email_formatted_str}
            if allocation_template:
                for rec in self:
                    allocation_template.sudo().send_mail(rec.id, force_send=True,email_values=email_values)
                    rec.ticket_allocated = True
        return res

    def preview_ticket(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url(),
        }

    @api.depends('stage_id')
    def _compute_stage_booleans(self):
        if self:
            for rec in self:
                rec.cancel_stage_boolean = False
                rec.done_stage_boolean = False
                rec.reopen_stage_boolean = False
                rec.closed_stage_boolean = False
                rec.open_boolean = False
                if rec.stage_id.id == rec.company_id.cancel_stage_id.id:
                    rec.cancel_stage_boolean = True
                    rec.open_boolean = True
                elif rec.stage_id.id == rec.company_id.done_stage_id.id:
                    rec.done_stage_boolean = True
                    rec.open_boolean = True
                elif rec.stage_id.id == rec.company_id.reopen_stage_id.id:
                    rec.reopen_stage_boolean = True
                    rec.open_boolean = False
                elif rec.stage_id.id == rec.company_id.close_stage_id.id:
                    rec.closed_stage_boolean = True
                    rec.open_boolean = True

    @api.depends('stage_id')
    def _compute_cancel_button_boolean(self):
        if self:
            for rec in self:
                rec.cancel_button_boolean = False
                if rec.stage_id.is_cancel_button_visible:
                    rec.cancel_button_boolean = True

    @api.depends('stage_id')
    def _compute_done_button_boolean(self):
        if self:
            for rec in self:
                rec.done_button_boolean = False
                if rec.stage_id.is_done_button_visible:
                    rec.done_button_boolean = True

    def action_approve(self):
        self.ensure_one()
        if self.stage_id.sh_next_stage:
            self.stage_id = self.stage_id.sh_next_stage.id
            self.change_sh_status()
            self._compute_sh_sla_deadline()
            if self.stage_id.mail_template_ids:
                for template in self.stage_id.mail_template_ids:
                    template.sudo().send_mail(self.id, force_send=True)

    def aciton_draft(self):
        self.ensure_one()
        if self.company_id and self.company_id.new_stage_id:
            self.stage_id = self.company_id.new_stage_id.id

    def action_done(self):
        self.ensure_one()
        if self.company_id and self.company_id.done_stage_id and self.company_id.done_stage_id.mail_template_ids:
            for template in self.company_id.done_stage_id.mail_template_ids:
                template.sudo().send_mail(self.id, force_send=True)
            self.stage_id = self.company_id.done_stage_id.id

    def action_reply(self):
        self.ensure_one()
        self.write({'replied_date': datetime.datetime.now(),
                    'state': 'staff_replied'})
        ir_model_data = self.env['ir.model.data']
        template_id = self.company_id.reply_mail_template_id.id
        try:
            compose_form_id = ir_model_data.get_object_reference(
                'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'helpdesk.ticket',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def action_closed(self):
        self.ensure_one()
        if self.company_id and self.company_id.close_stage_id and self.company_id.close_stage_id.mail_template_ids:
            for template in self.company_id.close_stage_id.mail_template_ids:
                template.sudo().send_mail(self.id, force_send=True)
        self.write({'close_date': datetime.datetime.now(), 'close_by': self.env.user.id,
                    'closed_stage_boolean': True, 'stage_id': self.company_id.close_stage_id.id})

    def action_cancel(self):
        self.ensure_one()
        if self.company_id and self.company_id.cancel_stage_id and self.company_id.cancel_stage_id.mail_template_ids:
            for template in self.company_id.cancel_stage_id.mail_template_ids:
                template.sudo().send_mail(self.id, force_send=True)
        stage_id = self.company_id.cancel_stage_id
        self.stage_id = stage_id.id
        self.cancel_date = datetime.datetime.now()
        self.cancel_by = self.env.user.id
        self.cancel_stage_boolean = True

    def action_open(self):
        if self.company_id and self.company_id.reopen_stage_id and self.company_id.reopen_stage_id.mail_template_ids:
            for template in self.company_id.reopen_stage_id.mail_template_ids:
                template.sudo().send_mail(self.id, force_send=True)
        self.write({
            'stage_id': self.company_id.reopen_stage_id.id,
            'open_boolean': True,
        })

    @api.onchange('team_id')
    def onchange_team(self):
        if self.team_id:
            self.team_head = self.team_id.team_head
            user_ids = self.env['helpdesk.team'].sudo().search(
                [('id', '=', self.team_id.id)])
            return {'domain': {'user_id': [('id', 'in', user_ids.team_members.ids)], 'sh_user_ids': [('id', 'in', user_ids.team_members.ids)]}}
        else:
            self.team_head = False

    @api.onchange('category_id')
    def onchange_category(self):
        if self.category_id:
            sub_category_ids = self.env['helpdesk.subcategory'].sudo().search(
                [('parent_category_id', '=', self.category_id.id)]).ids
            return {'domain': {'sub_category_id': [('id', 'in', sub_category_ids)]}}
        else:
            self.sub_category_id = False

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            self.person_name = self.partner_id.name
            self.email = self.partner_id.email
        else:
            self.person_name = False
            self.email = False

    @api.model
    def _run_auto_close_ticket(self):
        tikcet_ids = self.env['helpdesk.ticket'].sudo().search(
            [('done_stage_boolean', '=', False), ('cancel_stage_boolean', '=', False)])
        for ticket in tikcet_ids:
            create_date = ticket.create_date.date()
            if ticket.company_id.auto_close_ticket:
                no_of_days = ticket.company_id.close_days
                end_date = create_date + datetime.timedelta(days=no_of_days)
                if end_date == fields.Date.today():
                    ticket.sudo().write({
                        'done_stage_boolean': True,
                        'stage_id': ticket.company_id.done_stage_id.id,
                    })
