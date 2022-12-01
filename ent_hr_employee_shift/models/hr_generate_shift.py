# -*- coding: utf-8 -*-
######################################################################################
#
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Copyright (C) 2022-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
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
from odoo import models, fields


class HrGenerateShift(models.TransientModel):
    _name = 'hr.shift.generate'

    hr_department = fields.Many2one('hr.department',
                                    string="Department",
                                    help="Department")
    start_date = fields.Date(string="Start Date",
                             required=True,
                             help="Start date")
    end_date = fields.Date(string="End Date",
                           required=True,
                           help="End date")
    company_id = fields.Many2one('res.company',
                                 string='Company',
                                 help="Company")

    def action_schedule_shift(self):
        """Create mass schedule for all departments based on the shift
        scheduled in corresponding employee's contract """
        if self.hr_department:
            for contract in self.env['hr.contract'].search(
                    [('department_id', '=', self.hr_department.id)]):
                if contract.shift_schedule:
                    for shift_val in contract.shift_schedule:
                        shift = shift_val.hr_shift
                    start_date = self.start_date
                    end_date = self.end_date
                    shift_obj = self.env['resource.calendar'].search(
                        [('hr_department', '=', self.hr_department.id),
                         ('name', '=', shift.name)], limit=1)
                    sequence = shift_obj.sequence
                    seq_no = sequence + 1
                    new_shift = self.env['resource.calendar'].search([
                        ('sequence', '=', seq_no),
                        ('hr_department', '=', self.hr_department.id)],
                        limit=1)
                    if new_shift:
                        shift_ids = [(0, 0, {
                            'hr_shift': new_shift.id,
                            'start_date': start_date,
                            'end_date': end_date
                        })]
                        contract.shift_schedule = shift_ids
                    else:
                        seq_no = 1
                        new_shift = self.env['resource.calendar'].search([
                            ('sequence', '=', seq_no),
                            ('hr_department', '=', self.hr_department.id)],
                            limit=1)
                        if new_shift:
                            shift_ids = [(0, 0, {
                                'hr_shift': new_shift.id,
                                'start_date': start_date,
                                'end_date': end_date
                            })]
                            contract.shift_schedule = shift_ids
                else:
                    start_date = self.start_date
                    end_date = self.end_date
                    shift_obj = self.env['resource.calendar'].search(
                        [('hr_department', '=', self.hr_department.id)],
                        limit=1)
                    sequence = shift_obj.sequence
                    seq_no = sequence + 1
                    new_shift = self.env['resource.calendar'].search([
                        ('sequence', '=', seq_no),
                        ('hr_department', '=', self.hr_department.id)],
                        limit=1)
                    if new_shift:
                        shift_ids = [(0, 0, {
                            'hr_shift': new_shift.id,
                            'start_date': start_date,
                            'end_date': end_date
                        })]
                        contract.shift_schedule = shift_ids
                    else:
                        seq_no = 1
                        new_shift = self.env['resource.calendar'].search([
                            ('sequence', '=', seq_no),
                            ('hr_department', '=', self.hr_department.id)],
                            limit=1)
                        if not new_shift:
                            vals = {
                                'name': self.hr_department.name + ' Shift',
                                'hr_department': self.hr_department.id,
                                'sequence': seq_no,
                                'company_id': self.env.company.id
                            }
                            self.env['resource.calendar'].create(vals)
                            sortedline = self.env['resource.calendar'].search(
                                [], order='create_date desc', limit=1)
                            shift_ids = [(0, 0, {
                                'hr_shift': sortedline.id,
                                'start_date': start_date,
                                'end_date': end_date
                            })]
                            contract.shift_schedule = shift_ids
                        else:
                            shift_ids = [(0, 0, {
                                'hr_shift': new_shift.id,
                                'start_date': start_date,
                                'end_date': end_date
                            })]
                            contract.shift_schedule = shift_ids

        else:
            for contract in self.env['hr.contract'].search([]):
                if contract.shift_schedule and contract.department_id:
                    for shift_val in contract.shift_schedule:
                        shift = shift_val.hr_shift
                    start_date = self.start_date
                    end_date = self.end_date
                    shift_obj = self.env['resource.calendar'].search(
                        [('hr_department', '=', contract.department_id.id),
                         ('name', '=', shift.name)], limit=1)
                    sequence = shift_obj.sequence
                    seq_no = sequence + 1
                    new_shift = self.env['resource.calendar'].search([
                        ('sequence', '=', seq_no),
                        ('hr_department', '=', contract.department_id.id)],
                        limit=1)
                    if new_shift:
                        shift_ids = [(0, 0, {
                            'hr_shift': new_shift.id,
                            'start_date': start_date,
                            'end_date': end_date
                        })]
                        contract.shift_schedule = shift_ids
                    else:
                        seq_no = 1
                        new_shift = self.env['resource.calendar'].search([
                            ('sequence', '=', seq_no),
                            ('hr_department', '=', contract.department_id.id)],
                            limit=1)
                        shift_ids = [(0, 0, {
                            'hr_shift': new_shift.id,
                            'start_date': start_date,
                            'end_date': end_date
                        })]
                        contract.shift_schedule = shift_ids
                else:
                    start_date = self.start_date
                    end_date = self.end_date
                    shift_obj = self.env['resource.calendar'].search(
                        [('hr_department', '=', self.hr_department.id)],
                        limit=1)
                    sequence = shift_obj.sequence
                    seq_no = sequence + 1
                    new_shift = self.env['resource.calendar'].search([
                        ('sequence', '=', seq_no),
                        ('hr_department', '=', self.hr_department.id)],
                        limit=1)
                    if new_shift:
                        shift_ids = [(0, 0, {
                            'hr_shift': new_shift.id,
                            'start_date': start_date,
                            'end_date': end_date
                        })]
                        contract.shift_schedule = shift_ids
                    else:
                        seq_no = 1
                        new_shift = self.env['resource.calendar'].search([
                            ('sequence', '=', seq_no),
                            ('hr_department', '=', self.hr_department.id)],
                            limit=1)
                        if not new_shift:
                            vals = {
                                'name': self.hr_department.name + ' Shift',
                                'hr_department': self.hr_department.id,
                                'sequence': seq_no,
                                'company_id': self.env.company.id
                            }
                            self.env['resource.calendar'].create(vals)
                            sortedline = self.env['resource.calendar'].search(
                                [], order='create_date desc', limit=1)
                            shift_ids = [(0, 0, {
                                'hr_shift': sortedline.id,
                                'start_date': start_date,
                                'end_date': end_date
                            })]
                            contract.shift_schedule = shift_ids
                        else:
                            shift_ids = [(0, 0, {
                                'hr_shift': new_shift.id,
                                'start_date': start_date,
                                'end_date': end_date
                            })]
                            contract.shift_schedule = shift_ids
