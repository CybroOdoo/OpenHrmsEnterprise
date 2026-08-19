# -*- coding: utf-8 -*-
######################################################################################
#
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Copyright (C) 2026-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
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
from unittest.mock import patch

from odoo.tests import tagged, TransactionCase


@tagged("-at_install", "post_install")
class TestOvertimeType(TransactionCase):

    def test_compute_leave_type_ids_uses_duration_type(self):
        overtime_type = self.env["overtime.type"].new({
            "name": "Leave Overtime",
            "type": "leave",
            "duration_type": "days",
        })

        with patch.object(type(self.env["hr.leave.type"]), "search", return_value=self.env["hr.leave.type"].browse([])) as search_mock:
            overtime_type._compute_leave_type_ids()

        search_mock.assert_called_once()
        self.assertIn(("request_unit", "=", "day"), search_mock.call_args.args[0])
        self.assertFalse(overtime_type.leave_type_ids)
