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
    'name': 'Enterprise  HRMS Biometric Device Integration',
    'version': '15.0.1.0.0',
    'summary': """Integrating Biometric Device With HR Attendance (Face + Thumb)""",
    'description': 'This module integrates Odoo with the biometric device(Model: ZKteco uFace 202)',
    'category': 'Generic Modules/Human Resources',
     'live_test_url': 'https://youtu.be/RHSHHU7nzTo',
    'author': 'Cybrosys Techno Solutions, Mostafa Shokiel,Open HRMS',
    'live_test_url': 'https://youtu.be/RHSHHU7nzTo',
    'company': 'Cybrosys Techno Solutions',
    'website': "http://www.openhrms.com",
    'maintainer': 'Cybrosys Techno Solutions',
    'depends': ['base_setup', 'hr_attendance'],
    'data': [
        'security/ir.model.access.csv',
        'views/zk_machine_view.xml',
        'views/zk_machine_attendance_view.xml',
        'data/download_data.xml'
    ],
    'images': ['static/description/banner.png'],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
}
