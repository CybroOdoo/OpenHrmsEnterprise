# -*- coding: utf-8 -*-
######################################################################################
#
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Copyright (C) 2026-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions (odoo@cybrosys.com)
#
#    This program is under the terms of the Odoo Proprietary License v1.0 (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#    or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
########################################################################################
import pandas as pd
from dateutil import relativedelta
from odoo import _, api, fields, models
from odoo.addons.resource.models.utils import HOURS_PER_DAY
from odoo.exceptions import UserError, ValidationError


class HrOvertime(models.Model):
    """Model holding overtime data"""
    _name = 'hr.overtime'
    _description = "HR Overtime"
    _inherit = ['mail.thread']

    def _domain_employee(self):
        """Returns employee domain"""
        employee = self.env['hr.employee'].search(
            [('user_id', '=', self.env.user.id)], limit=1)
        domain = [('id', '=', employee.id)]
        if self.env.user.has_group('hr.group_hr_user'):
            domain = []
        return domain

    name = fields.Char(string='Name', help='Name of the record', readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employee',
                                  help='Employee corresponding to the overtime',
                                  domain=_domain_employee,
                                  default=lambda
                                      self: self.env.user.employee_id.id,
                                  required=True)
    department_id = fields.Many2one('hr.department', string="Department",
                                    help='Department of employee',
                                    related="employee_id.department_id")
    job_id = fields.Many2one('hr.job', string="Job",
                             help='Job of employee',
                             related="employee_id.job_id")
    manager_id = fields.Many2one('res.users', string="Manager",
                                 related="employee_id.parent_id.user_id",
                                 help='Manager of employee',
                                 store=True)
    current_user_id = fields.Many2one('res.users', string="Current User",
                                      related='employee_id.user_id',
                                      help='User corresponding to the employee',
                                      default=lambda self: self.env.uid,
                                      store=True)
    is_current_user = fields.Boolean(string='Current User',
                                     help='True for current users')
    project_id = fields.Many2one('project.project', string="Project",
                                 help='Choose the project')
    project_manager_id = fields.Many2one('res.users', string="Project Manager",
                                         compute='_get_project_manager',
                                         store=True,
                                         help='Manager of project')
    contract_id = fields.Many2one('hr.contract', string="Contract",
                                  related="employee_id.contract_id",
                                  help='Contract of employee'
                                  )
    date_from = fields.Datetime(string='From', help='Overtime staring time')
    date_to = fields.Datetime(string='To', help='Overtime ending time')
    days_no = fields.Float(string='No. of Days', compute='_compute_days_no',
                           help='Number of days', store=True)
    days_no_tmp = fields.Float(string='Hours', compute="_compute_days_no_tmp",
                               help='Total hours', store=True)
    desc = fields.Text(string='Description',
                       help='Description regarding the overtime')
    state = fields.Selection([('draft', 'Draft'),
                              ('f_approve', 'Waiting'),
                              ('approved', 'Approved'),
                              ('refused', 'Refused')], string="State",
                             help='State of the record',
                             default="draft")
    cancel_reason = fields.Text(string='Refuse Reason',
                                help='Reason for cancellation')
    leave_id = fields.Many2one('hr.leave.allocation',
                               string="Leave ID",
                               help='Leave allocation for overtime')
    attchd_copy = fields.Binary(string='Attach A File',
                                help='Attach the file here')
    attchd_copy_name = fields.Char(string='File Name', help='Name of the file')
    type = fields.Selection([('cash', 'Cash'), ('leave', 'Leave')],
                            default="leave",
                            required=True, string="Type",
                            help='Choose how to redeem the overtime')
    overtime_type_id = fields.Many2one('overtime.type',
                                       domain="[('type','=',type),"
                                              "('duration_type','=', "
                                              "duration_type)]",
                                       string='Overtime Type',
                                       help='Type of overtime'
                                       )
    public_holiday = fields.Char(string='Public Holiday',
                                 help='Public holiday details', readonly=True)
    attendance_ids = fields.Many2many('hr.attendance', string='Attendance',
                                      help='Attendance details')
    work_schedule_ids = fields.One2many(
        related='employee_id.resource_calendar_id.attendance_ids',
        string='Work Schedule', help='work schedule corresponding to '
                                     'the overtime')
    global_leave_ids = fields.One2many(
        related='employee_id.resource_calendar_id.global_leave_ids',
        string='Global Leaves', help='Global leave details corresponding '
                                     'to the overtime')
    duration_type = fields.Selection([('hours', 'Hour'),
                                      ('days', 'Days')], string="Duration Type",
                                     default="hours",
                                     required=True,
                                     help='Type of Duration')
    cash_hrs_amount = fields.Float(string='Overtime Amount',
                                   help='Amount for overtime', readonly=True)
    cash_day_amount = fields.Float(string='Overtime Amount',
                                   help='Amount for overtime', readonly=True)
    payslip_paid = fields.Boolean('Paid in Payslip',
                                  help='True if paid in payslip', readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        """Sequence generation"""
        for values in vals_list:
            if not values.get('name') or values.get('name') == '/':
                values['name'] = self.env['ir.sequence'].next_by_code('hr.overtime') or '/'
        return super().create(vals_list)

    def unlink(self):
        """Method for unlinking"""
        for overtime in self.filtered(
                lambda overtime: overtime.state != 'draft'):
            raise UserError(
                _('You cannot delete TIL request which is not in draft state.'))
        return super().unlink()

    @api.constrains('date_from', 'date_to')
    def _check_date(self):
        """Method for checking the dates"""
        for req in self:
            domain = [
                ('date_from', '<=', req.date_to),
                ('date_to', '>=', req.date_from),
                ('employee_id', '=', req.employee_id.id),
                ('id', '!=', req.id),
                ('state', 'not in', ['refused']),
            ]
            holidays = self.search_count(domain)
            if holidays:
                raise ValidationError(_(
                    'You can not have 2 Overtime requests that '
                    'overlaps on same day!'))

    @api.depends('days_no_tmp')
    def _compute_days_no(self):
        """Method for computing dats_no"""
        for rec in self:
            rec.days_no = rec.days_no_tmp

    @api.depends('date_from', 'date_to')
    def _compute_days_no_tmp(self):
        """Method to compute days_no_temp"""
        for sheet in self:
            if sheet.date_from and sheet.date_to:
                if sheet.date_from > sheet.date_to:
                    raise ValidationError(
                        'Start Date must be less than End Date')
            if sheet.date_from and sheet.date_to:
                start_dt = fields.Datetime.from_string(sheet.date_from)
                finish_dt = fields.Datetime.from_string(sheet.date_to)
                s = finish_dt - start_dt
                difference = relativedelta.relativedelta(finish_dt, start_dt)
                hours = difference.hours
                minutes = difference.minutes
                days_in_mins = s.days * 24 * 60
                hours_in_mins = hours * 60
                days_no = ((days_in_mins + hours_in_mins + minutes) / (24 * 60))
                diff = sheet.date_to - sheet.date_from
                days, seconds = diff.days, diff.seconds
                hours = days * 24 + seconds // 3600
                sheet.update({
                    'days_no_tmp': hours if sheet.duration_type == 'hours' else days_no,
                })

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        """Method for updating the sheet while changing the employee"""
        for sheet in self:
            if sheet.employee_id:
                sheet.update({
                    'department_id': sheet.employee_id.department_id.id,
                    'job_id': sheet.employee_id.job_id.id,
                    'manager_id': sheet.sudo().employee_id.parent_id.user_id.id,
                })

    @api.depends('project_id', 'project_id.user_id')
    def _get_project_manager(self):
        """Method for updating the sheet"""
        for sheet in self:
            sheet.project_manager_id = sheet.project_id.user_id

    @api.onchange('overtime_type_id')
    def _onchange_overtime_type_id(self):
        """Method executing while updating the overtime type"""
        if self.overtime_type_id.rule_line_ids and self.duration_type == 'hours':
            for recd in self.overtime_type_id.rule_line_ids:
                if recd.from_hrs < self.days_no_tmp <= recd.to_hrs and self.contract_id:
                    if self.contract_id.over_hour:
                        cash_amount = self.contract_id.over_hour * recd.hrs_amount
                        self.cash_hrs_amount = cash_amount
                    else:
                        raise UserError(
                            _("Hour Overtime Needs Hour Wage in Employee Contract."))
        elif self.overtime_type_id.rule_line_ids and self.duration_type == 'days':
            for recd in self.overtime_type_id.rule_line_ids:
                if recd.from_hrs < self.days_no_tmp <= recd.to_hrs and self.contract_id:
                    if self.contract_id.over_day:
                        cash_amount = self.contract_id.over_day * recd.hrs_amount
                        self.cash_day_amount = cash_amount
                    else:
                        raise UserError(
                            _("Day Overtime Needs Day Wage in Employee Contract."))

    @api.onchange('date_from', 'date_to', 'employee_id')
    def _onchange_date_from(self):
        """Method executing on changing the dates and employee"""
        holiday = False
        if self.contract_id and self.date_from and self.date_to:
            for leaves in self.contract_id.resource_calendar_id.global_leave_ids:
                leave_dates = pd.date_range(leaves.date_from,
                                            leaves.date_to).date
                overtime_dates = pd.date_range(self.date_from,
                                               self.date_to).date
                for over_time in overtime_dates:
                    for leave_date in leave_dates:
                        if leave_date == over_time:
                            holiday = True
            if holiday:
                self.write({
                    'public_holiday': 'You have Public Holidays in your Overtime request.'})
            else:
                self.write({'public_holiday': ' '})
            hr_attendance = self.env['hr.attendance'].search(
                [('check_in', '>=', self.date_from),
                 ('check_in', '<=', self.date_to),
                 ('employee_id', '=', self.employee_id.id)])
            self.update({
                'attendance_ids': [(6, 0, hr_attendance.ids)]
            })

    def action_submit(self):
        """Method for submitting the request"""
        return self.sudo().write({
            'state': 'f_approve'
        })

    def action_approve(self):
        """Method for approving the request"""
        if self.overtime_type_id.type == 'leave':
            if self.duration_type == 'days':
                holiday_vals = {
                    'name': 'Overtime',
                    'holiday_status_id': self.overtime_type_id.leave_type_id.id,
                    'number_of_days': self.days_no_tmp,
                    'notes': self.desc,
                    'employee_id': self.employee_id.id,
                }
            else:
                day_hour = self.days_no_tmp / HOURS_PER_DAY
                holiday_vals = {
                    'name': 'Overtime',
                    'holiday_status_id': self.overtime_type_id.leave_type_id.id,
                    'number_of_days': day_hour,
                    'notes': self.desc,
                    'employee_id': self.employee_id.id,
                }
            holiday = self.env['hr.leave.allocation'].sudo().create(
                holiday_vals)
            holiday.sudo().action_validate()
            self.leave_id = holiday.id
        return self.sudo().write({
            'state': 'approved',
        })

    def action_reject(self):
        """Method for rejecting the request"""
        self.state = 'refused'
