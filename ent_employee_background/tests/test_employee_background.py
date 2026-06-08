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
import base64
from unittest.mock import patch
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import UserError, ValidationError


@tagged('post_install', '-at_install')
class TestEmployeeBackground(TransactionCase):
    """Test suite for the Employee Background Verification module.

    Covers:
    - res.partner          : verification_agent field
    - employee.verification: field defaults, sequence, state machine,
                             create/unlink constraints, action methods,
                             _check_file_type constraint
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Agency partner (verification agent)
        cls.agency = cls.env['res.partner'].create({
            'name': 'Test Verification Agency',
            'email': 'agency@test.com',
            'verification_agent': True,
        })

        # Non-agent partner
        cls.normal_partner = cls.env['res.partner'].create({
            'name': 'Normal Partner',
            'email': 'normal@test.com',
            'verification_agent': False,
        })

        # Employee
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Test Employee BG',
        })

        # A valid PDF attachment (minimal valid base64 PDF)
        cls.pdf_attachment = cls.env['ir.attachment'].create({
            'name': 'resume.pdf',
            'datas': base64.b64encode(b'%PDF-1.4 test content'),
            'mimetype': 'application/pdf',
        })

        # A non-PDF attachment
        cls.png_attachment = cls.env['ir.attachment'].create({
            'name': 'photo.png',
            'datas': base64.b64encode(b'fake png data'),
            'mimetype': 'image/png',
        })

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------
    def _make_verification(self, **kwargs):
        """Create a draft employee.verification with sensible defaults."""
        vals = {
            'employee_id': self.employee.id,
            'agency_id': self.agency.id,
        }
        vals.update(kwargs)
        return self.env['employee.verification'].create(vals)

    # ==================================================================
    # 1.  res.partner — verification_agent field
    # ==================================================================
    def test_01_verification_agent_true(self):
        """verification_agent must be True when explicitly set."""
        self.assertTrue(self.agency.verification_agent)

    def test_02_verification_agent_default_false(self):
        """verification_agent must default to False on a regular partner."""
        self.assertFalse(self.normal_partner.verification_agent)

    def test_03_verification_agent_toggleable(self):
        """verification_agent must be writable — can be toggled on/off."""
        self.normal_partner.verification_agent = True
        self.assertTrue(self.normal_partner.verification_agent)
        self.normal_partner.verification_agent = False
        self.assertFalse(self.normal_partner.verification_agent)

    # ==================================================================
    # 2.  employee.verification — field defaults and sequence
    # ==================================================================
    def test_04_create_assigns_sequence_name(self):
        """A new record must receive a non-empty sequence ID in 'name'."""
        rec = self._make_verification()
        self.assertTrue(rec.name, "name must be set by sequence on create.")
        self.assertNotEqual(rec.name, '/')

    def test_05_default_state_is_draft(self):
        """Newly created records must start in 'draft' state."""
        rec = self._make_verification()
        self.assertEqual(rec.state, 'draft')

    def test_06_default_assigned_date_is_today(self):
        """assigned_date must default to today."""
        from odoo import fields as odoo_fields
        rec = self._make_verification()
        self.assertEqual(rec.assigned_date, odoo_fields.Date.today())

    def test_07_assigned_by_is_current_user(self):
        """assigned_by_id must default to the current user."""
        rec = self._make_verification()
        self.assertEqual(rec.assigned_by_id, self.env.user)

    def test_08_company_defaults_to_current_company(self):
        """company_id must default to the current company."""
        rec = self._make_verification()
        self.assertEqual(rec.company_id, self.env.company)

    def test_09_employee_id_stored(self):
        """employee_id must be stored correctly."""
        rec = self._make_verification()
        self.assertEqual(rec.employee_id, self.employee)

    def test_10_agency_id_stored(self):
        """agency_id must be stored correctly."""
        rec = self._make_verification()
        self.assertEqual(rec.agency_id, self.agency)

    def test_11_expected_date_writable(self):
        """expected_date must be writable and readable."""
        from odoo import fields as odoo_fields
        today = odoo_fields.Date.today()
        rec = self._make_verification(expected_date=today)
        self.assertEqual(rec.expected_date, today)

    def test_12_multiple_records_get_unique_names(self):
        """Each new record must receive a unique sequence name."""
        rec1 = self._make_verification()
        rec2 = self._make_verification()
        self.assertNotEqual(rec1.name, rec2.name)

    # ==================================================================
    # 3.  _check_file_type constraint
    # ==================================================================
    def test_13_pdf_attachment_allowed(self):
        """PDF attachments must be accepted without raising."""
        try:
            rec = self._make_verification(
                resume_uploaded_ids=[(4, self.pdf_attachment.id)])
        except ValidationError:
            self.fail("PDF attachment raised ValidationError unexpectedly.")
        self.assertIn(self.pdf_attachment, rec.resume_uploaded_ids)

    def test_14_non_pdf_attachment_raises_validation_error(self):
        """Non-PDF attachments must raise a ValidationError."""
        with self.assertRaises(ValidationError):
            self._make_verification(
                resume_uploaded_ids=[(4, self.png_attachment.id)])

    def test_15_multiple_pdf_attachments_allowed(self):
        """Multiple PDF attachments must all be accepted."""
        pdf2 = self.env['ir.attachment'].create({
            'name': 'resume2.pdf',
            'datas': base64.b64encode(b'%PDF-1.4 second doc'),
            'mimetype': 'application/pdf',
        })
        rec = self._make_verification(resume_uploaded_ids=[
            (4, self.pdf_attachment.id),
            (4, pdf2.id),
        ])
        self.assertEqual(len(rec.resume_uploaded_ids), 2)

    # ==================================================================
    # 4.  unlink constraint
    # ==================================================================
    def test_16_unlink_draft_record_allowed(self):
        """Deleting a draft record must succeed."""
        rec = self._make_verification()
        self.assertEqual(rec.state, 'draft')
        rec_id = rec.id
        rec.unlink()
        self.assertFalse(self.env['employee.verification'].browse(rec_id).exists())

    def test_17_unlink_assigned_record_raises(self):
        """Deleting an assigned (non-draft) record must raise UserError."""
        rec = self._make_verification()
        rec.state = 'assign'
        with self.assertRaises(UserError):
            rec.unlink()

    def test_18_unlink_submitted_record_raises(self):
        """Deleting a submitted record must raise UserError."""
        rec = self._make_verification()
        rec.state = 'submit'
        with self.assertRaises(UserError):
            rec.unlink()

    # ==================================================================
    # 5.  action_assign_agency
    # ==================================================================
    def test_19_assign_agency_no_agency_raises(self):
        """action_assign_agency must raise UserError when agency_id is empty."""
        rec = self.env['employee.verification'].create({
            'employee_id': self.employee.id,
        })
        with self.assertRaises(UserError):
            rec.action_assign_agency()

    def test_20_assign_agency_no_address_no_resume_raises(self):
        """action_assign_agency must raise UserError when neither address
        nor resume attachments are present."""
        rec = self._make_verification()
        # Ensure no address and no attachments
        rec.address_id = False
        rec.resume_uploaded_ids = [(5, 0, 0)]
        with self.assertRaises(UserError):
            rec.action_assign_agency()

    def test_21_assign_agency_with_resume_sets_state_assign(self):
        """action_assign_agency with a PDF resume must move state to 'assign'."""
        rec = self._make_verification(
            resume_uploaded_ids=[(4, self.pdf_attachment.id)]
        )
        rec.address_id = False

        template = self.env.ref(
            'ent_employee_background.assign_agency_email_template'
        )

        with patch.object(type(template), 'send_mail', return_value=True):
            rec.action_assign_agency()

        self.assertEqual(rec.state, 'assign')

    def test_22_assign_agency_with_address_sets_state_assign(self):
        """action_assign_agency with an address must move state to 'assign'."""
        rec = self._make_verification()

        rec.address_id = self.agency.id
        rec.resume_uploaded_ids = [(5, 0, 0)]

        template = self.env.ref(
            'ent_employee_background.assign_agency_email_template'
        )

        with patch.object(type(template), 'send_mail', return_value=True):
            rec.action_assign_agency()

        self.assertEqual(rec.state, 'assign')

    # ==================================================================
    # 6.  action_download_attachment
    # ==================================================================
    def test_23_download_attachment_no_attachment_raises(self):
        """action_download_attachment must raise UserError when no
        agency_attachment_id is set."""
        rec = self._make_verification()
        self.assertFalse(rec.agency_attachment_id)
        with self.assertRaises(UserError):
            rec.action_download_attachment()

    def test_24_download_attachment_returns_act_url(self):
        """action_download_attachment must return an act_url action dict
        when agency_attachment_id is set."""
        rec = self._make_verification()
        rec.agency_attachment_id = self.pdf_attachment.id
        result = rec.action_download_attachment()
        self.assertEqual(result.get('type'), 'ir.actions.act_url')
        self.assertIn(str(self.pdf_attachment.id), result.get('url', ''))

    def test_25_download_attachment_url_contains_filename(self):
        """The download URL must contain the attachment filename."""
        rec = self._make_verification()
        rec.agency_attachment_id = self.pdf_attachment.id
        result = rec.action_download_attachment()
        self.assertIn(self.pdf_attachment.name, result.get('url', ''))

    # ==================================================================
    # 7.  state field and transitions
    # ==================================================================
    def test_26_state_draft_to_assign_transition(self):
        """State must go from 'draft' to 'assign' via action_assign_agency."""
        rec = self._make_verification(
            resume_uploaded_ids=[(4, self.pdf_attachment.id)]
        )

        self.assertEqual(rec.state, 'draft')

        template = self.env.ref(
            'ent_employee_background.assign_agency_email_template'
        )

        with patch.object(type(template), 'send_mail', return_value=True):
            rec.action_assign_agency()

        self.assertEqual(rec.state, 'assign')

    def test_27_state_can_be_set_to_submit(self):
        """State must accept 'submit' value (set by portal on completion)."""
        rec = self._make_verification()
        rec.state = 'submit'
        self.assertEqual(rec.state, 'submit')

    def test_28_state_values_are_valid_selection(self):
        """All three selection values draft/assign/submit must be valid."""
        rec = self._make_verification()
        for state_val in ('draft', 'assign', 'submit'):
            rec.state = state_val
            self.assertEqual(rec.state, state_val)

    # ==================================================================
    # 8.  description_by_agency and agency_attachment_id fields
    # ==================================================================
    def test_29_description_by_agency_writable(self):
        """description_by_agency must be writable and readable."""
        rec = self._make_verification()
        rec.description_by_agency = 'Verification passed.'
        self.assertEqual(rec.description_by_agency, 'Verification passed.')

    def test_30_agency_attachment_id_writable(self):
        """agency_attachment_id must be writable and point to correct record."""
        rec = self._make_verification()
        rec.agency_attachment_id = self.pdf_attachment.id
        self.assertEqual(rec.agency_attachment_id, self.pdf_attachment)

    def test_31_field_check_default_false(self):
        """field_check must default to False."""
        rec = self._make_verification()
        self.assertFalse(rec.field_check)

    def test_32_field_check_writable(self):
        """field_check must be settable to True."""
        rec = self._make_verification()
        rec.field_check = True
        self.assertTrue(rec.field_check)

    # ==================================================================
    # 9.  res.partner domain filter support
    # ==================================================================
    def test_33_only_agents_appear_in_agent_domain(self):
        """Partners with verification_agent=True must be findable by domain."""
        agents = self.env['res.partner'].search(
            [('verification_agent', '=', True)])
        self.assertIn(self.agency, agents)
        self.assertNotIn(self.normal_partner, agents)

    def test_34_non_agents_excluded_from_agent_domain(self):
        """Partners with verification_agent=False must not appear in agent search."""
        non_agents = self.env['res.partner'].search(
            [('verification_agent', '=', False),
             ('id', 'in', [self.agency.id, self.normal_partner.id])])
        self.assertIn(self.normal_partner, non_agents)
        self.assertNotIn(self.agency, non_agents)

    # ==================================================================
    # 10.  copy=False on name and resume_uploaded_ids
    # ==================================================================
    def test_35_copy_generates_new_sequence_name(self):
        """Copying a record must generate a fresh sequence name, not copy
        the original."""
        rec = self._make_verification()
        copied = rec.copy()
        self.assertNotEqual(copied.name, rec.name,
                            "copy() must assign a new sequence, not duplicate the name.")

    def test_36_copy_does_not_carry_resume_attachments(self):
        """copy=False on resume_uploaded_ids means copied record has no resumes."""
        rec = self._make_verification(
            resume_uploaded_ids=[(4, self.pdf_attachment.id)])
        copied = rec.copy()
        self.assertFalse(copied.resume_uploaded_ids,
                         "resume_uploaded_ids must not be copied to new record.")