# -*- coding: utf-8 -*-
################################################################################
#
#    A part of OpenHRMS Project <https://www.openhrms.com>
#
#    Copyright (C) 2026-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
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
from odoo.tools import _
from odoo.exceptions import UserError, AccessError


class HrLeave(models.Model):
    """Inheriting hr.leave to add more fields and functions"""
    _inherit = 'hr.leave'

    leave_approvals_ids = fields.One2many('leave.validation.status',
                                          'holiday_id',
                                          string='Leave Validators',
                                          help="Leave approvals")
    is_multi_level_validation = fields.Boolean(
        string='Multiple Level Approval',
        compute="_compute_is_multi_level_validation",
        help="If checked then multi-level approval is necessary")
    is_button_visibility = fields.Boolean(
        default=True,
        compute="_compute_is_button_visibility",
        string='Button Visibility')

    @api.depends('holiday_status_id')
    def _compute_is_multi_level_validation(self):
        """Computes the multi level validation"""
        for rec in self:
            rec.is_multi_level_validation = (
                rec.holiday_status_id.leave_validation_type == 'multi')

    def _check_validator_access(self):
        """Restrict approve/refuse on multi-level leaves to the
        configured validators for that leave, or an HR administrator."""
        if self.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
            return
        for holiday in self:
            validator_ids = holiday.leave_approvals_ids.mapped(
                'validating_users_id').ids
            if self.env.uid not in validator_ids:
                raise AccessError(_(
                    'Only the assigned approvers or an HR administrator '
                    'can approve or refuse this leave request.'))

    def action_approve(self):
        """Multi-level leave types are restricted to configured
        validators/administrators and handled by this module's approval
        workflow. Other leave types keep Odoo's standard approval logic
        and access checks."""
        multi_recs = self.filtered(
            lambda l: l.holiday_status_id.leave_validation_type == 'multi')
        other_recs = self - multi_recs

        if other_recs:
            super(HrLeave, other_recs).action_approve()

        if multi_recs:
            multi_recs._check_validator_access()
            if any(holiday.state != 'confirm' for holiday in multi_recs):
                raise UserError(_(
                    'Leave request must be confirmed ("To Approve")'
                    ' in order to approve it.'))
            ohrmspro_vacation_project = self.sudo().env[
                'ir.module.module'].search(
                [('name', '=', 'ohrmspro_vacation_project')],
                limit=1).state
            if ohrmspro_vacation_project == 'installed':
                return self.env['hr.leave'].check_pending_task(multi_recs)
            else:
                return multi_recs.approval_check()
        return True

    def approval_check(self):
        """Check all leave validators approved the leave request. If all
        approved, change the current request stage to Approved."""
        current_employee = self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)], limit=1)
        for holiday in self:
            validation_obj = holiday.leave_approvals_ids.filtered(
                lambda v: v.validating_users_id.id == self.env.uid)
            validation_obj.is_validation_status = True
            approval_flag = all(
                v.is_validation_status for v in holiday.leave_approvals_ids)
            if approval_flag:
                if holiday.validation_type == 'both':
                    holiday.sudo().write(
                        {'state': 'validate1',
                         'first_approver_id': current_employee.id})
                else:
                    holiday.sudo()._action_validate()
                if not holiday.env.context.get('leave_fast_create'):
                    holiday.activity_update()
        return True

    def action_refuse(self):
        """Multi-level leave types are restricted to configured
        validators/administrators. Other leave types keep Odoo's
        standard refusal logic and access checks."""
        multi_recs = self.filtered(
            lambda l: l.holiday_status_id.leave_validation_type == 'multi')
        other_recs = self - multi_recs

        if other_recs:
            super(HrLeave, other_recs).action_refuse()

        if multi_recs:
            multi_recs._check_validator_access()
            current_employee = self.env['hr.employee'].search(
                [('user_id', '=', self.env.uid)], limit=1)
            for holiday in multi_recs:
                if holiday.state not in ['confirm', 'validate', 'validate1']:
                    raise UserError(_(
                        'Leave request must be confirmed '
                        'or validated in order to refuse it.'))
                if holiday.state == 'validate1':
                    holiday.sudo().write(
                        {'state': 'refuse',
                         'first_approver_id': current_employee.id})
                else:
                    holiday.sudo().write(
                        {'state': 'refuse',
                         'second_approver_id': current_employee.id})
                if holiday.meeting_id:
                    holiday.meeting_id.unlink()
                # linked_request_ids was removed in Odoo 19
                if hasattr(holiday, 'linked_request_ids'):
                    holiday.linked_request_ids.action_refuse()
            multi_recs._remove_resource_leave()
            multi_recs.activity_update()
            validation_obj = multi_recs.leave_approvals_ids.filtered(
                lambda v: v.validating_users_id.id == self.env.uid)
            validation_obj.is_validation_status = False
        return True

    def action_draft(self):
        """Reset all validation status to false when leave request
        set to draft stage"""
        for user in self.leave_approvals_ids:
            user.is_validation_status = False
        return super().action_draft()

    @api.onchange('holiday_status_id')
    def _onchange_holiday_status_id(self):
        """Update the list view and add new validators
        when leave type is changed in leave request form"""
        validators_list = []
        self.leave_approvals_ids = [(5, 0, 0)]
        for user in self.holiday_status_id.leave_validators_ids:
            validators_list.append((0, 0, {
                'validating_users_id': user.holiday_validators_id.id,
            }))
        self.leave_approvals_ids = validators_list

    def _get_approval_requests(self):
        """Action for Approvals menu item to show approval
        requests assigned to current user"""
        current_uid = self.env.uid
        hr_holidays = self.env['hr.leave'].search([('state', '=', 'confirm')])
        approval = []
        for req in hr_holidays:
            for user in req.leave_approvals_ids.filtered(
                    lambda l: l.validating_users_id.id == current_uid):
                approval.append(req.id)
        return {
            'domain': str([('id', 'in', approval)]),
            'view_mode': 'list,form',
            'res_model': 'hr.leave',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'name': _('Approvals'),
            'res_id': self.id,
            'target': 'current',
            'create': False,
            'edit': False,
        }

    @api.depends('holiday_status_id', 'leave_approvals_ids',
                 'leave_approvals_ids.is_validation_status', 'state')
    def _compute_is_button_visibility(self):
        """Show the Approve button (is_button_visibility=False) only when:
        - Leave type is multi-level
        - Leave state is 'confirm' (To Approve)
        - Current user is a validator who has NOT yet approved"""
        for rec in self:
            # Must be multi-level leave type
            if rec.holiday_status_id.leave_validation_type != 'multi':
                rec.is_button_visibility = True
                continue
            # Must be in 'confirm' state (To Approve)
            if rec.state != 'confirm':
                rec.is_button_visibility = True
                continue
            # Current user must be a validator who hasn't approved yet
            validator_entry = rec.leave_approvals_ids.filtered(
                lambda l: l.validating_users_id == self.env.user)
            if validator_entry and not validator_entry[0].is_validation_status:
                rec.is_button_visibility = False  # show Approve button
            else:
                rec.is_button_visibility = True   # hide Approve button


class LeaveValidationStatus(models.Model):
    """Model for leave validators and their status for each leave request"""
    _name = 'leave.validation.status'

    holiday_id = fields.Many2one('hr.leave', string="Holiday", help="Holiday")
    validating_users_id = fields.Many2one(
        'res.users', string='Leave Validators', help="Leave validators",
        domain="[('share','=',False)]")
    is_validation_status = fields.Boolean(
        string='Approve Status', readonly=True, default=False,
        tracking=True, help="Status of approval process")
    leave_comments = fields.Text(string='Comments',
                                 help="Comments for the validation")

    @api.onchange('validating_users_id')
    def _onchange_validating_users_id(self):
        """Prevent Changing leave validators from leave request form"""
        raise UserError(_(
            "Changing leave validators is not permitted. You can only change "
            "it from Leave Types Configuration"))