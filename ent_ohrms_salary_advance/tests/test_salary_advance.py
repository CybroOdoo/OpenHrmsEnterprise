###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2026-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Aysha Shalin (odoo@cybrosys.com)
#
#    This program is under the terms of the Odoo Proprietary License v1.0 (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the
#    Software or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NON INFRINGEMENT. IN NO EVENT SHALL
#    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
###############################################################################

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestSalaryAdvance(TransactionCase):
    """Test suite for the salary.advance model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Company
        cls.company = cls.env.ref('base.main_company')

        # Create a partner with an address (needed for advance approval)
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Employee Partner',
            'street': '123 Test St',
            'city': 'Test City',
            'country_id': cls.env.ref('base.us').id,
        })

        # Department
        cls.department = cls.env['hr.department'].create({
            'name': 'Test Department',
            'company_id': cls.company.id,
        })

        # Employee
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Test Employee',
            'department_id': cls.department.id,
            'company_id': cls.company.id,
            'address_id': cls.partner.id,
        })

        # Currency
        cls.currency = cls.company.currency_id

        # Journals
        cls.bank_journal = cls.env['account.journal'].search(
            [('type', '=', 'bank'), ('company_id', '=', cls.company.id)],
            limit=1
        )
        if not cls.bank_journal:
            cls.bank_journal = cls.env['account.journal'].create({
                'name': 'Test Bank Journal',
                'type': 'bank',
                'code': 'TBNK',
                'company_id': cls.company.id,
            })

        # Accounts for journal entries
        cls.account_type_asset = cls.env.ref(
            'account.data_account_type_current_assets', raise_if_not_found=False
        )
        cls.debit_account = cls.env['account.account'].search(
            [('account_type', 'in', ['asset_current', 'asset_non_current']),
             ('company_ids', 'in', cls.company.id)],
            limit=1
        )
        cls.credit_account = cls.env['account.account'].search(
            [('account_type', 'in', ['liability_current', 'liability_non_current']),
             ('company_ids', 'in', cls.company.id)],
            limit=1
        )

        # Fallback: create accounts if not found
        if not cls.debit_account:
            cls.debit_account = cls.env['account.account'].create({
                'name': 'Test Debit Account',
                'code': 'TDEBIT',
                'account_type': 'asset_current',
                'company_ids': [(4, cls.company.id)],
            })
        if not cls.credit_account:
            cls.credit_account = cls.env['account.account'].create({
                'name': 'Test Credit Account',
                'code': 'TCREDIT',
                'account_type': 'liability_current',
                'company_ids': [(4, cls.company.id)],
            })

    def _create_advance(self, **kwargs):
        """Helper to create a salary advance with sensible defaults."""
        vals = {
            'employee_id': self.employee.id,
            'advance': 500.0,
            'currency_id': self.currency.id,
            'company_id': self.company.id,
        }
        vals.update(kwargs)
        return self.env['salary.advance'].create(vals)

    # ─────────────────────────────────────────────────────────────────────────
    # 1. Creation tests
    # ─────────────────────────────────────────────────────────────────────────

    def test_create_salary_advance_default_state(self):
        """A newly created advance must be in 'draft' state."""
        advance = self._create_advance()
        self.assertEqual(advance.state, 'draft',
                         "New advance should have 'draft' state.")

    def test_create_salary_advance_sequence_generated(self):
        """Sequence (name) should be auto-assigned on creation."""
        advance = self._create_advance()
        self.assertTrue(advance.name,
                        "Advance name/sequence should be set after creation.")
        self.assertNotEqual(advance.name, 'Adv/',
                            "Name should not remain as the default 'Adv/'.")

    def test_create_salary_advance_with_reason(self):
        """Advance with an optional reason field should save correctly."""
        advance = self._create_advance(reason='Emergency family expense')
        self.assertEqual(advance.reason, 'Emergency family expense')

    def test_create_salary_advance_defaults_currency(self):
        """Currency should default to the company currency."""
        advance = self._create_advance()
        self.assertEqual(advance.currency_id, self.currency)

    def test_create_salary_advance_defaults_company(self):
        """Company should default to the current user's company."""
        advance = self._create_advance()
        self.assertEqual(advance.company_id, self.company)

    def test_create_multiple_advances_unique_sequences(self):
        """Multiple advances must receive unique sequence numbers."""
        adv1 = self._create_advance()
        adv2 = self._create_advance()
        self.assertNotEqual(adv1.name, adv2.name,
                            "Each advance must have a unique sequence name.")

    # ─────────────────────────────────────────────────────────────────────────
    # 2. State-transition action tests
    # ─────────────────────────────────────────────────────────────────────────

    def test_action_submit_to_manager(self):
        """action_submit_to_manager should move state to 'submit'."""
        advance = self._create_advance()
        advance.action_submit_to_manager()
        self.assertEqual(advance.state, 'submit')

    def test_action_cancel(self):
        """action_cancel should move state to 'cancel' from any state."""
        advance = self._create_advance()
        advance.action_cancel()
        self.assertEqual(advance.state, 'cancel')

    def test_action_reject(self):
        """action_reject should move state to 'reject'."""
        advance = self._create_advance()
        advance.action_reject()
        self.assertEqual(advance.state, 'reject')

    # ─────────────────────────────────────────────────────────────────────────
    # 3. action_approve_request (HR manager) – error-path tests
    # ─────────────────────────────────────────────────────────────────────────

    def test_approve_request_raises_without_address(self):
        """Approval should raise UserError when employee has no address."""
        employee_no_addr = self.env['hr.employee'].create({
            'name': 'No Address Employee',
            'company_id': self.company.id,
        })
        advance = self._create_advance(employee_id=employee_no_addr.id)
        with self.assertRaises(UserError):
            advance.action_approve_request()

    def test_approve_request_raises_without_contract(self):
        """Approval should raise UserError when employee has no contract."""
        # Employee has address but no contract → has_contract=False
        advance = self._create_advance()
        # Force has_contract to False to trigger the error
        advance.has_contract = False
        with self.assertRaises(UserError):
            advance.action_approve_request()

    def test_approve_request_raises_advance_exceeds_wage(self):
        """Approval should raise UserError when advance > wage and exceed_condition=False."""
        advance = self._create_advance(advance=99999.0)
        # Simulate a contract with a low wage
        advance.has_contract = True
        advance.contract_wage = 1000.0
        advance.exceed_condition = False
        with self.assertRaises(UserError):
            advance.action_approve_request()

    # ─────────────────────────────────────────────────────────────────────────
    # 4. action_approve_request_acc_dept (Accounting) – error-path tests
    # ─────────────────────────────────────────────────────────────────────────

    def test_acc_approve_raises_missing_debit_credit_journal(self):
        """Accounting approval must raise UserError if debit/credit/journal missing."""
        advance = self._create_advance()
        # Do not set debit_id, credit_id, journal_id
        with self.assertRaises(UserError):
            advance.action_approve_request_acc_dept()

    def test_acc_approve_raises_zero_advance(self):
        """Accounting approval must raise UserError when advance amount is 0."""
        advance = self._create_advance(advance=0.0)
        advance.debit_id = self.debit_account.id
        advance.credit_id = self.credit_account.id
        advance.journal_id = self.bank_journal.id
        with self.assertRaises(UserError):
            advance.action_approve_request_acc_dept()

    def test_acc_approve_creates_journal_entry_and_sets_state(self):
        """Successful accounting approval creates an account.move and sets state='approve'."""
        advance = self._create_advance()
        advance.debit_id = self.debit_account.id
        advance.credit_id = self.credit_account.id
        advance.journal_id = self.bank_journal.id

        advance.action_approve_request_acc_dept()

        self.assertEqual(advance.state, 'approve',
                         "State should be 'approve' after accounting approval.")
        # Check that a journal entry was created with this advance as reference
        move = self.env['account.move'].search([('ref', '=', advance.name)],
                                               limit=1)
        self.assertTrue(move.exists(),
                        "An account.move entry should be created on approval.")

    # ─────────────────────────────────────────────────────────────────────────
    # 5. Compute field tests
    # ─────────────────────────────────────────────────────────────────────────

    def test_compute_contract_data_no_employee(self):
        """Without an employee, contract computed fields should be falsy."""
        advance = self.env['salary.advance'].new({
            'advance': 100.0,
            'currency_id': self.currency.id,
            'company_id': self.company.id,
        })
        # employee_id is not set; trigger compute manually
        advance._compute_contract_data()
        self.assertFalse(advance.has_contract)
        self.assertEqual(advance.contract_wage, 0.0)

    def test_compute_contract_data_employee_with_no_contract(self):
        """Employee without an active contract version → has_contract=False."""
        employee = self.env['hr.employee'].create({
            'name': 'No Contract Employee',
            'company_id': self.company.id,
            'address_id': self.partner.id,
        })
        advance = self._create_advance(employee_id=employee.id)
        # Recompute
        advance._compute_contract_data()
        self.assertFalse(advance.has_contract)
        self.assertEqual(advance.contract_wage, 0.0)
        self.assertFalse(advance.contract_struct_id)

    # ─────────────────────────────────────────────────────────────────────────
    # 6. Onchange tests
    # ─────────────────────────────────────────────────────────────────────────

    def test_onchange_employee_id_sets_department(self):
        """_onchange_employee_id should return the employee's department."""
        employee = self.env['hr.employee'].create({
            'name': 'Dept Employee',
            'department_id': self.department.id,
            'company_id': self.company.id,
            'address_id': self.partner.id,
        })
        advance = self.env['salary.advance'].new({
            'employee_id': employee.id,
            'advance': 100.0,
            'currency_id': self.currency.id,
            'company_id': self.company.id,
        })
        result = advance._onchange_employee_id()
        self.assertIn('value', result)
        self.assertEqual(result['value']['department_id'],
                         self.department.id,
                         "Department should be set from the employee.")

    def test_onchange_company_id_returns_journal_domain(self):
        """onchange_company_id should return a domain restricting journals to the company."""
        advance = self.env['salary.advance'].new({
            'employee_id': self.employee.id,
            'advance': 100.0,
            'currency_id': self.currency.id,
            'company_id': self.company.id,
        })
        result = advance.onchange_company_id()
        self.assertIn('domain', result)
        self.assertIn('journal_id', result['domain'])
        expected_domain = [('company_id', '=', self.company.id)]
        self.assertEqual(result['domain']['journal_id'], expected_domain)

    # ─────────────────────────────────────────────────────────────────────────
    # 7. Field validation / data integrity
    # ─────────────────────────────────────────────────────────────────────────

    def test_advance_amount_stored_correctly(self):
        """The advance float field should persist exactly as supplied."""
        advance = self._create_advance(advance=1234.56)
        self.assertAlmostEqual(advance.advance, 1234.56, places=2)

    def test_department_stored_correctly(self):
        """Department stored on the advance should match what was set."""
        advance = self._create_advance(department_id=self.department.id)
        self.assertEqual(advance.department_id, self.department)

    def test_payment_method_stored(self):
        """payment_method_id should be stored when provided."""
        advance = self._create_advance(payment_method_id=self.bank_journal.id)
        self.assertEqual(advance.payment_method_id, self.bank_journal)

    def test_exceed_condition_default_false(self):
        """exceed_condition should default to False."""
        advance = self._create_advance()
        self.assertFalse(advance.exceed_condition)

    def test_exceed_condition_can_be_set_true(self):
        """exceed_condition can be explicitly set to True."""
        advance = self._create_advance(exceed_condition=True)
        self.assertTrue(advance.exceed_condition)

    # ─────────────────────────────────────────────────────────────────────────
    # 8. Duplicate-approval-in-same-month guard
    # ─────────────────────────────────────────────────────────────────────────

    def test_acc_approve_raises_duplicate_in_same_month(self):
        """A second accounting approval in the same month should raise UserError."""
        # Create and fully approve the first advance
        adv1 = self._create_advance()
        adv1.debit_id = self.debit_account.id
        adv1.credit_id = self.credit_account.id
        adv1.journal_id = self.bank_journal.id
        adv1.action_approve_request_acc_dept()
        self.assertEqual(adv1.state, 'approve')

        # Now try to approve a second advance for the same employee/same month
        adv2 = self._create_advance()
        adv2.debit_id = self.debit_account.id
        adv2.credit_id = self.credit_account.id
        adv2.journal_id = self.bank_journal.id
        with self.assertRaises(UserError):
            adv2.action_approve_request_acc_dept()
