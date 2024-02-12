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
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """Inherited res config settings to add the alias prefix and alias
    domain."""
    _inherit = 'res.config.settings'

    alias_prefix = fields.Char(string='Prefix',
                               help='Default alias name for leave',
                               translate=True,
                               config_parameter='hr_holidays.alias_prefix')
    alias_domain = fields.Char(string='Domain', translate=True,
                               help='Default alias domain for leave',
                               config_parameter='hr_holidays.alias_domain')
