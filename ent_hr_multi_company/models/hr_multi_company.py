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


class HrAttendanceMultiCompany(models.Model):
    _inherit = 'hr.attendance'

    company_id = fields.Many2one('res.company', 'Company', copy=False, readonly=True, help="Company",
                                 default=lambda self: self.env.user.company_id)


class HrLeaveMultiCompany(models.Model):
    _inherit = 'hr.leave'

    company_id = fields.Many2one('res.company', 'Company', copy=False, readonly=True, help="Company",
                                 default=lambda self: self.env.user.company_id)


class HrPayslipMultiCompany(models.Model):
    _inherit = 'hr.payslip.run'

    company_id = fields.Many2one('res.company', 'Company', copy=False, readonly=True, help="Company",
                                 default=lambda self: self.env.user.company_id)


class HrSalaryCategoryMultiCompany(models.Model):
    _inherit = 'hr.salary.rule.category'

    company_id = fields.Many2one('res.company', 'Company', copy=False, readonly=True, help="Comapny",
                                 default=lambda self: self.env.user.company_id)
