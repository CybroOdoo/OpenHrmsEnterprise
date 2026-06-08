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

from datetime import timedelta
from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestHrCustody(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Test Employee',
        })
        cls.property = cls.env['custody.property'].create({
            'name': 'Laptop',
            'property_selection': 'empty',
        })

    def _create_custody(self):
        """Create test custody."""
        return self.env['hr.custody'].create({
            'employee': self.employee.id,
            'custody_name': self.property.id,
            'purpose': 'Testing',
            'date_request': fields.Date.today(),
            'return_date': fields.Date.today() + timedelta(days=5),
        })

    def test_sequence_generation(self):
        """Test custody sequence."""
        custody = self._create_custody()
        self.assertTrue(
            custody.name
        )

    def test_validate_return_date(self):
        """Test return date validation."""
        with self.assertRaises(ValidationError):
            self.env['hr.custody'].create({
                'employee': self.employee.id,
                'custody_name': self.property.id,
                'purpose': 'Testing',
                'date_request': fields.Date.today(),
                'return_date': fields.Date.today() - timedelta(days=1),
            })

    def test_approve_custody(self):
        """Test custody approval."""
        custody = self._create_custody()
        custody.approve()
        self.assertEqual(
            custody.state,
            'approved'
        )

    def test_return_custody(self):
        """Test custody return."""
        custody = self._create_custody()
        custody.approve()
        custody.set_to_return()
        self.assertEqual(
            custody.state,
            'returned'
        )

    def test_change_custody_name(self):
        """Test custody onchange."""
        custody = self.env['hr.custody'].new({
            'custody_name': self.property.id,
        })
        custody.change_custody_name()
        self.assertFalse(
            custody.property_type
        )

    def test_employee_custody_count(self):
        """Test custody count."""
        self._create_custody()
        self.employee._custody_count()
        self.assertEqual(
            self.employee.custody_count,
            1
        )

    def test_employee_equipment_count(self):
        """Test equipment count."""
        custody = self._create_custody()
        custody.approve()
        self.employee._equipment_count()
        self.assertEqual(
            self.employee.equipment_count,
            1
        )

    def test_custody_view(self):
        """Test custody action."""
        self._create_custody()
        action = self.employee.custody_view()
        self.assertEqual(
            action['res_model'],
            'hr.custody'
        )

    def test_equipment_view(self):
        """Test equipment action."""
        custody = self._create_custody()
        custody.approve()
        action = self.employee.equipment_view()
        self.assertEqual(
            action['res_model'],
            'custody.property'
        )

    def test_property_onchange_product(self):
        """Test product onchange."""
        product = self.env['product.product'].create({
            'name': 'Office Laptop',
        })
        property_rec = self.env['custody.property'].new({
            'product_id': product.id,
        })
        property_rec._onchange_product_id()
        self.assertEqual(
            property_rec.name,
            product.name
        )

    def test_contract_renewal_proceed(self):
        """Test custody renewal."""
        custody = self._create_custody()
        wizard = self.env['contract.renewal'].with_context(
            custody_id=custody.id
        ).create({
            'returned_date': fields.Date.today() + timedelta(days=10),
        })
        wizard.proceed()
        custody.invalidate_recordset()
        self.assertTrue(
            custody.renew_return_date
        )
        self.assertEqual(
            custody.state,
            'to_approve'
        )

    def test_custody_refuse_reason(self):
        """Test custody refusal."""
        custody = self._create_custody()
        wizard = self.env['custody.refuse'].with_context(
            model_id='hr.custody',
            reject_id=custody.id
        ).create({
            'reason': 'Rejected',
        })
        wizard.send_reason()
        custody.invalidate_recordset()
        self.assertEqual(
            custody.state,
            'rejected'
        )
        self.assertEqual(
            custody.rejected_reason,
            'Rejected'
        )