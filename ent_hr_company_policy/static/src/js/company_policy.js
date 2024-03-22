/** @odoo-module **/

import { HrDashboard } from "@ent_hrms_dashboard/js/hrms_dashboard";
//var AbstractAction = require('web.AbstractAction');
//var core = require('web.core');
import { session } from "@web/session";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

patch(HrDashboard.prototype, {
//const CompanyPolicy = HrDashboard.extend({
       events: {
        'click .hr_leave_request_approve': 'leaves_to_approve',
        'click .hr_leave_allocations_approve': 'leave_allocations_to_approve',
        'click .hr_timesheets': 'hr_timesheets',
        'click .hr_job_application_approve': 'job_applications_to_approve',
        'click .hr_payslip':'hr_payslip',
        'click .hr_contract':'hr_contract',
        'click .hr_employee':'hr_employee',
        'click .oe_company_policy': 'company_policy',
        'click .leaves_request_month':'leaves_request_month',
        'click .leaves_request_today':'leaves_request_today',
        "click .o_hr_attendance_sign_in_out_icon": function() {
            this.$('.o_hr_attendance_sign_in_out_icon').attr("disabled", "disabled");
            this.update_attendance();
        },
        'click #broad_factor_pdf': 'generate_broad_factor_report',
    },

    company_policy() {

        var self = this;
        self.action.doAction({
            name: _t("Company Policy"),
            type: 'ir.actions.act_window',
            res_model: 'res.company.policy',
            view_mode: 'form',
            views: [[false, 'form']],
            context: {
                'default_company_id': session.company_id,
            },
            target: 'new'
        });

      },
});
