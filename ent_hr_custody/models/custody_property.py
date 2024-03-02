# -*- coding: utf-8 -*-
###############################################################################
#
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions (odoo@cybrosys.com)
#
#    This program is under the terms of the Odoo Proprietary
#    License v1.0 (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software
#    or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
#    TORT OR OTHERWISE,
#    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
###############################################################################
from odoo import api, fields, models, _


class CustodyProperty(models.Model):
    """Hr property creation model."""
    _name = 'custody.property'
    _description = 'Custody Property'

    name = fields.Char(string='Property Name', required=True, help="Name of "
                                                                   "property")
    image = fields.Image(string="Image",
                         help="This field holds the image used for this "
                              "provider, limited to 1024x1024px")
    image_medium = fields.Binary(
        "Medium-sized image", attachment=True,
        help="Medium-sized image of this provider. It is automatically "
             "resized as a 128x128px image, with aspect ratio preserved. "
             "Use this field in form views or some kanban views.")
    image_small = fields.Binary(
        "Small-sized image", attachment=True,
        help="Small-sized image of this provider. It is automatically "
             "resized as a 64x64px image, with aspect ratio preserved. "
             "Use this field anywhere a small image is required.")
    desc = fields.Html(string='Description', help="Description")
    company_id = fields.Many2one('res.company', 'Company', help="Company",
                                 default=lambda self: self.env.user.company_id)
    property_selection = fields.Selection([('empty', 'No Connection'),
                                           ('product', 'Products')],
                                          default='empty',
                                          string='Property From',
                                          help="Select the property")
    product_id = fields.Many2one('product.product', string='Product',
                                 help="Product")
    stock_quant_ids = fields.Many2many('stock.quant', string="Stock",
                                       help="To get stock location")
    location_id = fields.Many2one('stock.location', string='Location',
                                  help="Locations of product",
                                  domain="[('id', 'in', stock_quant_ids)]")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """To set the domain of location"""
        self.name = self.product_id.name
        lod = self.env['stock.quant'].search(
            [('product_id', "=", self.product_id.id)])
        self.stock_quant_ids = [fields.Command.clear()]
        for rec in lod.location_id:
            self.write({
                'stock_quant_ids': [(4, rec.id)]
            })
