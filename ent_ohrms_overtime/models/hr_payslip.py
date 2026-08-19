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
from odoo import api, Command, fields, models


class HrPayslip(models.Model):
    """Inherited to add fields and functions"""
    _inherit = 'hr.payslip'

    overtime_ids = fields.Many2many('hr.overtime',
                                    string='Overtime', help='Overtime corresponding to the payslip')

    @api.model
    def _compute_input_line_ids(self):
        """
        function used for writing overtime record in payslip
        input tree.

        """
        res = super()._compute_input_line_ids()
        overtime_input_type = self.env.ref('ent_ohrms_overtime.hr_payslip_input_type_overtime')
        salary_rule = self.env.ref('ent_ohrms_overtime.hr_salary_rule_overtime')
        for payslip in self:
            input_data = []
            overtime_id = self.env['hr.overtime'].search([
                ('employee_id', '=', payslip.employee_id.id),
                ('contract_id', '=', payslip.contract_id.id),
                ('state', '=', 'approved'),
                ('payslip_paid', '=', False)
            ])
            cash_amount = sum(overtime_id.mapped('cash_hrs_amount')) + sum(
                overtime_id.mapped('cash_day_amount'))
            old_input_rec = payslip.input_line_ids.filtered(
                lambda r: r.input_type_id.id == overtime_input_type.id)
            if old_input_rec:
                for rec in old_input_rec:
                    payslip.input_line_ids = [(2, rec.id, 0)]
            if (overtime_id and payslip.struct_id and
                    overtime_input_type in payslip.struct_id.input_line_type_ids):
                payslip.overtime_ids = overtime_id
                input_data.append(Command.create({
                    'name': salary_rule.name,
                    'amount': cash_amount,
                    'input_type_id': overtime_input_type.id
                }))
                payslip.update({'input_line_ids': input_data})
        return res

    def action_payslip_done(self):
        """
        function used for marking paid overtime
        request.

        """
        for recd in self.overtime_ids:
            if recd.type == 'cash':
                recd.payslip_paid = True
        return super().action_payslip_done()
