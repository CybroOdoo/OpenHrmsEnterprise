# -*- coding: utf-8 -*-
######################################################################################
#
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Copyright (C) 2022-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
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

{
    'name': 'Enterprise Open HRMS Employee Insurance',
    'version': '16.0.1.0.0',
    'summary': """Employee Insurance Management for Open HRMS.""",
    'description': """Manages insurance amounts for employees to be deducted from salary""",
    'category': 'Generic Modules/Human Resources',
    'author': 'Cybrosys Techno solutions,Open HRMS',
    'live_test_url': 'https://youtu.be/OBwVroUPspw',
    'maintainer': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'website': 'https://www.openhrms.com',
    'depends': [
                'base', 'hr', 'ent_hr_payroll_extension', 'ent_hr_employee_updation',
                ],
    'data': [
        'security/ir.model.access.csv',
        'security/e_hr_insurance_security.xml',
        'views/e_employee_insurance_view.xml',
        'views/e_insurance_salary_stucture.xml',
        'views/e_policy_management.xml',
              ],
    'images': ['static/description/banner.png'],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
}
