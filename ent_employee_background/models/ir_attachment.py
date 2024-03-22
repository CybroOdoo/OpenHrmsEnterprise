# -*- coding: utf-8 -*-
######################################################################################
#
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
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
from odoo import api, models, _
from odoo.exceptions import AccessError
from collections import defaultdict


class IrAttachment(models.Model):
    """Inherits the attachment model"""
    _inherit = 'ir.attachment'

    @api.model
    def check(self, mode, values=None):
        """ Restricts the access to an ir.attachment, according to referred
         mode """
        if self.env.is_superuser():
            return True
        # Always require an internal user (aka, employee) to access to a
        # attachment
        if not (self.env.is_admin() or self.env.user.
                has_group('base.group_user') or self.env.user.
                has_group('base.group_portal')):
            raise AccessError(_("Sorry, you are not allowed to access "
                                "this document."))
        # collect the records to check (by model)
        model_ids = defaultdict(set)  # {model_name: set(ids)}
        if self:
            # DLE P173: `test_01_portal_attachment`
            self._cr.execute(
                'SELECT res_model, res_id, create_uid, public, res_field '
                'FROM ir_attachment WHERE id IN %s',
                [tuple(self.ids)])
            for res_model, res_id, create_uid, public, res_field in (
                    self._cr.fetchall()):
                if not self.env.is_system() and res_field:
                    raise AccessError(
                        _("Sorry, you are not allowed to access "
                          "this document."))
                if public and mode == 'read':
                    continue
                if not (res_model and res_id):
                    continue
                model_ids[res_model].add(res_id)
        if values and values.get('res_model') and values.get('res_id'):
            model_ids[values['res_model']].add(values['res_id'])

        # check access rights on the records
        for res_model, res_ids in model_ids.items():
            # ignore attachments that are not attached to a resource anymore
            # when checking access rights (resource was deleted but attachment
            # was not)
            if res_model not in self.env:
                continue
            if res_model == 'res.users' and len(
                    res_ids) == 1 and self.env.uid == list(res_ids)[0]:
                # by default a user cannot write on itself, despite the list
                # of writeable fields
                # e.g. in the case of a user inserting an image into his
                # image signature
                # we need to bypass this check which would needlessly throw
                # us away
                continue
            records = self.env[res_model].browse(res_ids).exists()
            # For related models, check if we can write to the model, as
            # unlinking
            # and creating attachments can be seen as an update to the model
            access_mode = 'write' if mode in ('create', 'unlink') else mode
            records.check_access_rights(access_mode)
            records.check_access_rule(access_mode)
