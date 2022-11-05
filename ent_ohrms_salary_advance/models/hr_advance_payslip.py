# -*- coding: utf-8 -*-
###################################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
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
from datetime import datetime
from odoo import models, api, _


class SalaryRuleInputInherit(models.Model):
    _inherit = 'hr.payslip'

    def input_data_salary_line(self, name, amount):
        input_type = self.env['hr.payslip.input.type'].search([
            ('input_id', '=', name)])
        for data in self:
            data.write({
                'input_line_ids': [(0, 0, {
                    'input_type_id': input_type,
                    'amount': amount
                })],
            })

    @api.onchange('struct_id', 'date_from', 'date_to', 'employee_id')
    def onchange_employee_salary(self):
        res = super(SalaryRuleInputInherit, self).onchange_employee_loan()
        salary_line = self.struct_id.rule_ids.filtered(
                        lambda x: x.code == 'SAR')
        if salary_line:
            get_amount = self.env['salary.advance'].search([
                ('employee_id', '=', self.employee_id.id),
                ('state', '=', 'approve')
            ])
            if get_amount:
                if self.date_from <= get_amount.date <= self.date_to:
                    amount = get_amount.advance
                    name = salary_line.id
                    date = get_amount.date
                    code = salary_line.code
                    if code not in self.input_line_ids.mapped('input_type_id').mapped('code'):
                        self.input_data_salary_line(name, amount)
        return res
