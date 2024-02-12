# -*- coding: utf-8 -*-
################################################################################
#
#    A part of OpenHRMS Project <https://www.openhrms.com>
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
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


class ResUsers(models.Model):
    """ Inherit res users for adding fields """
    _inherit = 'res.users'

    employee_id = fields.Many2one(comodel_name='hr.employee',
                                  string='Related Employee',
                                  ondelete='restrict', auto_join=True,
                                  help='Employee-related data of the user')

    @api.model
    def create(self, vals):
        """ This code is to create an employee while creating a user. """
        result = super(ResUsers, self).create(vals)
        val = self.search([('share', '=', False)])
        for record in val:
            if result.id == record.id:
                result['employee_id'] = self.env['hr.employee'].sudo().create(
                    {
                        'name': result['name'],
                        'user_id': result['id'],
                        'private_street': result['partner_id'].name
                    })
        return result
