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
from odoo import fields, models, _


class HREmployee(models.Model):
    """Class is inherited to add custom fields and methods"""
    _inherit = 'hr.employee'

    legal_count = fields.Integer(compute='_compute_legal_count',
                                 string='Legal Actions',
                                 help='Number of legal actions associated with the employee')

    def _compute_legal_count(self):
        """Compute the legal actions count for the given employee"""
        for employee in self:
            employee.legal_count = self.env['hr.lawsuit'].search_count(
                [('employee_id', '=', employee.id)])

    def action_legal_view(self):
        """Returns a list of legal actions associated with the employee"""
        self.ensure_one()
        legal_ids = self.env['hr.lawsuit'].sudo().search(
            [('employee_id', '=', self.id)]).ids
        return {
            'domain': [('id', 'in', legal_ids)],
            'view_mode': 'list,form',
            'res_model': 'hr.lawsuit',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'name': _('Legal Actions'),
        }
