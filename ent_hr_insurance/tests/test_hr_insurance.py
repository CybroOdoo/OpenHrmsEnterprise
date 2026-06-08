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
from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestHRInsurance(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.employee = cls.env['hr.employee'].create({
            'name': 'Insurance Employee',
        })

        cls.policy = cls.env['insurance.policy'].create({
            'name': 'Medical Insurance',
        })

    # ----------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------

    def _create_insurance(self, **vals):
        defaults = {
            'employee_id': self.employee.id,
            'policy_id': self.policy.id,
            'amount': 1000,
            'sum_insured': 100000,
            'policy_coverage': 'monthly',
        }
        defaults.update(vals)
        return self.env['hr.insurance'].create(defaults)

    # ==========================================================
    # Insurance Policy
    # ==========================================================

    def test_01_policy_name_stored(self):
        self.assertEqual(self.policy.name, 'Medical Insurance')

    def test_02_policy_company_default(self):
        self.assertEqual(
            self.policy.company_id,
            self.env.company
        )

    # ==========================================================
    # HR Insurance Defaults
    # ==========================================================

    def test_03_create_insurance(self):
        insurance = self._create_insurance()
        self.assertTrue(insurance)

    def test_04_employee_stored(self):
        insurance = self._create_insurance()
        self.assertEqual(insurance.employee_id, self.employee)

    def test_05_policy_stored(self):
        insurance = self._create_insurance()
        self.assertEqual(insurance.policy_id, self.policy)

    def test_06_default_policy_coverage(self):
        insurance = self._create_insurance()
        self.assertEqual(
            insurance.policy_coverage,
            'monthly'
        )

    def test_07_default_company(self):
        insurance = self._create_insurance()
        self.assertEqual(
            insurance.company_id,
            self.env.company
        )

    def test_08_default_date_from(self):
        insurance = self._create_insurance()
        self.assertEqual(
            insurance.date_from,
            fields.Date.today()
        )

    # ==========================================================
    # State Computation
    # ==========================================================

    def test_09_state_active(self):
        insurance = self._create_insurance()
        insurance._compute_state()

        self.assertEqual(
            insurance.state,
            'active'
        )

    def test_10_state_expired(self):
        insurance = self._create_insurance(
            date_from=fields.Date.today() - relativedelta(months=3),
            date_to=fields.Date.today() - relativedelta(days=1)
        )

        insurance._compute_state()

        self.assertEqual(
            insurance.state,
            'expired'
        )

    def test_11_state_active_future_end_date(self):
        insurance = self._create_insurance(
            date_to=fields.Date.today() + relativedelta(days=10)
        )

        insurance._compute_state()

        self.assertEqual(
            insurance.state,
            'active'
        )

    # ==========================================================
    # Onchange Coverage
    # ==========================================================

    def test_12_onchange_monthly_sets_date(self):
        insurance = self._create_insurance()

        insurance.policy_coverage = 'monthly'
        insurance._onchange_policy_coverage()

        self.assertTrue(insurance.date_to)

    def test_13_onchange_yearly_sets_date(self):
        insurance = self._create_insurance()

        insurance.policy_coverage = 'yearly'
        insurance._onchange_policy_coverage()

        expected = (
            fields.Date.today()
            + relativedelta(months=12)
        )

        self.assertEqual(
            insurance.date_to,
            expected
        )

    # ==========================================================
    # Percentage Validation
    # ==========================================================

    def test_14_percentage_zero_allowed(self):
        self.employee.insurance_percentage = 0
        self.employee._check_percentage()

    def test_15_percentage_hundred_allowed(self):
        self.employee.insurance_percentage = 100
        self.employee._check_percentage()

    def test_16_percentage_negative_not_allowed(self):
        with self.assertRaises(ValidationError):
            self.employee.write({
                'insurance_percentage': -1
            })

    def test_17_percentage_above_hundred_not_allowed(self):
        with self.assertRaises(ValidationError):
            self.employee.write({
                'insurance_percentage': 101
            })

    # ==========================================================
    # Deduction Computation
    # ==========================================================

    def test_18_monthly_deduction_calculation(self):
        self.employee.insurance_percentage = 0

        self._create_insurance(
            amount=1000,
            policy_coverage='monthly'
        )

        self.employee._compute_deduced_amount()

        self.assertEqual(
            self.employee.deduced_amount_per_year,
            12000
        )

        self.assertEqual(
            self.employee.deduced_amount_per_month,
            1000
        )

    def test_19_yearly_deduction_calculation(self):
        self.employee.insurance_percentage = 0

        self._create_insurance(
            amount=12000,
            policy_coverage='yearly'
        )

        self.employee._compute_deduced_amount()

        self.assertEqual(
            self.employee.deduced_amount_per_year,
            12000
        )

    def test_20_percentage_reduces_deduction(self):
        self.employee.insurance_percentage = 50

        self._create_insurance(
            amount=1000,
            policy_coverage='monthly'
        )

        self.employee._compute_deduced_amount()

        self.assertEqual(
            self.employee.deduced_amount_per_year,
            6000
        )

    def test_21_percentage_hundred_results_zero(self):
        self.employee.insurance_percentage = 100

        self._create_insurance(
            amount=1000,
            policy_coverage='monthly'
        )

        self.employee._compute_deduced_amount()

        self.assertEqual(
            self.employee.deduced_amount_per_year,
            0
        )

    def test_22_expired_policy_not_counted(self):
        self.employee.insurance_percentage = 0

        self._create_insurance(
            amount=1000,
            date_from=fields.Date.today() - relativedelta(months=3),
            date_to=fields.Date.today() - relativedelta(days=1)
        )

        self.employee._compute_deduced_amount()

        self.assertEqual(
            self.employee.deduced_amount_per_year,
            0
        )

    # ==========================================================
    # Multiple Policies
    # ==========================================================

    def test_23_multiple_monthly_policies(self):
        self.employee.insurance_percentage = 0

        self._create_insurance(amount=1000)
        self._create_insurance(amount=500)

        self.employee._compute_deduced_amount()

        self.assertEqual(
            self.employee.deduced_amount_per_year,
            18000
        )

    def test_24_multiple_policies_with_percentage(self):
        self.employee.insurance_percentage = 25

        self._create_insurance(amount=1000)
        self._create_insurance(amount=1000)

        self.employee._compute_deduced_amount()

        self.assertEqual(
            self.employee.deduced_amount_per_year,
            18000
        )

    # ==========================================================
    # Relationship Tests
    # ==========================================================

    def test_25_insurance_linked_to_employee(self):
        insurance = self._create_insurance()

        self.assertIn(
            insurance,
            self.employee.insurance_ids
        )

    def test_26_active_domain_returns_active_records(self):
        insurance = self._create_insurance()

        self.assertIn(
            insurance,
            self.employee.insurance_ids
        )