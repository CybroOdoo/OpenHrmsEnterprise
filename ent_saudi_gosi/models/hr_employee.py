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
from odoo import api, fields, models
from dateutil.relativedelta import relativedelta


class HrEmployee(models.Model):
    """Inherited hr_employee to add new fields"""
    _inherit = 'hr.employee'

    type = fields.Selection([('saudi', 'Saudi')], string='Type',
                            help="Select the type")
    gosi_number = fields.Char(string='GOSI Number', help="Enter Gosi Number")
    issue_date = fields.Date(string='Issued Date', help="Choose Issued Date")
    age = fields.Integer(string='Age', compute='_compute_age', store=True,
                         help="Computed from Birthday")
    limit = fields.Boolean(string='Eligible For GOSI', compute='_compute_limit',
                           store=True, help="Eligibility for GOSI")

    @api.depends('birthday')
    def _compute_age(self):
        """Compute age from birthday field"""
        today = fields.Date.today()
        for res in self:
            if res.birthday:
                res.age = relativedelta(today, res.birthday).years
            else:
                res.age = 0

    @api.depends('age')
    def _compute_limit(self):
        """Check age for gosi eligibility"""
        for res in self:
            res.limit = 18 <= res.age <= 60