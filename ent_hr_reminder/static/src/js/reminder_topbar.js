odoo.define('ent_hr_reminder.reminder_topbar', function (require) {
"use strict";

var core = require('web.core');
var SystrayMenu = require('web.SystrayMenu');
var Widget = require('web.Widget');
var QWeb = core.qweb;
var rpc = require('web.rpc');
var ajax = require('web.ajax');
var reminder_menu = Widget.extend({
    template:'reminder_menu',

    events: {
        "click .dropdown-options": "reminder_active",
    },

    willStart: async function(){
        var self = this;
        this._super();
        self.all_reminder = [];
        await ajax.jsonRpc("/ent_hr_reminder/all_reminder", 'call',{}).
        then(function(all_reminder){
            self.all_reminder = all_reminder
        });
    },

    start: function(){
        this._super();
        this.$('.reminders_list').html(QWeb.render('reminder_menu_template',{
            values: this.all_reminder,
            widget: this
        }));
    },

    reminder_active: function(ev){

        var self = this;
        var value = $(ev.target).data('name');

        ajax.jsonRpc("/ent_hr_reminder/reminder_active", 'call',{'reminder_name':value})
        .then(function(reminder){
            self.reminder = reminder
            console.log('reminder on click selection',self.reminder)
             for (var i=0;i<1;i++){
                    var model = self.reminder[i]
                    console.log("model",model)

                    var date = self.reminder[i+2]
                    console.log("date",date)
                    var field = self.reminder[i+1]
                    console.log("field",field)

                    var id = self.reminder[i+6]
                    console.log("id",id)
                    var today = self.reminder[i+7]
                    console.log("today",today)
                     var type = self.reminder[i+8]
                    console.log("type",type)


                    if (self.reminder[i+2] == 'today'){
                        if (self.reminder[i+8]=='datetime')
                            return self.do_action({
                                type: 'ir.actions.act_window',
                                res_model: model,
                                view_mode: 'list',

                                domain: [[field,'>',today+" 00:00:00"],[field,'<',today + " 23:59:59"]],
                                views: [[false, 'list']],
                                target: 'new',})
                         else if(self.reminder[i+8]=='date')
                            return self.do_action({
                                type: 'ir.actions.act_window',
                                res_model: model,
                                view_mode: 'list',

                                domain: [[field,'=',today]],
                                views: [[false, 'list']],
                                target: 'new',})
                        }

                    else if (self.reminder[i+2] == 'set_date'){
                        return self.do_action({
                            type: 'ir.actions.act_window',
                            res_model: model,
                            view_mode: 'list',
                            domain: [[field, '=', self.reminder[i+3]]],
                            views: [[false, 'list']],
                            target: 'new',
                            })
                        }

                    else if (self.reminder[i+2] == 'set_period'){
                        return self.do_action({
                            type: 'ir.actions.act_window',
                            res_model: model,
                            view_mode: 'list',
                            domain: [[field, '<', self.reminder[i+5]],[field, '>', self.reminder[i+4]]],
                            views: [[false, 'list']],
                            target: 'new',
                            })
                            }

                        }
             });
        },
});

SystrayMenu.Items.push(reminder_menu);
});
