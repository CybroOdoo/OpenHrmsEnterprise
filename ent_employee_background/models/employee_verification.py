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
from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class EmployeeVerification(models.Model):
    """Employee verification records"""
    _name = 'employee.verification'
    _description = 'Employee Verification'
    _rec_name = 'verification'

    verification = fields.Char('ID', readonly=True, copy=False,
                               help="Verification Id")
    employee_id = fields.Many2one('hr.employee', string='Employee',
                                  required=True,
                                  help='You can choose the employee for '
                                       'background verification')
    address_id = fields.Many2one(related='employee_id.work_contact_id',
                                 string='Address', readonly=False)
    assigned_by_id = fields.Many2one('res.users',
                                     string='Assigned By', readonly=1,
                                     default=lambda self: self.env.uid,
                                     help="Assigned Login User")
    agency_id = fields.Many2one('res.partner', string='Agency',
                                domain=[('verification_agent', '=', True)],
                                help='You can choose a Verification Agent')
    resume_uploaded_ids = fields.Many2many('ir.attachment',
                                           string="Resume of Applicant",
                                           help='You can attach the copy of '
                                                'your document', copy=False)
    description_by_agency = fields.Char(string='Description', readonly=True,
                                        help="Description")
    agency_attachment_id = fields.Many2one('ir.attachment',
                                           string='Attachment',
                                           help='Attachment from Agency')
    field_check = fields.Boolean(string='Check', invisible=True)
    assigned_date = fields.Date(string="Assigned Date", readonly=True,
                                default=date.today(),
                                help="Record Assigned Date")
    expected_date = fields.Date(string='Expected Date',
                                help='Expected date of completion of '
                                     'background verification')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('assign', 'Assigned'),
        ('submit', 'Verification Completed'),
    ], string='Status', default='draft')
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self:
                                 self.env['res.company'].browse(1))

    def action_download_attachment(self):
        """Download attachment file"""
        if self.agency_attachment_id:
            return {
                'type': 'ir.actions.act_url',
                'url': "web/content/?model=ir.attachment&id=" + str(
                    self.agency_attachment_id.id) +
                       "&filename_field=name&field=datas&download=true&name=" +
                       self.agency_attachment_id.name,
                'target': 'self'
            }
        else:
            raise UserError(_("No attachments available."))

    def assign_statusbar(self):
        """Send mail for the verification"""
        if self.agency_id:
            if self.address_id or self.resume_uploaded_ids:
                self.state = 'assign'
                template = self.env.ref('ent_employee_background.'
                                        'assign_agency_email_template')
                (self.env['mail.template'].browse(template.id).send_mail
                 (self.id, force_send=True))
            else:
                raise UserError(_("There should be at least address or resume "
                                  "of the employee."))
        else:
            raise UserError(_("Agency is not assigned. Please select one "
                              "of the Agency."))

    # sequence generation for employee verification
    @api.model
    def create(self, vals):
        """Super the Create operation"""
        seq = self.env['ir.sequence'].next_by_code('res.users') or '/'
        vals['verification'] = seq
        return super(EmployeeVerification, self).create(vals)

    def unlink(self):
        """Super unlink() function"""
        if self.state not in 'draft':
            raise UserError(_('You cannot delete the verification created.'))
        super(EmployeeVerification, self).unlink()
