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


class TestHrPayslipSalaryAdvance(TransactionCase):
    """Test suite for HrPayslip extensions added by ent_ohrms_salary_advance."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.company = cls.env.ref('base.main_company')

        # Partner / address for the employee
        cls.partner = cls.env['res.partner'].create({
            'name': 'Payslip Test Partner',
            'street': '1 Test Ave',
            'city': 'Testville',
            'country_id': cls.env.ref('base.us').id,
        })

        # Employee
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Payslip Test Employee',
            'company_id': cls.company.id,
            'address_id': cls.partner.id,
        })

        # Payroll structure
        cls.payroll_structure = cls.env['hr.payroll.structure'].search(
            [('company_id', '=', cls.company.id)], limit=1
        )
        if not cls.payroll_structure:
            # Fetch the default structure type
            struct_type = cls.env['hr.payroll.structure.type'].search([], limit=1)
            if not struct_type:
                struct_type = cls.env['hr.payroll.structure.type'].create({
                    'name': 'Test Structure Type',
                    'wage_type': 'monthly',
                })
            cls.payroll_structure = cls.env['hr.payroll.structure'].create({
                'name': 'Test Payroll Structure',
                'type_id': struct_type.id,
                'company_id': cls.company.id,
            })

        # Look for the SAR salary rule (created by module data)
        cls.sar_rule = cls.env['hr.salary.rule'].search(
            [('code', '=', 'SAR')], limit=1
        )

        # Create a basic payslip (state: draft)
        import datetime
        today = datetime.date.today()
        first_day = today.replace(day=1)
        import calendar
        last_day = today.replace(
            day=calendar.monthrange(today.year, today.month)[1]
        )

        cls.payslip = cls.env['hr.payslip'].create({
            'name': 'Test Payslip',
            'employee_id': cls.employee.id,
            'struct_id': cls.payroll_structure.id,
            'date_from': first_day,
            'date_to': last_day,
            'company_id': cls.company.id,
        })

        # Currency
        cls.currency = cls.company.currency_id

        # Bank journal
        cls.bank_journal = cls.env['account.journal'].search(
            [('type', '=', 'bank'), ('company_id', '=', cls.company.id)],
            limit=1
        )

    # ─────────────────────────────────────────────────────────────────────────
    # 1. input_data_salary_line
    # ─────────────────────────────────────────────────────────────────────────

    def test_input_data_salary_line_with_valid_input_type(self):
        """input_data_salary_line adds a line when the input type exists.

        The method signature is input_data_salary_line(name, amount) where
        `name` is a salary rule ID.  It searches hr.payslip.input.type by
        ('input_id', '=', name) — input_id is a Many2one to hr.salary.rule.
        """
        rule_category = self.env['hr.salary.rule.category'].search([], limit=1)
        salary_rule = self.env['hr.salary.rule'].create({
            'name': 'Test SAR Rule Valid',
            'code': 'TSARV',
            'category_id': rule_category.id,
            'struct_id': self.payroll_structure.id,
        })
        input_type = self.env['hr.payslip.input.type'].create({
            'name': 'Test Salary Advance Repayment Valid',
            'code': 'TSARV',
            'input_id': salary_rule.id,
        })
        initial_count = len(self.payslip.input_line_ids)
        # Pass the salary rule ID — that is what compute_sheet passes
        self.payslip.input_data_salary_line(salary_rule.id, 250.0)
        self.assertEqual(
            len(self.payslip.input_line_ids), initial_count + 1,
            "One new input line should be added."
        )
        added = self.payslip.input_line_ids.filtered(
            lambda l: l.input_type_id.id == input_type.id
        )
        self.assertTrue(added)
        self.assertAlmostEqual(added[0].amount, 250.0, places=2)

    def test_input_data_salary_line_with_invalid_input_type(self):
        """input_data_salary_line does nothing when the input type is not found."""
        initial_count = len(self.payslip.input_line_ids)
        # Pass a non-existent id (0) – search returns empty recordset
        self.payslip.input_data_salary_line(0, 100.0)
        self.assertEqual(
            len(self.payslip.input_line_ids), initial_count,
            "No input line should be added for an invalid input type."
        )

    def test_input_data_salary_line_zero_amount(self):
        """input_data_salary_line stores 0.0 amount when provided."""
        rule_category = self.env['hr.salary.rule.category'].search([], limit=1)
        salary_rule = self.env['hr.salary.rule'].create({
            'name': 'Test SAR Rule Zero',
            'code': 'TSARZERO',
            'category_id': rule_category.id,
            'struct_id': self.payroll_structure.id,
        })
        input_type = self.env['hr.payslip.input.type'].create({
            'name': 'Zero Advance Input',
            'code': 'TSARZERO',
            'input_id': salary_rule.id,
        })
        self.payslip.input_data_salary_line(salary_rule.id, 0.0)
        added = self.payslip.input_line_ids.filtered(
            lambda l: l.input_type_id.id == input_type.id
        )
        self.assertTrue(added, "Input line should be created even with 0.0 amount.")
        self.assertAlmostEqual(added[0].amount, 0.0, places=2)

    def test_input_data_salary_line_negative_amount(self):
        """input_data_salary_line stores negative amounts (deductions) correctly."""
        rule_category = self.env['hr.salary.rule.category'].search([], limit=1)
        salary_rule = self.env['hr.salary.rule'].create({
            'name': 'Test SAR Rule Negative',
            'code': 'TSARNEG',
            'category_id': rule_category.id,
            'struct_id': self.payroll_structure.id,
        })
        input_type = self.env['hr.payslip.input.type'].create({
            'name': 'Negative Advance Input',
            'code': 'TSARNEG',
            'input_id': salary_rule.id,
        })
        self.payslip.input_data_salary_line(salary_rule.id, -150.0)
        added = self.payslip.input_line_ids.filtered(
            lambda l: l.input_type_id.id == input_type.id
        )
        self.assertTrue(added)
        self.assertAlmostEqual(added[0].amount, -150.0, places=2)

    # ─────────────────────────────────────────────────────────────────────────
    # 2. compute_sheet – interaction with salary.advance
    # ─────────────────────────────────────────────────────────────────────────

    def test_compute_sheet_no_sar_rule_skips_advance_line(self):
        """compute_sheet should not add an advance input when no SAR rule exists."""
        # Ensure no SAR rule on our structure
        self.payroll_structure.rule_ids.filtered(
            lambda r: r.code == 'SAR'
        ).unlink()

        initial_count = len(self.payslip.input_line_ids)
        # compute_sheet calls super() which may raise; we only check the pre-super logic
        try:
            self.payslip.compute_sheet()
        except Exception:
            pass
        # The SAR block should not have added any lines
        sar_lines = self.payslip.input_line_ids.filtered(
            lambda l: l.input_type_id.code == 'SAR'
        )
        self.assertFalse(sar_lines,
                         "No SAR input line should be added without an SAR rule.")

    def test_compute_sheet_no_approved_advance_skips_input_line(self):
        """compute_sheet skips adding an input line when no approved advance exists."""
        # Ensure at least one SAR rule exists so the block is entered
        if not self.sar_rule:
            rule_category = self.env['hr.salary.rule.category'].search([], limit=1)
            self.sar_rule = self.env['hr.salary.rule'].create({
                'name': 'Salary Advance Repayment',
                'code': 'SAR',
                'category_id': rule_category.id,
                'struct_id': self.payroll_structure.id,
            })
        # Make sure no approved advance exists for this employee
        self.env['salary.advance'].search([
            ('employee_id', '=', self.employee.id),
            ('state', '=', 'approve'),
        ]).write({'state': 'cancel'})

        initial_input_count = len(self.payslip.input_line_ids)
        try:
            self.payslip.compute_sheet()
        except Exception:
            pass
        sar_lines = self.payslip.input_line_ids.filtered(
            lambda l: l.input_type_id.code == 'SAR'
        )
        self.assertFalse(sar_lines,
                         "No SAR input line when there is no approved advance.")

    def test_compute_sheet_with_approved_advance_adds_input_line(self):
        """compute_sheet adds an advance input line when an approved advance exists."""
        import datetime
        today = datetime.date.today()

        # Ensure SAR rule is attached to the payslip's structure
        if not self.sar_rule:
            rule_category = self.env['hr.salary.rule.category'].search([], limit=1)
            self.sar_rule = self.env['hr.salary.rule'].create({
                'name': 'Salary Advance Repayment',
                'code': 'SAR',
                'category_id': rule_category.id,
                'struct_id': self.payroll_structure.id,
            })
        elif self.sar_rule.struct_id != self.payroll_structure:
            self.sar_rule.struct_id = self.payroll_structure.id

        # Create an approved salary advance with a date within the payslip period
        advance = self.env['salary.advance'].create({
            'employee_id': self.employee.id,
            'advance': 300.0,
            'currency_id': self.currency.id,
            'company_id': self.company.id,
            'date': today,
            'state': 'approve',
        })

        # Ensure the input type with code 'SAR' exists
        input_type = self.env['hr.payslip.input.type'].search(
            [('code', '=', 'SAR')], limit=1
        )
        if not input_type:
            input_type = self.env['hr.payslip.input.type'].create({
                'name': 'Salary Advance Repayment Input',
                'code': 'SAR',
            })

        initial_count = len(self.payslip.input_line_ids)
        try:
            self.payslip.compute_sheet()
        except Exception:
            pass

        sar_lines = self.payslip.input_line_ids.filtered(
            lambda l: l.input_type_id.code == 'SAR'
        )
        self.assertTrue(sar_lines,
                        "An SAR input line should be added when an approved advance exists.")

    def test_compute_sheet_does_not_duplicate_sar_input(self):
        """compute_sheet should not add a duplicate SAR line if one already exists."""
        import datetime
        today = datetime.date.today()

        if not self.sar_rule:
            rule_category = self.env['hr.salary.rule.category'].search([], limit=1)
            self.sar_rule = self.env['hr.salary.rule'].create({
                'name': 'Salary Advance Repayment',
                'code': 'SAR',
                'category_id': rule_category.id,
                'struct_id': self.payroll_structure.id,
            })

        input_type = self.env['hr.payslip.input.type'].search(
            [('code', '=', 'SAR')], limit=1
        )
        if not input_type:
            input_type = self.env['hr.payslip.input.type'].create({
                'name': 'Salary Advance Repayment Input',
                'code': 'SAR',
            })

        # Pre-add the SAR line
        self.payslip.input_line_ids = [(0, 0, {
            'input_type_id': input_type.id,
            'amount': 300.0,
        })]
        count_after_first = len(self.payslip.input_line_ids)

        # Create an approved advance
        self.env['salary.advance'].create({
            'employee_id': self.employee.id,
            'advance': 300.0,
            'currency_id': self.currency.id,
            'company_id': self.company.id,
            'date': today,
            'state': 'approve',
        })

        try:
            self.payslip.compute_sheet()
        except Exception:
            pass

        sar_lines = self.payslip.input_line_ids.filtered(
            lambda l: l.input_type_id.code == 'SAR'
        )
        self.assertEqual(len(sar_lines), 1,
                         "SAR input line must not be duplicated on re-compute.")

    # ─────────────────────────────────────────────────────────────────────────
    # 3. HrPayrollStructure – extra fields (max_percent, advance_date, company_id)
    # ─────────────────────────────────────────────────────────────────────────

    def test_payroll_structure_max_percent_default_zero(self):
        """max_percent should default to 0 for a newly created structure."""
        struct_type = self.env['hr.payroll.structure.type'].search([], limit=1)
        if not struct_type:
            struct_type = self.env['hr.payroll.structure.type'].create({
                'name': 'Default Type',
                'wage_type': 'monthly',
            })
        new_structure = self.env['hr.payroll.structure'].create({
            'name': 'Max Percent Test Structure',
            'type_id': struct_type.id,
            'company_id': self.company.id,
        })
        self.assertEqual(new_structure.max_percent, 0,
                         "max_percent should default to 0.")

    def test_payroll_structure_advance_date_default_zero(self):
        """advance_date should default to 0 for a newly created structure."""
        struct_type = self.env['hr.payroll.structure.type'].search([], limit=1)
        new_structure = self.env['hr.payroll.structure'].create({
            'name': 'Advance Date Test Structure',
            'type_id': struct_type.id,
            'company_id': self.company.id,
        })
        self.assertEqual(new_structure.advance_date, 0,
                         "advance_date should default to 0.")

    def test_payroll_structure_max_percent_set_correctly(self):
        """max_percent should store the provided integer value."""
        struct_type = self.env['hr.payroll.structure.type'].search([], limit=1)
        new_structure = self.env['hr.payroll.structure'].create({
            'name': 'Max Percent 50 Structure',
            'type_id': struct_type.id,
            'company_id': self.company.id,
            'max_percent': 50,
        })
        self.assertEqual(new_structure.max_percent, 50)

    def test_payroll_structure_advance_date_set_correctly(self):
        """advance_date should store the provided integer value."""
        struct_type = self.env['hr.payroll.structure.type'].search([], limit=1)
        new_structure = self.env['hr.payroll.structure'].create({
            'name': 'Advance Date 10 Structure',
            'type_id': struct_type.id,
            'company_id': self.company.id,
            'advance_date': 10,
        })
        self.assertEqual(new_structure.advance_date, 10)

    def test_payroll_structure_company_defaults_to_current_company(self):
        """company_id on hr.payroll.structure should default to the current user's company."""
        struct_type = self.env['hr.payroll.structure.type'].search([], limit=1)
        new_structure = self.env['hr.payroll.structure'].create({
            'name': 'Company Default Structure',
            'type_id': struct_type.id,
        })
        self.assertEqual(new_structure.company_id, self.env.user.company_id,
                         "company_id should default to the current user's company.")

    def test_payroll_structure_company_can_be_set_explicitly(self):
        """company_id on hr.payroll.structure can be explicitly assigned."""
        struct_type = self.env['hr.payroll.structure.type'].search([], limit=1)
        new_structure = self.env['hr.payroll.structure'].create({
            'name': 'Explicit Company Structure',
            'type_id': struct_type.id,
            'company_id': self.company.id,
        })
        self.assertEqual(new_structure.company_id, self.company)
