/**********************************************************************************
*
*    Copyright (c) 2017-2019 MuK IT GmbH.
*
*    This file is part of MuK Dynamic List Views 
*    (see https://mukit.at).
*
*    MuK Proprietary License v1.0
*
*    This software and associated files (the "Software") may only be used 
*    (executed, modified, executed after modifications) if you have
*    purchased a valid license from MuK IT GmbH.
*
*    The above permissions are granted for a single database per purchased 
*    license. Furthermore, with a valid license it is permitted to use the
*    software on other databases as long as the usage is limited to a testing
*    or development environment.
*
*    You may develop modules based on the Software or that use the Software
*    as a library (typically by depending on it, importing it and using its
*    resources), but without copying any source code or material from the
*    Software. You may distribute those modules under the license of your
*    choice, provided that this license is compatible with the terms of the 
*    MuK Proprietary License (For example: LGPL, MIT, or proprietary licenses
*    similar to this one).
*
*    It is forbidden to publish, distribute, sublicense, or sell copies of
*    the Software or modified copies of the Software.
*
*    The above copyright notice and this permission notice must be included
*    in all copies or substantial portions of the Software.
*
*    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
*    OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
*    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
*    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
*    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
*    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
*    DEALINGS IN THE SOFTWARE.
*
**********************************************************************************/

odoo.define('muk_web_views_list_dynamic.controller', function (require) {
"use strict";

var core = require('web.core');
var session = require('web.session');
var framework = require('web.framework');
var field_registry = require('web.field_registry');

var ListController = require('web.ListController');

var FieldDropdown = require('muk_web_views_list_dynamic.FieldDropdown');

var _t = core._t;
var QWeb = core.qweb;

ListController.include({
	custom_events: _.extend({}, ListController.prototype.custom_events, {
        update_fields: '_updateFields',
    }),
    init: function (parent, model, renderer, params) {
    	this._super.apply(this, arguments);
    	this.viewClass = params.viewClass;
    },
	renderButtons: function ($node) {
		this._super.apply(this, arguments);
		if (this.$buttons) {
        	this.$mode_switch = $(QWeb.render('muk_web_utils.switch', {
        		id: 'mk-list-switch-' + this.controllerID,
        		label: _t("Editable"),
        	}));
        	this.$buttons.find('.mk_list_button_switch').html(this.$mode_switch);
        	this.$mode_switch.on('change', 'input[type="checkbox"]', this._onSwitchMode.bind(this));
        	this.$mode_switch.find('input[type="checkbox"]').prop('checked', !!this.editable);
        	this.$list_customize = this.$buttons.find('.mk_list_button_customize');
        	this.fields_dropdown = this._createFieldsDropdown();
            this.fields_dropdown.appendTo(this.$list_customize);
        }
    },
    _getViewStorageKey: function () {
    	return this.viewClass._getViewStorageKey();
    },
    _setViewStorageData: function (data) {
    	this.call('local_storage', 'setItem', this._getViewStorageKey(), data);
    },
    _createFieldsDropdown: function () {
		var state = this.model.get(this.handle); 
		return new FieldDropdown(this, state.fields, state.fieldsInfo[this.viewType], 
				this.renderer.arch.children, this.viewClass);
    },
    _updateFields: function (event) {
    	event.stopPropagation();
    	var state = this.model.get(this.handle); 
		state.fieldsInfo[this.viewType] = event.data.info;
    	this.renderer.arch.children = event.data.arch;  
    	this._setViewStorageData(this.renderer.arch);
    	this.update({}, {reload: true})
    },
    _updateButtons: function (mode) {
    	this._super.apply(this, arguments);
    	if (this.$mode_switch) {
        	this.$mode_switch.find('input[type="checkbox"]').prop('checked', !!this.editable);
    	}
    },
    _onSwitchMode: function(event) {
    	var editable = $(event.currentTarget).is(':checked');
    	if(editable) {
    		this.editable = 'top';
    		this.renderer.editable = this.editable;
    		this.renderer.isMultiEditable = this.editable;
    	} else {
    		this.editable = false;
    		this.renderer.editable = false;
    	}
    	this.update({}, {reload: true}).then(this._updateButtons.bind(this, 'readonly'));
    }

 });

});
