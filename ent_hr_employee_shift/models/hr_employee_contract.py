# -*- coding: utf-8 -*-
###################################################################################
#    A part of OpenHrms Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2021-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Techno solutions, Open HRMS (<https://www.cybrosys.com>)

#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrEmployeeContract(models.Model):
    _inherit = 'hr.contract'

    shift_schedule = fields.One2many('hr.shift.schedule', 'rel_hr_schedule',
                                     string="Shift Schedule",
                                     help="Shift schedule")
    working_hours = fields.Many2one('resource.calendar',
                                    string='Working Schedule',
                                    help="Working hours")
    department_id = fields.Many2one('hr.department',
                                    string="Department",
                                    help="Department",
                                    required=True)


class HrSchedule(models.Model):
    _name = 'hr.shift.schedule'

    start_date = fields.Date(string="Date From",
                             required=True,
                             help="Starting date for the shift")
    end_date = fields.Date(string="Date To",
                           required=True,
                           help="Ending date for the shift")
    rel_hr_schedule = fields.Many2one('hr.contract')
    hr_shift = fields.Many2one('resource.calendar',
                               string="Shift",
                               required=True,
                               help="Shift")
    company_id = fields.Many2one('res.company',
                                 string='Company',
                                 help="Company")

    @api.onchange('start_date', 'end_date')
    def get_department(self):
        """Adding domain to  the hr_shift field"""
        hr_department = None
        if self.start_date:
            hr_department = self.rel_hr_schedule.department_id.id
        return {
            'domain': {
                'hr_shift': [('hr_department', '=', hr_department)]
            }
        }

    @api.model
    def create(self, vals):
        self._check_overlap(vals)
        return super(HrSchedule, self).create(vals)

    def write(self, vals):
        self._check_overlap(vals)
        return super(HrSchedule, self).write(vals)

    def _check_overlap(self, vals):
        if self:
            shifts = self.env['hr.shift.schedule'].\
                search([('rel_hr_schedule', '=', self.rel_hr_schedule.id)])
            shifts -= self
        else:
            shifts = self.env['hr.shift.schedule'].\
                search([('rel_hr_schedule', '=', vals.get('rel_hr_schedule'))])
        start_date = fields.Date.to_date(vals.get('start_date', False)) if vals\
            .get('start_date', False) else self.start_date
        end_date = fields.Date.to_date(vals.get('end_date', False)) if vals\
            .get('end_date', False) else self.end_date
        if start_date and end_date:
            for each in shifts:
                if each.start_date <= start_date <= each.end_date \
                        or each.start_date <= end_date <= each.end_date \
                        or each.start_date <= start_date \
                        and each.end_date >= end_date \
                        or each.start_date >= start_date \
                        and each.end_date <= end_date:
                    raise UserError(_('The dates may not overlap with one '
                                      'another.'))
            if start_date > end_date:
                raise UserError(_('Start date should be less than end date in '
                                  'shift schedule.'))
        return True
