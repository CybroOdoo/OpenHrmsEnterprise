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

import base64
import zipfile
from io import BytesIO

from odoo import http, _
from odoo.exceptions import AccessError, UserError
from odoo.http import request, content_disposition
from odoo.tools import consteq
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal \
    import CustomerPortal, pager as portal_pager, get_records_pager


class CustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        employee_records = request.env['employee.verification'].sudo().search(
            ['&', ('state', '=', 'assign'), ('agency', '=', partner.id)])

        if 'varification_count' in counters:
            values['varification_count'] = employee_records.search_count([('state', '=', 'assign')]) if employee_records else 0

        return values

    @http.route(['/my/records', '/my/records/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_records(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        partner = request.env.user.partner_id
        employee_records = request.env['employee.verification'].sudo().search(
            ['&', ('state', '=', 'assign'), ('agency', '=', partner.id)])
        varification_count = request.env['employee.verification'].sudo().search_count(
            ['&', ('state', '=', 'assign'), ('agency', '=', partner.id)])
        pager = portal_pager(
            url="/my/records",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=varification_count,
            page=page,
            step=self._items_per_page
        )
        values = {
            'date': date_begin,
            'records': employee_records.sudo(),
            'page_name': 'employee',
            'pager': pager,
            # 'archive_groups': archive_groups,
            'default_url': '/my/records',
            # 'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        }
        return request.render("ent_employee_background.portal_my_records", values)

    @http.route(['/my/details/<int:order>'], type='http', auth="public", website=True)
    def portal_record_page(self, order=None, access_token=None, **kw):

        try:
            data = request.env['employee.verification'].sudo().browse(order)

        except AccessError:
            return request.redirect('/my')

        values = {
            'page_name': 'employee_details',
            'records': data
        }

        return request.render("ent_employee_background.portal_record_page", values)

    @http.route('/test/path', type='http', auth="public", website=True, csrf=False)
    def portal_order_report(self, **kw):

        employee = request.env['employee.verification'].sudo().browse(kw['employee_token'])
        if kw['description'] or kw.get('attachment', False):
            if kw['description']:
                employee.description_by_agency = kw['description']
            if kw.get('attachment', False):
                Attachments = request.env['ir.attachment']
                name = kw.get('attachment').filename
                file = kw.get('attachment')
                attachment = file.read()
                attachment_id = Attachments.sudo().create({
                    'name': name,
                    'store_fname': name,
                    'res_name': name,
                    'type': 'binary',
                    'res_model': 'employee.verification',
                    'res_id': kw['employee_token'],
                    'mimetype': 'image/jpeg',
                    'datas': base64.b64encode(attachment),
                })

                employee.agency_attachment_id = attachment_id
            employee.state = 'submit'
            values = {
                'page_name': 'employee_submit'
            }
            return request.render("ent_employee_background.portal_record_completed", values)
        else:
            raise UserError(_("You need to Enter description or attact a file before submit."))

    @http.route('/my/attachments/download/<int:order>', type='http', auth="public")
    def download_document(self, order):
        employee_record = request.env['employee.verification'].sudo().browse(order)
        if employee_record:
            attachment_ids = employee_record.mapped('resume_uploaded')
            if attachment_ids:
                file_dict = {}
                for attachment_id in attachment_ids:
                    file_struct = attachment_id.store_fname
                    if file_struct:
                        file_name = attachment_id.name
                        file_path = attachment_id._full_path(file_struct)
                        file_dict["%s:%s" % (file_struct, file_name)] = dict(path=file_path, name=file_name)
                zip_filename = "%s_Employee_Verification.zip" % employee_record.verification_id
                bytIO = BytesIO()
                zip_file = zipfile.ZipFile(bytIO, "w", zipfile.ZIP_STORED)
                for file_info in file_dict.values():
                    zip_file.write(file_info["path"], file_info["name"])
                zip_file.close()
                return request.make_response(bytIO.getvalue(),
                                             headers=[('Content-Type', 'application/x-zip-compressed'),
                                                      ('Content-Disposition', content_disposition(zip_filename))])

            else:
                return request.redirect('/')
        else:
            return request.redirect('/')
