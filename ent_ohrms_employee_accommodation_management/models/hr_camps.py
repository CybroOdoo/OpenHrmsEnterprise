# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Ranjith R(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
###########################################################################
from odoo import api, fields, models


class HrCamps(models.Model):
    """ Used to create camps for company"""
    _name = "hr.camps"
    _description = "Camp for Company"

    name = fields.Char(string="Camp Number", readonly=True,
                       copy=False, default="New", help="Name of camp")
    address = fields.Char(string="Address", help="Camp Address")
    capacity = fields.Integer(string="Capacity",
                              compute="_compute_capacity",
                              help="Total capacity of camp")
    occupied = fields.Integer(string="Occupied",
                              compute="_compute_available",
                              help=" Occupied room in corresponding camp")
    available = fields.Integer(string="Availability",
                               help="Availability of room")
    street = fields.Char(string="Street", help="Name of street")
    nearby_street = fields.Char(string="Near by Street",
                                help="Name of nearby Street ")
    zip = fields.Char(string="Zip", change_default=True,
                      help="Zip where camp is situated")
    city = fields.Char(string="City", help="City name")
    state_id = fields.Many2one("res.country.state", string='State',
                               ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]",
                               help="State where camp is situated")
    country_id = fields.Many2one('res.country', string='Country',
                                 ondelete='restrict',
                                 help="Country where camp is situated")
    country_code = fields.Char(string="Country Code", related='country_id.code',
                               help="Field to fill country code")
    company_id = fields.Many2one('res.company', string='Company',
                                 required=True, default=lambda
            self: self.env.user.company_id.id,
                                 help="Field to select company")
    employee_ids = fields.One2many('hr.employee',
                                   'camp_id', string="Employees",
                                   readonly=True,
                                   help="Table shows employees on this camp")
    state = fields.Selection([('available', 'Available'),
                              ('full', 'Full')],
                             default="available", string="State of Camp",
                             help="Field to represent state of record")
    room_ids = fields.One2many('hr.rooms', 'camp_id',
                               string="Rooms", readonly=True,
                               help="Table to show room under this camp")

    @api.model
    def create(self, vals):
        """Function return sequence number for record"""
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'hr.camps') or 'New'
            return super(HrCamps, self).create(vals)

    def _compute_capacity(self):
        """Function compute total bed in camp"""
        for camp in self:
            camp.capacity = sum(self.env['hr.rooms'].search(
                [('camp_id', '=', camp.id)]).mapped('capacity'))

    def _compute_available(self):
        """Function compute occupied bed in camp"""
        for camp in self:
            camp.occupied = sum(
                self.env['hr.rooms'].search([('camp_id', '=', camp.id)]).mapped(
                    'occupied'))
            camp.available = camp.capacity - camp.occupied
            if camp.available > 0:
                camp.write({'state': 'available'})
            else:
                camp.write({'state': 'full'})
