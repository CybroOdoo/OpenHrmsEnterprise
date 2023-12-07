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


class HrRooms(models.Model):
    """Used to create room for company"""

    _name = "hr.rooms"
    _description = "Room for Company"
    _rec_name = "room_number"

    room_number = fields.Char(
        string="Room Number",
        readonly=True,
        copy=False,
        default="New",
        help="Sequence number of the camp",
    )
    category = fields.Selection(
        [("male", "Male"), ("female", "Female"), ("other", "Other")],
        string="Category",
        required=True,
    )
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
    capacity = fields.Integer(
        string="Capacity",
        required=True,
        default="1",
        help="Give the capacity of room here",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.user.company_id.id,
    )
    camp_id = fields.Many2one(
        "hr.camps", string="Camp", required=True, help="Camp on which the room"
    )
    employee_ids = fields.One2many(
        "hr.employee",
        "room_id",
        string="Employee",
        readonly=True,
        help="Employees on this room ",
    )
    occupied = fields.Integer(
        string="Occupied",
        compute="_compute_occupied_number_room",
        help="Number of employees in the room ",
    )
    available = fields.Integer(string="Available", help="state of room")
    state = fields.Selection(
        [("available", "Available"), ("not_available", "Not Available")],
        default="not_available",
    )

    @api.model
    def create(self, vals):
        """Function return sequence number for record"""
        if vals.get("room_number", "New") == "New":
            vals["room_number"] = (
                self.env["ir.sequence"].next_by_code("hr.rooms") or "New"
            )
            return super(HrRooms, self).create(vals)

    def _compute_occupied_number_room(self):
        """Function compute occupied bed in room"""
        for room in self:
            room.occupied = self.env["hr.employee"].search_count(
                [("room_id", "=", room.id)]
            )
            room.available = room.capacity - room.occupied

    def action_create_room(self):
        """Function to create a room and do the
        necessary functions like calculating capacity and occupied bed"""
        self.write({"state": "available"})
        rooms = self.search([("camp_id", "=", self.camp_id.id)])
        self.camp_id.capacity = sum(rooms.mapped("capacity"))
        self.camp_id.occupied = sum(rooms.mapped("occupied"))
        self.camp_id.available = self.camp_id.capacity - self.camp_id.occupied
