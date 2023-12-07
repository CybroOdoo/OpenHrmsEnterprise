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
    """Used to create camps for company"""

    _name = "hr.camps"
    _description = "Camp for Company"
    _rec_name = "camp_number"

    camp_number = fields.Char(
        string="Camp Number",
        readonly=True,
        copy=False,
        default="New",
        help="Sequence number of the camp",
    )
    address = fields.Char(string="Address", help="Fill address of camp")
    capacity = fields.Integer(
        string="Capacity",
        compute="_compute_camp_capacity",
        help="Total capacity of camp",
    )
    occupied = fields.Integer(
        string="Occupied",
        compute="_compute_occupied_capacity",
        help=" Occupied room in corresponding camp",
    )
    available = fields.Integer(help="Availability of room")
    street = fields.Char(string="Address", help="fill the street")
    street2 = fields.Char(help="Field to fill street2", string="Street2")
    zip = fields.Char(change_default=True, help="Fill zip", string="Zip")
    city = fields.Char(help="Select city", string="City")
    state_id = fields.Many2one(
        "res.country.state",
        string="State",
        ondelete="restrict",
        domain="[('country_id', '=?', country_id)]",
        help="Select state",
    )
    country_id = fields.Many2one(
        "res.country", string="Country", ondelete="restrict", help="Select country"
    )
    country_code = fields.Char(
        related="country_id.code",
        string="Country Code",
        help="Field to fill country code",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.user.company_id.id,
        help="Field to select company",
    )
    employee_ids = fields.One2many(
        "hr.employee",
        "camp_id",
        string="Employee",
        readonly=True,
        help="Table shows employees on this camp",
    )
    state = fields.Selection(
        [("available", "Available"), ("full", "Full")],
        default="available",
        help="Field to represent state of record",
    )
    room_ids = fields.One2many(
        "hr.rooms",
        "camp_id",
        string="Rooms",
        readonly=True,
        help="Table to show room under this camp",
    )

    @api.model
    def create(self, vals):
        """Function return sequence number for record"""
        if vals.get("camp_number", "New") == "New":
            vals["camp_number"] = (
                self.env["ir.sequence"].next_by_code("hr.camps") or "New"
            )
            return super(HrCamps, self).create(vals)

    def _compute_camp_capacity(self):
        """Function compute total bed in camp"""
        for camp in self:
            camp.capacity = sum(
                self.env["hr.rooms"]
                .search([("camp_id", "=", camp.id)])
                .mapped("capacity")
            )

    def _compute_occupied_capacity(self):
        """Function compute occupied bed in camp"""
        for camp in self:
            camp.occupied = sum(
                self.env["hr.rooms"]
                .search([("camp_id", "=", camp.id)])
                .mapped("occupied")
            )
            camp.available = camp.capacity - camp.occupied
