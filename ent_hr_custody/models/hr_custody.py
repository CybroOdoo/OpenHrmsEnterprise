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
from datetime import date, datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class HrCustody(models.Model):
    """Hr custody contract creation model."""
    _name = 'hr.custody'
    _description = 'Hr Custody Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    read_only = fields.Boolean(string="check field", help="To check the "
                                                          "fields is readonly")
    name = fields.Char(string='Code', copy=False, help="Code")
    company_id = fields.Many2one('res.company', 'Company', readonly=True,
                                 help="Company",
                                 default=lambda self: self.env.user.company_id)
    quantity = fields.Integer(string="Quantity", default="1",
                              help="Quantity of the product")
    rejected_reason = fields.Text(string='Rejected Reason', copy=False,
                                  readonly=1, help="Reason for the rejection")
    renew_rejected_reason = fields.Text(string='Renew Rejected Reason',
                                        copy=False, readonly=1,
                                        help="Renew rejected reason")
    date_request = fields.Date(string='Requested Date', required=True,
                               track_visibility='always', readonly=True,
                               help="Requested date",
                               states={'draft': [('readonly', False)]},
                               default=datetime.now().strftime('%Y-%m-%d'))
    employee = fields.Many2one('hr.employee', string='Employee', required=True,
                               readonly=True, help="Employee",
                               default=lambda self: self.env.user.
                               employee_id.id,
                               states={'draft': [('readonly', False)]})
    purpose = fields.Char(string='Reason', track_visibility='always',
                          required=True, help="Reason")
    custody_name = fields.Many2one('custody.property', string='Property',
                                   required=True,
                                   help="Property name")
    location = fields.Char(string="Location", readonly=True,
                           help="Source location of the product")
    return_date = fields.Date(string='Return Date', required=True,
                              track_visibility='always',
                              help="Return date")
    renew_date = fields.Date(string='Renewal Return Date',
                             track_visibility='always',
                             help="Return date for the renewal", readonly=True,
                             copy=False)
    notes = fields.Html(string='Notes', help="Internal Notes")
    renew_return_date = fields.Boolean(default=False, copy=False,
                                       help="Renew return date")
    renew_reject = fields.Boolean(default=False, copy=False,
                                  help="Is renew rejected or not")
    state = fields.Selection(
        [('draft', 'Draft'), ('to_approve', 'Waiting For Approval'),
         ('approved', 'Approved'),
         ('returned', 'Returned'), ('rejected', 'Refused')], string='Status',
        default='draft',
        track_visibility='always', help="State in hr custody")
    mail_send = fields.Boolean(string="Mail Send", help="Is mail send or not")
    property_type = fields.Boolean(string="type", help="Property type")

    @api.onchange('employee')
    def _compute_read_only(self):
        """ Use this function to check weather the user has the permission to
        change the employee """
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if res_user.has_group('hr.group_hr_user'):
            self.read_only = True
        else:
            self.read_only = False

    def mail_reminder(self):
        """To set mail reminder"""
        now = datetime.now() + timedelta(days=1)
        date_now = now.date()
        match = self.search([('state', '=', 'approved')])
        for i in match:
            if i.return_date:
                exp_date = fields.Date.from_string(i.return_date)
                if exp_date <= date_now:
                    base_url = self.env['ir.config_parameter'].get_param(
                        'web.base.url')
                    url = base_url + _('/web#id=%s&view_type=form&model=hr'
                                       '.custody&menu_id=') % i.id
                    mail_content = _('Hi %s,<br>As per the %s you took %s on '
                                     '%s for the reason of %s. S0 here we '
                                     'remind you that you have to return that '
                                     'on or before %s. Otherwise, you can '
                                     'renew the reference number(%s) by '
                                     'extending the return date through '
                                     'following '
                                     'link.<br> <div style = "text-align: '
                                     'center; margin-top: 16px;"><a href = '
                                     '"%s" '
                                     'style = "padding: 5px 10px; font-size: '
                                     '12px; line-height: 18px; color: #FFFFFF; '
                                     'border-color:#875A7B;text-decoration: '
                                     'none; display: inline-block; '
                                     'margin-bottom: 0px; font-weight: '
                                     '400;text-align: center; vertical-align: '
                                     'middle; '
                                     'cursor: pointer; white-space: nowrap; '
                                     'background-image: none; '
                                     'background-color: #875A7B; border: 1px '
                                     'solid #875A7B; border-radius:3px;"> '
                                     'Renew %s</a></div>'
                                     ) % (i.employee.name,
                                          i.name,
                                          i.custody_name.name,
                                          i.date_request,
                                          i.purpose,
                                          date_now, i.name,
                                          url, i.name)
                    main_content = {
                        'subject': _('REMINDER On %s') % i.name,
                        'author_id': self.env.user.partner_id.id,
                        'body_html': mail_content,
                        'email_to': i.employee.work_email,
                    }
                    mail_id = self.env['mail.mail'].create(main_content)
                    mail_id.mail_message_id.body = mail_content
                    mail_id.send()
                    if i.employee.user_id:
                        mail_id.mail_message_id.write({'partner_ids': [
                            (4, i.employee.user_id.partner_id.id)]})

    @api.model
    def create(self, vals):
        """To create hr custody model"""
        vals['name'] = self.env['ir.sequence'].next_by_code('hr.custody')
        return super().create(vals)

    def sent(self):
        """Function for button sent"""
        self.state = 'to_approve'

    def send_mail(self):
        """Function for button send mail"""
        template = self.env.ref(
            'ent_hr_custody.custody_email_notification_template')
        self.env['mail.template'].browse(template.id).send_mail(self.id)
        self.mail_send = True

    def set_to_draft(self):
        """Function for set to draft"""
        self.state = 'draft'

    def renew_approve(self):
        """Function for renew approve button"""
        for custody in self.env['hr.custody'].search(
                [('custody_name', '=', self.custody_name.id)]):
            if custody.state == "approved":
                raise UserError(_("Custody is not available now"))
        self.return_date = self.renew_date
        self.renew_date = ''
        self.state = 'approved'

    def renew_refuse(self):
        """Function for renew refuse button """
        for custody in self.env['hr.custody'].search(
                [('custody_name', '=', self.custody_name.id)]):
            if custody.state == "approved":
                raise UserError(_("Custody is not available now"))
        self.renew_date = ''
        self.state = 'approved'

    def approve(self):
        """Function for approve button"""
        if self.custody_name.property_selection == 'empty':
            for custody in self.env['hr.custody'].search(
                    [('custody_name', '=', self.custody_name.id)]):
                if custody.state == "approved":
                    raise UserError(_("Custody is not available now"))
            self.state = 'approved'
        else:
            if self.custody_name.product_id.qty_available > 0:
                self.state = 'approved'
            else:
                raise UserError(_("Product is not available now"))
            if self.state == 'approved':
                rec = self.env['stock.quant'].search(
                    [('product_id', '=', self.custody_name.product_id.id),
                     ('location_id', '=', self.custody_name.location_id.id)])
                rec.quantity = \
                    self.custody_name.product_id.qty_available - self.quantity

    def set_to_return(self):
        """Function for set to return button"""
        self.state = 'returned'
        if self.state == 'returned':
            m_dia = self.env['stock.quant'].search(
                [('product_id', '=', self.custody_name.product_id.id),
                 ('location_id', '=', self.custody_name.location_id.id)])
            m_dia.quantity = \
                self.custody_name.product_id.qty_available + self.quantity
        self.return_date = date.today()

    @api.constrains('return_date')
    def validate_return_date(self):
        """Function for return date validation"""
        if self.return_date < self.date_request:
            raise ValidationError(_('Please Give Valid Return Date'))

    @api.onchange('custody_name')
    def change_custody_name(self):
        """Function for change custody name. To set the value of property
        type"""
        self.location = self.custody_name.location_id.name
        if self.custody_name.property_selection == 'product':
            self.property_type = True
        else:
            self.property_type = False
