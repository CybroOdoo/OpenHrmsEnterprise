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
from odoo.tools import _
from odoo.exceptions import UserError


class HrLeaveType(models.Model):
    """ Extend model to add multilevel approval """
    _inherit = 'hr.leave.type'

    leave_validation_type = fields.Selection(
        selection_add=[('multi', 'Multi Level Approval')])
    leave_validators_ids = fields.One2many('hr.holidays.validators',
                                           'hr_holiday_status_id',
                                           string='Leave Validators',
                                           help="Approval users")

    @api.constrains('leave_validators_ids', 'leave_validation_type')
    def check_leave_validators_ids(self):
        """Checking the validation"""
        for each in self:
            if not each.leave_validators_ids \
                    and each.leave_validation_type == 'multi':
                raise UserError(_('You cannot make leave validators empty '
                                  'when selecting Multi Level Approval'))


class HrLeaveValidators(models.Model):
    """ Model for leave validators in Leave Types configuration """
    _name = 'hr.holidays.validators'

    hr_holiday_status_id = fields.Many2one('hr.leave.type',
                                           string="Holiday Status",
                                           help="Holiday status")
    holiday_validators_id = fields.Many2one('res.users',
                                            string='Leave Validators',
                                            help="Leave validators",
                                            domain="[('share','=',False)]")
