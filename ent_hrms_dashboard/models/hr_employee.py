# -*- coding: utf-8 -*-
################################################################################
#
#    A part of OpenHRMS Project <https://www.openhrms.com>
#
#    Copyright (C) 2026-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions (odoo@cybrosys.com)
#
#    This program is under the terms of the Odoo Proprietary License v1.0
#    (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the
#    Software or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#    OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
#    USE OR OTHER DEALINGS IN THE SOFTWARE.
#
################################################################################
import pandas as pd
from collections import defaultdict
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
from pytz import utc
from odoo import api, fields, models
from odoo.tools import _
from odoo.http import request
from odoo.tools import float_utils

ROUNDING_FACTOR = 16


class HrEmployee(models.Model):
    """Inherit hr employee for adding custom fields"""
    _inherit = 'hr.employee'

    birthday = fields.Date(string='Date of Birth', groups="base.group_user",
                           help="Birthday")

    def attendance_manual(self):
        """
            Manually record attendance for the current employee.
            This method is responsible for updating the attendance records for
            the employee based on the provided information, including the city,
            country, latitude, longitude, IP address, browser information,
            and the mode of attendance.
            Parameters:
            - None
            Returns:
            - The updated employee record.
            Note: This method assumes that the request object is available and
            has information such as geoip, user_agent, etc.
        """
        employee = request.env['hr.employee'].sudo().browse(
            request.session.uid)
        # v18->v19: geo-location fields (in_city, in_country_name, in_latitude,
        # in_longitude, in_ip_address, in_browser) were removed from hr.attendance
        # in v19. Passing them causes a hard ValueError on create().
        # We build the payload dynamically, only including fields that still
        # exist on the hr.attendance model.
        attendance_fields = self.env['hr.attendance'].sudo()._fields
        payload = {'mode': 'kiosk'}
        # _attendance_action_change() prepends 'in_'/'out_' to these keys
        # itself before writing to hr.attendance. Pass the bare key names.
        # We still guard against the field being absent in case of future
        # Odoo versions that may remove them at the hr.attendance level too.
        _geo_mapping = {
            'city':         lambda: request.geoip.city.name or _('Unknown'),
            'country_name': lambda: (request.geoip.country.name or
                                      request.geoip.continent.name or _('Unknown')),
            'latitude':     lambda: request.geoip.location.latitude or False,
            'longitude':    lambda: request.geoip.location.longitude or False,
            'ip_address':   lambda: request.geoip.ip,
            'browser':      lambda: request.httprequest.user_agent.browser,
        }
        for field_name, getter in _geo_mapping.items():
            # check both in_ and out_ prefixed variants exist on hr.attendance
            if ('in_' + field_name) in attendance_fields:
                try:
                    payload[field_name] = getter()
                except Exception:
                    pass
        employee.sudo()._attendance_action_change(payload)
        return employee

    @api.model
    def check_user_group(self):
        """ Check if the user belongs to the 'hr.group_hr_manager' group.
           Returns:
               bool: True if the user is in the 'hr.group_hr_manager' group,
               False otherwise.
        """
        uid = request.session.uid
        user = self.env['res.users'].sudo().search([('id', '=', uid)], limit=1)
        if user.has_group('hr.group_hr_manager'):
            return True
        else:
            return False

    @api.model
    def get_user_employee_details(self):
        """
           Get details related to the logged-in user's employee information.
           Returns:
           dict or False: Details of the user's employee information if
           available, else False.
        """
        uid = request.session.uid
        # Build the fields list dynamically — several fields were removed or
        # moved to private models in v19 (e.g. gender, country_id).
        # Requesting a non-existent field raises ValueError in v19, so we
        # filter the list against the model's actual field definitions first.
        _wanted_fields = [
            'id', 'name', 'job_id', 'department_id', 'birthday',
            'joining_date', 'image_1920', 'user_id', 'coach_id',
            'parent_id', 'child_ids', 'work_phone', 'private_phone',
            'work_email', 'resource_calendar_id',
            'sex', 'country_id', 'attendance_state',
            'payslip_count',
        ]
        # contracts_count computes by querying hr.contract internally.
        # Only request it when hr.contract is actually registered in Odoo 19.
        if 'hr.contract' in self.env:
            _wanted_fields.append('contracts_count')
        _model_fields = self.env['hr.employee'].sudo()._fields
        _safe_fields = [f for f in _wanted_fields if f in _model_fields]

        employee_rec = self.env['hr.employee'].sudo().search(
            [('user_id', '=', uid)], limit=1)

        if not employee_rec:
            return False

        employee = employee_rec.read(_safe_fields)
        leaves_to_approve = self.env['hr.leave'].sudo().search_count(
            [('state', 'in', ['confirm', 'validate1'])])
        today = datetime.strftime(datetime.today(), '%Y-%m-%d')
        query = """
        select count(id)
        from hr_leave
        WHERE (hr_leave.date_from::DATE,hr_leave.date_to::DATE) 
        OVERLAPS ('%s', '%s') and
        state='validate'""" % (today, today)
        cr = self._cr
        cr.execute(query)
        leaves_today = cr.fetchall()
        first_day = date.today().replace(day=1)
        last_day = (date.today() + relativedelta(months=1, day=1)) - timedelta(
            1)
        query = """
                select count(id)
                from hr_leave
                WHERE (hr_leave.date_from::DATE,hr_leave.date_to::DATE) 
                OVERLAPS ('%s', '%s')
                and  state='validate'""" % (first_day, last_day)
        cr = self._cr
        cr.execute(query)
        leaves_this_month = cr.fetchall()
        leaves_alloc_req = self.env['hr.leave.allocation'].sudo().search_count(
            [('state', 'in', ['confirm', 'validate1'])])
        timesheet_count = self.env['account.analytic.line'].sudo().search_count(
            [('project_id', '!=', False), ('user_id', '=', uid)])
        timesheet_view_id = self.env.ref(
            'hr_timesheet.hr_timesheet_line_search')
        job_applications = self.env['hr.applicant'].sudo().search_count([])
        if employee:
            sql = """select broad_factor from hr_employee_broad_factor 
            where id =%s"""
            self.env.cr.execute(sql, (employee[0]['id'],))
            result = self.env.cr.dictfetchall()
            broad_factor = result[0]['broad_factor'] if result[0][
                'broad_factor'] else False
            if employee[0].get('birthday'):
                diff = relativedelta(datetime.today(), employee[0]['birthday'])
                age = diff.years
            else:
                age = False
            # first_contract_date was removed in Odoo v19; derive from
            # the employee's first contract (if hr_contract is installed)
            # or fall back to joining_date.
            first_contract_date = employee[0].get('first_contract_date')
            if not first_contract_date:
                if 'hr.contract' in self.env:
                    emp_record = self.env['hr.employee'].sudo().browse(
                        employee[0]['id'])
                    first_contract = self.env['hr.contract'].sudo().search(
                        [('employee_id', '=', emp_record.id),
                         ('state', '!=', 'cancel')],
                        order='date_start asc', limit=1)
                    if first_contract:
                        first_contract_date = first_contract.date_start
                # fall back to joining_date if contract not found or module absent
                if not first_contract_date:
                    first_contract_date = employee[0].get('joining_date')
            if first_contract_date:
                diff = relativedelta(datetime.today(), first_contract_date)
                years = diff.years
                months = diff.months
                days = diff.days
                experience = '{} years {} months {} days'.format(years, months,
                                                                 days)
            else:
                experience = False
            if employee:
                data = {
                    'broad_factor': broad_factor if broad_factor else 0,
                    'leaves_to_approve': leaves_to_approve,
                    'leaves_today': leaves_today,
                    'leaves_this_month': leaves_this_month,
                    'leaves_alloc_req': leaves_alloc_req,
                    'emp_timesheets': timesheet_count,
                    'job_applications': job_applications,
                    'timesheet_view_id': timesheet_view_id,
                    'experience': experience,
                    'age': age,
                    # Safe defaults for fields that may not exist in v19.
                    # .get() returns None if the field was filtered out above;
                    # we then fall back to a sensible display value.
                    'payslip_count': employee[0].get('payslip_count') or 0,
                    'contracts_count': employee[0].get('contracts_count') or 0,
                    'has_contract_model': 'hr.contract' in self.env,
                    'attendance_state': employee[0].get('attendance_state') or 'checked_out',
                    'gender': employee[0].get('gender') or False,
                    'country_id': employee[0].get('country_id') or False,
                }
                employee[0].update(data)
            return employee
        else:
            return False

    @api.model
    def get_upcoming(self):
        """
           Retrieve upcoming events, birthdays, and announcements.
           Returns:
           dict: Contains upcoming birthdays, events, and announcements.
        """
        cr = self._cr
        uid = request.session.uid
        employee = self.env['hr.employee'].search([('user_id', '=', uid)],
                                                  limit=1)
        today = fields.Date.today()
        birthday_employees = self.env['hr.employee'].search_read(
            [('birthday', '!=', False)], fields=['id', 'name', 'birthday'],
            order='birthday ASC', limit=4)

        for emp in birthday_employees:
            if emp['birthday'].month == today.month and emp[
                'birthday'].day == today.day:
                emp['is_birthday'] = True
            else:
                emp_birthday = emp['birthday'].replace(year=today.year)
                if emp_birthday < today:
                    next_birthday = emp_birthday.replace(year=today.year + 1)
                else:
                    next_birthday = emp_birthday
                emp['days']  = (next_birthday - today).days

        announcements = self.env['hr.announcement'].search_read(
            [('state', '=', 'approved'),
             ('date_start', '<=', fields.Date.today()),
             '|', ('is_announcement', '=', True),
             '|', '|',
             ('employee_ids', 'in', employee.id),
             ('department_ids', 'in', employee.department_id.id),
             ('position_ids', 'in', employee.job_id.id),
             ], fields=['announcement_reason', 'date_start', 'date_end'])

        lang = f"'{self.env.context['lang']}'"
        cr.execute("""select e.id, e.name ->> e.lang as name, e.date_begin,
                e.date_end,rp.name as location
               from event_event e
               inner join res_partner rp 
               on e.address_id = rp.id
               and (e.date_begin >= now())
               order by e.date_begin limit 4 """)
        event = cr.fetchall()
        return {
            'birthday': birthday_employees,
            'event': event,
            'announcement': announcements
        }

    @api.model
    def get_dept_employee(self):
        """
           Get the count of employees per department.
           Returns:
           list: Contains dictionaries with department label and employee count.
           v18->v19: Replaced raw SQL (department_id no longer a direct column
           on hr_employee table) with ORM read_group.
        """
        groups = self.env['hr.employee'].sudo().read_group(
            domain=[('department_id', '!=', False)],
            fields=['department_id'],
            groupby=['department_id'],
        )
        data = []
        for group in groups:
            dept = group['department_id']
            if dept:
                dept_name = dept[1] if isinstance(dept, (list, tuple)) else str(dept)
                data.append({'label': dept_name, 'value': group['department_id_count']})
        return data

    @api.model
    def get_department_leave(self):
        """
           Retrieve department-wise leave statistics for the last six months.
           Returns:
           tuple: Graph results and department list.
        """
        month_list = []
        graph_result = []
        for i in range(5, -1, -1):
            last_month = datetime.now() - relativedelta(months=i)
            text = format(last_month, '%B %Y')
            month_list.append(text)
        dept_records = self.env['hr.department'].sudo().search_read(
            [('active', '=', True)], fields=['id', 'name'])
        # name may be a translated dict {'en_US': '...' } or a plain string
        def _dept_name(val):
            if isinstance(val, dict):
                return list(val.values())[0]
            return val or ''
        departments = [{'id': d['id'], 'name': _dept_name(d['name'])} for d in dept_records]
        department_list = [d['name'] for d in departments]
        for month in month_list:
            leave = {}
            for dept in departments:
                leave[dept['name']] = 0
            vals = {
                'l_month': month,
                'leave': leave
            }
            graph_result.append(vals)
        sql = """
        SELECT h.id, h.employee_id,h.department_id
             , extract('month' FROM y)::int AS leave_month
             , to_char(y, 'Month YYYY') as month_year
             , GREATEST(y                    , h.date_from) AS date_from
             , LEAST   (y + interval '1 month', h.date_to)   AS date_to
        FROM  (select * from hr_leave where state = 'validate') h
             , generate_series(date_trunc('month', date_from::timestamp)
                             , date_trunc('month', date_to::timestamp)
                             , interval '1 month') y
        where date_trunc('month', GREATEST(y , h.date_from)) >= 
        date_trunc('month', now()) - interval '6 month' and
        date_trunc('month', GREATEST(y , h.date_from)) <= 
        date_trunc('month', now())
        and h.department_id is not null
        """
        self.env.cr.execute(sql)
        results = self.env.cr.dictfetchall()
        leave_lines = []
        for line in results:
            employee = self.browse(line['employee_id'])
            from_dt = fields.Datetime.from_string(line['date_from'])
            to_dt = fields.Datetime.from_string(line['date_to'])
            days = employee.get_work_days_dashboard(from_dt, to_dt)
            line['days'] = days
            vals = {
                'department': line['department_id'],
                'l_month': line['month_year'],
                'days': days
            }
            leave_lines.append(vals)
        if leave_lines:
            df = pd.DataFrame(leave_lines)
            rf = df.groupby(['l_month', 'department']).sum()
            result_lines = rf.to_dict('index')
            for month in month_list:
                for line in result_lines:
                    if month.replace(' ', '') == line[0].replace(' ', ''):
                        match = list(filter(lambda d: d['l_month'] in [month],
                                            graph_result))[0]['leave']
                        dept_rec_name = self.env['hr.department'].browse(line[1]).name
                        dept_name = list(dept_rec_name.values())[0] if isinstance(dept_rec_name, dict) else (dept_rec_name or '')
                        if match:
                            match[dept_name] = result_lines[line]['days']
        for result in graph_result:
            result['l_month'] = result['l_month'].split(' ')[:1][0].strip()[
                                :3] + " " + \
                                result['l_month'].split(' ')[1:2][0]
        return graph_result, department_list

    def get_work_days_dashboard(self, from_datetime, to_datetime,
                                compute_leaves=False, calendar=None,
                                domain=None):
        """
               Calculate workdays between two datetime objects.
        """
        resource = self.resource_id
        calendar = calendar or self.resource_calendar_id

        if not from_datetime.tzinfo:
            from_datetime = from_datetime.replace(tzinfo=utc)
        if not to_datetime.tzinfo:
            to_datetime = to_datetime.replace(tzinfo=utc)
        from_full = from_datetime - timedelta(days=1)
        to_full = to_datetime + timedelta(days=1)
        intervals = calendar._attendance_intervals_batch(from_full, to_full,
                                                         resource)
        day_total = defaultdict(float)
        for start, stop, meta in intervals[resource.id]:
            day_total[start.date()] += (stop - start).total_seconds() / 3600
        if compute_leaves:
            intervals = calendar._work_intervals_batch(from_datetime,
                                                       to_datetime, resource,
                                                       domain)
        else:
            intervals = calendar._attendance_intervals_batch(from_datetime,
                                                             to_datetime,
                                                             resource)
        day_hours = defaultdict(float)
        for start, stop, meta in intervals[resource.id]:
            day_hours[start.date()] += (stop - start).total_seconds() / 3600
        days = sum(
            float_utils.round(ROUNDING_FACTOR * day_hours[day] / day_total[
                day]) / ROUNDING_FACTOR
            for day in day_hours
        )
        return days

    @api.model
    def employee_leave_trend(self):
        """
           Generate a trend of employee leaves over the last six months.
           Returns:
           list: Employee leave trends.
        """
        leave_lines = []
        month_list = []
        graph_result = []
        for i in range(5, -1, -1):
            last_month = datetime.now() - relativedelta(months=i)
            text = format(last_month, '%B %Y')
            month_list.append(text)
        uid = request.session.uid
        employee = self.env['hr.employee'].sudo().search_read(
            [('user_id', '=', uid)], limit=1)
        for month in month_list:
            vals = {
                'l_month': month,
                'leave': 0
            }
            graph_result.append(vals)
        sql = """
                SELECT h.id, h.employee_id
                     , extract('month' FROM y)::int AS leave_month
                     , to_char(y, 'Month YYYY') as month_year
                     , GREATEST(y                    , h.date_from) AS date_from
                     , LEAST   (y + interval '1 month', h.date_to)   AS date_to
                FROM  (select * from hr_leave where state = 'validate') h
                     , generate_series(date_trunc('month', date_from::timestamp)
                                     , date_trunc('month', date_to::timestamp)
                                     , interval '1 month') y
                where date_trunc('month', GREATEST(y , h.date_from)) >= 
                date_trunc('month', now()) - interval '6 month' and
                date_trunc('month', GREATEST(y , h.date_from)) <= 
                date_trunc('month', now()) and h.employee_id = %s """
        self.env.cr.execute(sql, (employee[0]['id'],))
        results = self.env.cr.dictfetchall()
        for line in results:
            employee = self.browse(line['employee_id'])
            from_dt = fields.Datetime.from_string(line['date_from'])
            to_dt = fields.Datetime.from_string(line['date_to'])
            days = employee.get_work_days_dashboard(from_dt, to_dt)
            line['days'] = days
            vals = {
                'l_month': line['month_year'],
                'days': days
            }
            leave_lines.append(vals)
        if leave_lines:
            df = pd.DataFrame(leave_lines)
            rf = df.groupby(['l_month']).sum()
            result_lines = rf.to_dict('index')
            for line in result_lines:
                match = list(filter(
                    lambda d: d['l_month'].replace(' ', '') == line.replace(' ',
                                                                            ''),
                    graph_result))
                if match:
                    match[0]['leave'] = result_lines[line]['days']
        for result in graph_result:
            result['l_month'] = result['l_month'].split(' ')[:1][0].strip()[
                                :3] + " " + \
                                result['l_month'].split(' ')[1:2][0]
        return graph_result

    @api.model
    def join_resign_trends(self):
        """
           Generate trends related to employee joinings and resignations.
           Returns:
           list: Joining and resignation trends.
        """
        cr = self.env.cr
        month_list = []
        join_trend = []
        resign_trend = []
        for i in range(11, -1, -1):
            last_month = datetime.now() - relativedelta(months=i)
            text = format(last_month, '%B %Y')
            month_list.append(text)
        for month in month_list:
            vals = {
                'l_month': month,
                'count': 0
            }
            join_trend.append(vals)
        for month in month_list:
            vals = {
                'l_month': month,
                'count': 0
            }
            resign_trend.append(vals)
        cr.execute('''select to_char(joining_date, 'Month YYYY') as l_month,
         count(id) from hr_employee
        WHERE joining_date BETWEEN CURRENT_DATE - INTERVAL '12 months'
        AND CURRENT_DATE + interval '1 month - 1 day'
        group by l_month''')
        join_data = cr.fetchall()
        cr.execute('''select to_char(resign_date, 'Month YYYY') as l_month,
         count(id) from hr_employee
        WHERE resign_date BETWEEN CURRENT_DATE - INTERVAL '12 months'
        AND CURRENT_DATE + interval '1 month - 1 day'
        group by l_month;''')
        resign_data = cr.fetchall()
        for line in join_data:
            match = list(filter(
                lambda d: d['l_month'].replace(' ', '') == line[0].replace(' ',
                                                                           ''),
                join_trend))
            if match:
                match[0]['count'] = line[1]
        for line in resign_data:
            match = list(filter(
                lambda d: d['l_month'].replace(' ', '') == line[0].replace(' ',
                                                                           ''),
                resign_trend))
            if match:
                match[0]['count'] = line[1]
        for join in join_trend:
            join['l_month'] = join['l_month'].split(' ')[:1][0].strip()[:3]
        for resign in resign_trend:
            resign['l_month'] = resign['l_month'].split(' ')[:1][0].strip()[:3]
        graph_result = [{
            'name': 'Join',
            'values': join_trend
        }, {
            'name': 'Resign',
            'values': resign_trend
        }]
        return graph_result

    @api.model
    def get_attrition_rate(self):
        """
           Calculate the attrition rate for each month over the past year.
           Returns:
           list: Attrition rates for each month.
        """
        month_attrition = []
        monthly_join_resign = self.join_resign_trends()
        month_join = monthly_join_resign[0]['values']
        month_resign = monthly_join_resign[1]['values']
        sql = """
        SELECT (date_trunc('month', CURRENT_DATE))::date - interval '1' 
        month * s.a AS month_start
        FROM generate_series(0,11,1) AS s(a);"""
        self._cr.execute(sql)
        month_start_list = self._cr.fetchall()
        for month_date in month_start_list:
            self._cr.execute("""select count(id), 
            to_char(date '%s', 'Month YYYY') as l_month from hr_employee
            where resign_date> date '%s' or resign_date is null and 
            joining_date < date '%s'
            """ % (month_date[0], month_date[0], month_date[0],))
            month_emp = self.env.cr.fetchone()
            match_join = \
                list(filter(
                    lambda d: d['l_month'] == month_emp[1].split(' ')[:1][
                                                  0].strip()[:3], month_join))[
                    0][
                    'count']
            match_resign = \
                list(filter(
                    lambda d: d['l_month'] == month_emp[1].split(' ')[:1][
                                                  0].strip()[:3],
                    month_resign))[0][
                    'count']
            month_avg = (month_emp[0] + match_join - match_resign + month_emp[
                0]) / 2
            attrition_rate = (match_resign / month_avg) * 100 \
                if month_avg != 0 else 0
            vals = {
                'month': month_emp[1].split(' ')[:1][0].strip()[:3],
                'attrition_rate': round(float(attrition_rate), 2)
            }
            month_attrition.append(vals)
        return month_attrition

    @api.model
    def get_employee_skill(self):
        """ Retrieve employee skills and its progress"""
        employee = self.env['hr.employee'].sudo().search(
            [('user_id', '=', request.session.uid)], limit=1)
        skills = self.env['hr.employee.skill'].sudo().search_read(
            [('employee_id', '=', employee.id)])
        dataset = []
        for rec in skills:
            vals = {
                'skills': rec['skill_type_id'][1] + '-' + rec['skill_id'][1],
                'progress': rec['level_progress']
            }
            dataset.append(vals)
        return dataset


class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    birthday = fields.Date(string='Date of Birth', groups="base.group_user",
                           help="Birthday")
    personal_mobile = fields.Char(
        string='Mobile',
        help="Personal mobile number of the employee")
    joining_date = fields.Date(
        string='Joining Date',
        help="Employee joining date computed from the contract start date",
        compute='_compute_joining_date', store=True)
    id_expiry_date = fields.Date(
        string='Expiry Date',
        help='Expiry date of Identification ID')
    passport_expiry_date = fields.Date(
        string='Expiry Date',
        help='Expiry date of Passport ID')
    resign_date = fields.Date(string="Resign Date", readonly=True,
                              help="Date of the resignation")
    resigned = fields.Boolean(string="Resigned", default=False, store=True,
                              help="If checked then employee has resigned")
    fired = fields.Boolean(string="Fired", default=False, store=True,
                           help="If checked then employee has fired")