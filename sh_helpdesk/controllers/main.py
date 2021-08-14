# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import http
from odoo.http import request
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class HelpdeskTicketFeedbackController(http.Controller):

    @http.route('/ticket/feedback/<ticket_id>', type="http", auth="public", website=True)
    def helpdesk_ticket_feedback(self, ticket_id, **kw):
        return http.request.render('sh_helpdesk.helpdesk_ticket_feedback_page', {'ticket': ticket_id})

    @http.route('/helpdesk/ticket/feedback/<ticket_id>', type="http", auth="public", website=True, csrf=False)
    def helpdesk_ticket_feedback_thanks(self, ticket_id, **kw):
        dic = {}
        if kw.get('smiley') != '':
            dic.update({
                'priority_new': kw.get('smiley'),
            })
        if kw.get('comment') != '':
            dic.update({
                'customer_comment': kw.get('comment'),
            })
        ticket = request.env['helpdesk.ticket'].sudo().search(
            [('id', '=', int(ticket_id))], limit=1)
        if ticket:
            ticket.sudo().write(dic)
        return http.request.render('sh_helpdesk.ticket_feedback_thank_you', {})

    @http.route('/get_team', type='http', auth="public")
    def team_data(self):

        team_obj = request.env['helpdesk.team'].sudo().search([])
        res_list = {}

        for rec in team_obj:
            res = {}
            res.update({'name': rec.name})
            res_list.update({rec.id: res})
        return json.dumps(res_list)

    @http.route('/get_team_leader', type='http', auth="public")
    def get_team_leader_data(self):
        user_obj = request.env['res.users'].sudo().search([])
        res_list = {}

        for rec in user_obj:
            res = {}
            res.update({'name': rec.name})
            res_list.update({rec.id: res})
        return json.dumps(res_list)

    @http.route([
        '/get-leader-user',
    ], type='http', auth="public", method="post", website=True, csrf=False)
    def get_data(self, **post):
        dic = {}
        if int(post.get('team_leader')) != 0:
            team_ids = request.env['helpdesk.team'].sudo().search(
                [('team_head', '=', int(post.get('team_leader')))])
            for rec in team_ids:
                res = {}
                res.update({'name': rec.name})
                dic.update({rec.id: res})
        return json.dumps(dic)

    @http.route([
        '/user-group',
    ], type='http', auth="public", method="post", website=True, csrf=False)
    def get_user_group(self, **post):
        dic = {}
        support_user = request.env.user.has_group(
            'sh_helpdesk.helpdesk_group_user')
        team_leader = request.env.user.has_group(
            'sh_helpdesk.helpdesk_group_team_leader')
        manager = request.env.user.has_group(
            'sh_helpdesk.helpdesk_group_manager')
        if support_user and not team_leader and not manager:
            dic.update({
                'user': '1'
            })
        elif support_user and team_leader and not manager:
            dic.update({
                'leader': '1'
            })
        elif support_user and team_leader and manager:
            dic.update({
                'manager': '1'
            })
        return json.dumps(dic)

    @http.route([
        '/get-user',
    ], type='http', auth="public", method="post", website=True, csrf=False)
    def get_user(self, **post):
        dic = {}
        if int(post.get('team')) != 0:
            team_id = request.env['helpdesk.team'].sudo().search(
                [('id', '=', int(post.get('team')))])
            for rec in team_id.team_members:
                res = {}
                res.update({'name': rec.name})
                dic.update({rec.id: res})
        return json.dumps(dic)

    @http.route(
        '/get-ticket-counter-data', type='http', auth="public")
    def get_ticket_counter_data(self, **kw):
        ticket_obj = request.env['helpdesk.ticket'].sudo().search(
            [], order='id desc', limit=1)
        company_id = request.env.company
        ticket_data_dic = {}
        ticket_data_list = []
        id_list = []
        data_dict = {}
        for stage in company_id.dashboard_filter:
            doman = []
            id_list = []
            if kw.get('filter_date') == 'today':

                dt_flt1 = []
                dt_flt1.append('create_date')
                dt_flt1.append('>')
                dt_flt1.append(
                    datetime.now().date().strftime("%Y/%m/%d 00:00:00"))
                doman.append(tuple(dt_flt1))

                dt_flt2 = []
                dt_flt2.append('create_date')
                dt_flt2.append('<=')
                dt_flt2.append(
                    datetime.now().date().strftime("%Y/%m/%d 23:59:59"))
                doman.append(tuple(dt_flt2))

            elif kw.get('filter_date') == 'yesterday':

                dt_flt1 = []
                dt_flt1.append('create_date')
                dt_flt1.append('>')
                prev_day = (datetime.now().date() -
                            relativedelta(days=1)).strftime('%Y/%m/%d 00:00:00')
                dt_flt1.append(prev_day)
                doman.append(tuple(dt_flt1))

                dt_flt2 = []
                dt_flt2.append('create_date')
                dt_flt2.append('<=')
                prev_day = (datetime.now().date() -
                            relativedelta(days=1)).strftime('%Y/%m/%d 23:59:59')
                dt_flt2.append(prev_day)
                doman.append(tuple(dt_flt2))

            elif kw.get('filter_date') == 'weekly':  # current week

                dt_flt1 = []
                dt_flt1.append('create_date')
                dt_flt1.append('>')
                dt_flt1.append((datetime.now().date(
                ) - relativedelta(weeks=1, weekday=0)).strftime("%Y/%m/%d 00:00:00"))
                doman.append(tuple(dt_flt1))

                dt_flt2 = []
                dt_flt2.append('create_date')
                dt_flt2.append('<=')
                dt_flt2.append(
                    datetime.now().date().strftime("%Y/%m/%d 23:59:59"))
                doman.append(tuple(dt_flt2))

            elif kw.get('filter_date') == 'prev_week':  # Previous week

                dt_flt1 = []
                dt_flt1.append('create_date')
                dt_flt1.append('>')
                dt_flt1.append((datetime.now().date(
                ) - relativedelta(weeks=2, weekday=0)).strftime("%Y/%m/%d 00:00:00"))
                doman.append(tuple(dt_flt1))

                dt_flt2 = []
                dt_flt2.append('create_date')
                dt_flt2.append('<=')
                dt_flt2.append((datetime.now().date(
                ) - relativedelta(weeks=1, weekday=6)).strftime("%Y/%m/%d 23:59:59"))
                doman.append(tuple(dt_flt2))

            elif kw.get('filter_date') == 'monthly':  # Current Month

                dt_flt1 = []
                dt_flt1.append('create_date')
                dt_flt1.append('>')
                dt_flt1.append(
                    (datetime.now().date()).strftime("%Y/%m/01 00:00:00"))
                doman.append(tuple(dt_flt1))

                dt_flt2 = []
                dt_flt2.append('create_date')
                dt_flt2.append('<=')
                dt_flt2.append(
                    datetime.now().date().strftime("%Y/%m/%d 23:59:59"))
                doman.append(tuple(dt_flt2))

            elif kw.get('filter_date') == 'prev_month':  # Previous Month

                dt_flt1 = []
                dt_flt1.append('create_date')
                dt_flt1.append('>')
                dt_flt1.append(
                    (datetime.now().date() - relativedelta(months=1)).strftime("%Y/%m/01 00:00:00"))
                doman.append(tuple(dt_flt1))

                dt_flt2 = []
                dt_flt2.append('create_date')
                dt_flt2.append('<')
                dt_flt2.append(
                    datetime.now().date().strftime("%Y/%m/01 00:00:00"))
                doman.append(tuple(dt_flt2))

            elif kw.get('filter_date') == 'cur_year':  # Current Year

                dt_flt1 = []
                dt_flt1.append('create_date')
                dt_flt1.append('>')
                dt_flt1.append(
                    (datetime.now().date()).strftime("%Y/01/01 00:00:00"))
                doman.append(tuple(dt_flt1))

                dt_flt2 = []
                dt_flt2.append('create_date')
                dt_flt2.append('<=')
                dt_flt2.append(
                    datetime.now().date().strftime("%Y/%m/%d 23:59:59"))
                doman.append(tuple(dt_flt2))

            elif kw.get('filter_date') == 'prev_year':  # Previous Year

                dt_flt1 = []
                dt_flt1.append('create_date')
                dt_flt1.append('>')
                dt_flt1.append(
                    (datetime.now().date() - relativedelta(years=1)).strftime("%Y/01/01 00:00:00"))
                doman.append(tuple(dt_flt1))

                dt_flt2 = []
                dt_flt2.append('create_date')
                dt_flt2.append('<')
                dt_flt2.append(
                    datetime.now().date().strftime("%Y/01/01 00:00:00"))
                doman.append(tuple(dt_flt2))
            elif kw.get('filter_date') == 'custom':
                if kw.get('date_start') and kw.get('date_end'):
                    dt_flt1 = []
                    dt_flt1.append('create_date')
                    dt_flt1.append('>=')
                    dt_flt1.append(datetime.strptime(
                        str(kw.get('date_start')), DEFAULT_SERVER_DATE_FORMAT).strftime("%Y/%m/%d"))
                    doman.append(tuple(dt_flt1))

                    dt_flt2 = []
                    dt_flt2.append('create_date')
                    dt_flt2.append('<=')
                    dt_flt2.append(datetime.strptime(
                        str(kw.get('date_end')), DEFAULT_SERVER_DATE_FORMAT).strftime("%Y/%m/%d"))
                    doman.append(tuple(dt_flt2))
            if int(kw.get('team')) != 0:
                doman.append(('team_id', '=', int(kw.get('team'))))
            elif int(kw.get('team')) == 0:
                if request.env.user.has_group('sh_helpdesk.helpdesk_group_team_leader') and request.env.user.has_group('sh_helpdesk.helpdesk_group_user') and not request.env.user.has_group('sh_helpdesk.helpdesk_group_manager'):
                    team_ids = request.env['helpdesk.team'].sudo().search(
                        ['|', ('team_head', '=', request.env.user.id), ('team_members', 'in', [request.env.user.id])])
                    doman.append(('team_id', 'in', team_ids.ids))
                elif not request.env.user.has_group('sh_helpdesk.helpdesk_group_team_leader') and request.env.user.has_group('sh_helpdesk.helpdesk_group_user') and not request.env.user.has_group('sh_helpdesk.helpdesk_group_manager'):
                    team_ids = request.env['helpdesk.team'].sudo().search(
                        [('team_members', 'in', [request.env.user.id])])
                    doman.append(('team_id', 'in', team_ids.ids))

            if int(kw.get('team_leader')) != 0:
                doman.append(('team_head', '=', int(kw.get('team_leader'))))
            elif int(kw.get('team_leader')) == 0:
                if request.env.user.has_group('sh_helpdesk.helpdesk_group_team_leader') and request.env.user.has_group('sh_helpdesk.helpdesk_group_user') and not request.env.user.has_group('sh_helpdesk.helpdesk_group_manager'):
                    doman.append(('|'))
                    doman.append(('|'))
                    doman.append(('team_head', '=', request.env.user.id))
                    doman.append(('user_id', '=', request.env.user.id))
                    doman.append(('sh_user_ids', 'in', [request.env.user.id]))
            if int(kw.get('user_id')) != 0:
                doman.append(('|'))
                doman.append(('user_id', '=', int(kw.get('user_id'))))
                doman.append(('sh_user_ids', 'in', [int(kw.get('user_id'))]))
            elif int(kw.get('user_id')) == 0:
                if request.env.user.has_group('sh_helpdesk.helpdesk_group_team_leader') and request.env.user.has_group('sh_helpdesk.helpdesk_group_user') and not request.env.user.has_group('sh_helpdesk.helpdesk_group_manager'):
                    doman.append(('|'))
                    doman.append(('|'))
                    doman.append(('sh_user_ids', 'in', [request.env.user.id]))
                    doman.append(('user_id', '=', request.env.user.id))
                    doman.append(('team_head', '=', request.env.user.id))
                elif not request.env.user.has_group('sh_helpdesk.helpdesk_group_team_leader') and request.env.user.has_group('sh_helpdesk.helpdesk_group_user') and not request.env.user.has_group('sh_helpdesk.helpdesk_group_manager'):
                    doman.append(('|'))
                    doman.append(('user_id', '=', request.env.user.id))
                    doman.append(('sh_user_ids', 'in', [request.env.user.id]))
            ticket_list = []
            doman.append(('stage_id', '=', stage.id))
            search_tickets = ticket_obj.sudo().search(doman)
            if search_tickets:
                for ticket in search_tickets:
                    ticket_dic = {
                        'ticket_id': ticket.id,
                        'ticket_no': ticket.name,
                        'partner_id': ticket.partner_id.name,
                        'create_date': str(ticket.create_date),
                        'write_date': str(ticket.write_date),
                        'user_id': ticket.user_id.name,
                    }
                    ticket_list.append(ticket_dic)
                    id_list.append(ticket.id)
            search_stage = request.env['helpdesk.stages'].sudo().search([
                ('id', '=', stage.id)
            ], limit=1)
            if search_stage:
                ticket_data_dic.update({search_stage.name: ticket_list})
                list_ids = [id_list]
                data_dict.update({search_stage.name: list_ids})
                ticket_data_list.append(search_stage.name)
        return request.env['ir.ui.view'].with_context()._render_template('sh_helpdesk.ticket_dashboard_count', {
            'ticket_data_dic': ticket_data_dic,
            'ticket_data_list': ticket_data_list,
            'data_dict': data_dict,
        })

    @http.route([
        '/open-ticket',
    ], type='http', auth="public", method="post", website=True, csrf=False)
    def open_tickets(self, **kw):
        dashboard_id = request.env['ticket.dashboard'].sudo().search(
            [('id', '=', 1)], limit=1)
        dashboard_id.get_ticket_data(kw.get('ids'))
        dic = {}
        dic.update({'success': 1})
        return json.dumps(dic)

    @http.route(
        '/get-ticket-table-data', type='http', auth="public")
    def get_ticket_table_data(self, **kw):
        ticket_obj = request.env['helpdesk.ticket'].sudo().search(
            [], order='id desc', limit=1)
        company_id = request.env.company
        ticket_data_dic = {}
        ticket_data_list = []
        for stage in company_id.dashboard_tables:
            doman = []
            if kw.get('filter_date') == 'today':

                dt_flt1 = []
                dt_flt1.append('create_date')
                dt_flt1.append('>')
                dt_flt1.append(
                    datetime.now().date().strftime("%Y/%m/%d 00:00:00"))
                doman.append(tuple(dt_flt1))

                dt_flt2 = []
                dt_flt2.append('create_date')
                dt_flt2.append('<=')
                dt_flt2.append(
                    datetime.now().date().strftime("%Y/%m/%d 23:59:59"))
                doman.append(tuple(dt_flt2))

            elif kw.get('filter_date') == 'yesterday':

                dt_flt1 = []
                dt_flt1.append('create_date')
                dt_flt1.append('>')
                prev_day = (datetime.now().date() -
                            relativedelta(days=1)).strftime('%Y/%m/%d 00:00:00')
                dt_flt1.append(prev_day)
                doman.append(tuple(dt_flt1))

                dt_flt2 = []
                dt_flt2.append('create_date')
                dt_flt2.append('<=')
                prev_day = (datetime.now().date() -
                            relativedelta(days=1)).strftime('%Y/%m/%d 23:59:59')
                dt_flt2.append(prev_day)
                doman.append(tuple(dt_flt2))

            elif kw.get('filter_date') == 'weekly':  # current week

                dt_flt1 = []
                dt_flt1.append('create_date')
                dt_flt1.append('>')
                dt_flt1.append((datetime.now().date(
                ) - relativedelta(weeks=1, weekday=0)).strftime("%Y/%m/%d 00:00:00"))
                doman.append(tuple(dt_flt1))

                dt_flt2 = []
                dt_flt2.append('create_date')
                dt_flt2.append('<=')
                dt_flt2.append(
                    datetime.now().date().strftime("%Y/%m/%d 23:59:59"))
                doman.append(tuple(dt_flt2))

            elif kw.get('filter_date') == 'prev_week':  # Previous week

                dt_flt1 = []
                dt_flt1.append('create_date')
                dt_flt1.append('>')
                dt_flt1.append((datetime.now().date(
                ) - relativedelta(weeks=2, weekday=0)).strftime("%Y/%m/%d 00:00:00"))
                doman.append(tuple(dt_flt1))

                dt_flt2 = []
                dt_flt2.append('create_date')
                dt_flt2.append('<=')
                dt_flt2.append((datetime.now().date(
                ) - relativedelta(weeks=1, weekday=6)).strftime("%Y/%m/%d 23:59:59"))
                doman.append(tuple(dt_flt2))

            elif kw.get('filter_date') == 'monthly':  # Current Month

                dt_flt1 = []
                dt_flt1.append('create_date')
                dt_flt1.append('>')
                dt_flt1.append(
                    (datetime.now().date()).strftime("%Y/%m/01 00:00:00"))
                doman.append(tuple(dt_flt1))

                dt_flt2 = []
                dt_flt2.append('create_date')
                dt_flt2.append('<=')
                dt_flt2.append(
                    datetime.now().date().strftime("%Y/%m/%d 23:59:59"))
                doman.append(tuple(dt_flt2))

            elif kw.get('filter_date') == 'prev_month':  # Previous Month

                dt_flt1 = []
                dt_flt1.append('create_date')
                dt_flt1.append('>')
                dt_flt1.append(
                    (datetime.now().date() - relativedelta(months=1)).strftime("%Y/%m/01 00:00:00"))
                doman.append(tuple(dt_flt1))

                dt_flt2 = []
                dt_flt2.append('create_date')
                dt_flt2.append('<')
                dt_flt2.append(
                    datetime.now().date().strftime("%Y/%m/01 00:00:00"))
                doman.append(tuple(dt_flt2))

            elif kw.get('filter_date') == 'cur_year':  # Current Year

                dt_flt1 = []
                dt_flt1.append('create_date')
                dt_flt1.append('>')
                dt_flt1.append(
                    (datetime.now().date()).strftime("%Y/01/01 00:00:00"))
                doman.append(tuple(dt_flt1))

                dt_flt2 = []
                dt_flt2.append('create_date')
                dt_flt2.append('<=')
                dt_flt2.append(
                    datetime.now().date().strftime("%Y/%m/%d 23:59:59"))
                doman.append(tuple(dt_flt2))

            elif kw.get('filter_date') == 'prev_year':  # Previous Year

                dt_flt1 = []
                dt_flt1.append('create_date')
                dt_flt1.append('>')
                dt_flt1.append(
                    (datetime.now().date() - relativedelta(years=1)).strftime("%Y/01/01 00:00:00"))
                doman.append(tuple(dt_flt1))

                dt_flt2 = []
                dt_flt2.append('create_date')
                dt_flt2.append('<')
                dt_flt2.append(
                    datetime.now().date().strftime("%Y/01/01 00:00:00"))
                doman.append(tuple(dt_flt2))
            elif kw.get('filter_date') == 'custom':
                if kw.get('date_start') and kw.get('date_end'):
                    dt_flt1 = []
                    dt_flt1.append('create_date')
                    dt_flt1.append('>=')
                    dt_flt1.append(datetime.strptime(
                        str(kw.get('date_start')), DEFAULT_SERVER_DATE_FORMAT).strftime("%Y/%m/%d"))
                    doman.append(tuple(dt_flt1))

                    dt_flt2 = []
                    dt_flt2.append('create_date')
                    dt_flt2.append('<=')
                    dt_flt2.append(datetime.strptime(
                        str(kw.get('date_end')), DEFAULT_SERVER_DATE_FORMAT).strftime("%Y/%m/%d"))
                    doman.append(tuple(dt_flt2))
            if int(kw.get('team')) != 0:
                doman.append(('team_id', '=', int(kw.get('team'))))
            elif int(kw.get('team')) == 0:
                if request.env.user.has_group('sh_helpdesk.helpdesk_group_team_leader') and request.env.user.has_group('sh_helpdesk.helpdesk_group_user') and not request.env.user.has_group('sh_helpdesk.helpdesk_group_manager'):
                    team_ids = request.env['helpdesk.team'].sudo().search(
                        ['|', ('team_head', '=', request.env.user.id), ('team_members', 'in', [request.env.user.id])])
                    doman.append(('team_id', 'in', team_ids.ids))
                elif not request.env.user.has_group('sh_helpdesk.helpdesk_group_team_leader') and request.env.user.has_group('sh_helpdesk.helpdesk_group_user') and not request.env.user.has_group('sh_helpdesk.helpdesk_group_manager'):
                    team_ids = request.env['helpdesk.team'].sudo().search(
                        [('team_members', 'in', [request.env.user.id])])
                    doman.append(('team_id', 'in', team_ids.ids))
            if int(kw.get('team_leader')) != 0:
                doman.append(('team_head', '=', int(kw.get('team_leader'))))
            elif int(kw.get('team_leader')) == 0:
                if request.env.user.has_group('sh_helpdesk.helpdesk_group_team_leader') and request.env.user.has_group('sh_helpdesk.helpdesk_group_user') and not request.env.user.has_group('sh_helpdesk.helpdesk_group_manager'):
                    doman.append(('|'))
                    doman.append(('|'))
                    doman.append(('team_head', '=', request.env.user.id))
                    doman.append(('user_id', '=', request.env.user.id))
                    doman.append(('sh_user_ids', 'in', [request.env.user.id]))
            if int(kw.get('user_id')) != 0:
                doman.append(('|'))
                doman.append(('user_id', '=', int(kw.get('user_id'))))
                doman.append(('sh_user_ids', 'in', [int(kw.get('user_id'))]))
            elif int(kw.get('user_id')) == 0:
                if request.env.user.has_group('sh_helpdesk.helpdesk_group_team_leader') and request.env.user.has_group('sh_helpdesk.helpdesk_group_user') and not request.env.user.has_group('sh_helpdesk.helpdesk_group_manager'):
                    doman.append(('|'))
                    doman.append(('|'))
                    doman.append(('user_id', '=', request.env.user.id))
                    doman.append(('sh_user_ids', 'in', [request.env.user.id]))
                    doman.append(('team_head', '=', request.env.user.id))
                elif not request.env.user.has_group('sh_helpdesk.helpdesk_group_team_leader') and request.env.user.has_group('sh_helpdesk.helpdesk_group_user') and not request.env.user.has_group('sh_helpdesk.helpdesk_group_manager'):
                    doman.append(('|'))
                    doman.append(('user_id', '=', request.env.user.id))
                    doman.append(('sh_user_ids', 'in', [request.env.user.id]))
            ticket_list = []
            doman.append(('stage_id', '=', stage.id))
            search_tickets = ticket_obj.sudo().search(doman)
            if search_tickets:
                for ticket in search_tickets:
                    ticket_dic = {
                        'ticket_id': ticket.id,
                        'ticket_no': ticket.name,
                        'partner_id': ticket.partner_id.name,
                        'create_date': str(ticket.create_date),
                        'write_date': str(ticket.write_date),
                        'user_id': ticket.user_id.name,
                    }
                    ticket_list.append(ticket_dic)
            search_stage = request.env['helpdesk.stages'].sudo().search([
                ('id', '=', stage.id)
            ], limit=1)
            if search_stage:
                ticket_data_dic.update({search_stage.name: ticket_list})
                ticket_data_list.append(search_stage.name)
        return request.env['ir.ui.view'].with_context()._render_template('sh_helpdesk.ticket_dashboard_tbl', {
            'ticket_data_dic': ticket_data_dic,
            'ticket_data_list': ticket_data_list,
        })
