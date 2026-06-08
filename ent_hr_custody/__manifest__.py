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

{
    'name': 'Enterprise Open HRMS Custody',
    'version': '19.0.1.0.0',
    'category': 'Human Resources',
    'summary': """Manage the company properties when it is in the 
    custody of an employee""",
    'description': 'Manage the company properties when it is in the '
                   'custody of an employee',
    'live_test_url':
        'https://www.youtube.com/watch?v=keh3ttj9kws&feature=youtu.be',
    'author': "Cybrosys Techno Solutions,Open HRMS",
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.openhrms.com",
    'depends': ['base', 'hr', 'mail', 'ent_hr_employee_updation', 'product',
                'stock'],
    'data': [
        'security/custody_property_security.xml',
        'security/hr_custody_security.xml',
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'data/ir_sequence_data.xml',
        'data/mail_template_data.xml',
        'wizard/custody_refuse_views.xml',
        'wizard/contract_renewal_views.xml',
        'views/hr_custody_views.xml',
        'views/hr_employee_views.xml',
        'views/custody_property_views.xml',
        'report/report_custody_views.xml',
    ],
    'demo': ['demo/ent_hr_custody_demo.xml'],
    'images': ['static/description/banner.jpg'],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': True,
}
