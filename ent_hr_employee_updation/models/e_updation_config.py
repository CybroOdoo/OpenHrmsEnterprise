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

from odoo import fields, models, api


class JournalConfig(models.TransientModel):
    _inherit = ['res.config.settings']

    notice_period = fields.Boolean(string='Notice Period')
    no_of_days = fields.Integer()

    def set_values(self):
        super(JournalConfig, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            "hr_resignation.notice_period", self.notice_period)
        self.env['ir.config_parameter'].sudo().set_param(
            "hr_resignation.no_of_days", self.no_of_days)

    @api.model
    def get_values(self):
        res = super(JournalConfig, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        res['notice_period'] = get_param('hr_resignation.notice_period')
        res['no_of_days'] = int(get_param('hr_resignation.no_of_days'))
        return res
