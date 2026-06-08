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
from odoo import fields, models
from odoo.exceptions import UserError


class HrEmployee(models.Model):
    """Inherit hr.employee to track department, job, salary, hourly cost
    and contract type history changes."""
    _inherit = 'hr.employee'

    def write(self, vals):
        """Override write to track and log changes in employee fields."""
        # Snapshot old values BEFORE write
        old_values = {}
        for record in self:
            if not record.id:
                continue
            old_values[record.id] = {
                'name': record.name or '',
                'department_id': record.department_id.id if record.department_id else False,
                'job_id': record.job_id.id if record.job_id else False,
                'hourly_cost': record.hourly_cost,
                'wage': record.wage if hasattr(record, 'wage') else None,
                'contract_type_id': record.contract_type_id.id if hasattr(record,
                                                                          'contract_type_id') and record.contract_type_id else None,
            }

        result = super().write(vals)

        # Compare AFTER write and create history only if value changed
        for record in self:
            if record.id not in old_values:
                continue
            old = old_values[record.id]
            emp_id = record.id
            emp_name = record.name or old['name']

            # Department history
            if 'department_id' in vals:
                new_id = record.department_id.id if record.department_id else False
                if new_id != old['department_id'] and record.department_id.name:
                    self.env['department.history'].sudo().create({
                        'employee_id': emp_id,
                        'employee_name': emp_name,
                        'updated_date': fields.Date.today(),
                        'changed_field': 'Department',
                        'current_value': record.department_id.name,
                    })

            # Job Position history
            if 'job_id' in vals:
                new_id = record.job_id.id if record.job_id else False
                if new_id != old['job_id'] and record.job_id.name:
                    self.env['department.history'].sudo().create({
                        'employee_id': emp_id,
                        'employee_name': emp_name,
                        'updated_date': fields.Date.today(),
                        'changed_field': 'Job Position',
                        'current_value': record.job_id.name,
                    })

            # Hourly cost history
            if 'hourly_cost' in vals and record.hourly_cost != old['hourly_cost']:
                self.env['timesheet.cost'].sudo().create({
                    'employee_id': emp_id,
                    'employee_name': emp_name,
                    'updated_date': fields.Date.today(),
                    'current_value': str(record.hourly_cost),
                })

            # Wage / salary history
            if 'wage' in vals and hasattr(record, 'wage') and record.wage != old['wage']:
                self.env['salary.history'].sudo().create({
                    'employee_id': emp_id,
                    'employee_name': emp_name,
                    'updated_date': fields.Date.today(),
                    'current_value': str(record.wage),
                })

            # Contract Type history
            if 'contract_type_id' in vals and hasattr(record, 'contract_type_id'):
                new_id = record.contract_type_id.id if record.contract_type_id else None
                if new_id != old['contract_type_id'] and record.contract_type_id.name:
                    self.env['contract.history'].sudo().create({
                        'employee_id': emp_id,
                        'employee_name': emp_name,
                        'updated_date': fields.Date.today(),
                        'changed_field': 'Contract Type',
                        'current_value': record.contract_type_id.name,
                    })

        return result

    def action_department_details(self):
        """Open department and job history view for the employee."""
        res_user = self.env['res.users'].browse(self._uid)
        if res_user.has_group('hr.group_hr_manager') or \
                self.id == self.env.user.employee_id.id:
            return {
                'name': "Job/Department History",
                'view_mode': 'list',
                'res_model': 'department.history',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'domain': [('employee_id', '=', self.id)],
            }
        raise UserError('You cannot access this field!')

    def action_time_sheet(self):
        """Open timesheet cost history view for the employee."""
        res_user = self.env['res.users'].browse(self._uid)
        if res_user.has_group('hr.group_hr_manager') or \
                self.id == self.env.user.employee_id.id:
            return {
                'name': "Timesheet Cost Details",
                'view_mode': 'list',
                'res_model': 'timesheet.cost',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'domain': [('employee_id', '=', self.id)],
            }
        raise UserError('You cannot access this field!')

    def action_salary_history(self):
        """Open salary history view for the employee"""
        res_user = self.env['res.users'].browse(self._uid)
        if res_user.has_group('hr.group_hr_manager') or \
                self.id == self.env.user.employee_id.id:
            return {
                'name': "Salary History",
                'view_mode': 'list',
                'res_model': 'salary.history',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'domain': [('employee_id', '=', self.id)],
            }
        raise UserError('You cannot access this field!')

    def action_contract_history(self):
        """Open contract type history view for the employee"""
        res_user = self.env['res.users'].browse(self._uid)
        if res_user.has_group('hr.group_hr_manager') or \
                self.id == self.env.user.employee_id.id:
            return {
                'name': "Contract History",
                'view_mode': 'list',
                'res_model': 'contract.history',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'domain': [('employee_id', '=', self.id)],
            }
        raise UserError('You cannot access this field!')
