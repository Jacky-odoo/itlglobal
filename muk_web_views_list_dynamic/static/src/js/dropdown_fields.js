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

odoo.define('muk_web_views_list_dynamic.FieldDropdown', function (require) {
"use strict";

var core = require('web.core');
var config = require('web.config');
var session = require('web.session');
var field_registry = require('web.field_registry');

var Widget = require('web.Widget');

var QWeb = core.qweb;
var _t = core._t;

var FieldDropdown = Widget.extend({
    template: 'muk_web_views_list_dynamic.FieldsDropdown',
    fieldTemplate: 'muk_web_views_list_dynamic.FieldsDropdownItems',
    events: {
        'click .o_menu_item': '_onFieldClick',
        'click .mk_list_customize_fields_reset': '_onResetClick',
        'input .mk_list_customize_fields_search input': '_onSearch',
    },
    init: function (parent, fields, info, arch, viewClass) {
    	this._super.apply(this, arguments);
    	var arch_fields = _.object(_.map(arch, function(val, seq) {
        	return [val.attrs.name, seq] 
        }));
    	this.fields = _.chain(fields).map(function(value, key){
    		var modifiers = key in info && info[key].modifiers;
    		return {
				id: key,
				data: value,
				invisible: false,
				description: value.string,
				original: key in info,
				active: !(!modifiers || modifiers.invisible || modifiers.column_invisible),
			}; 
		}).map(function(field, index, list) {
			field['sequence'] = field.id in arch_fields ?
					arch_fields[field.id] : (list.length + index + 1);
        	return field;
        }).sortBy(function(field) {
        	return field.sequence;
        }).value();
        this.info = $.extend(true, {}, info);
        this.arch = _.object(_.map(arch, function(value) {
        	return [value.attrs.name, value] 
        }));
        this.viewClass = viewClass;
    },
    start: function () {
        this.$menu = this.$('.o_dropdown_menu');
        this.$search = this.$('.mk_list_customize_fields_search');
        this.$menu.sortable({
			axis: "y",
			items: "> .o_menu_item",
			containment: "parent",
			update: this._onFieldMove.bind(this),
        }); 
    }, 
    updateFieldActiveStatus: function (ids) {
        _.each(this.fields, function (field) {
        	field.active = _.contains(ids, field.id);
        });
    	this._updateDropdownFields();
    },
    _updateDropdownFields: function() {
    	this.$menu.find('.o_menu_item').remove();
    	this.$search.after($(QWeb.render(this.fieldTemplate, {
    		widget: this
    	})));
    },
    _onFieldMove: function(event) {
        var keys = {};
        _.each(event.target.children, function (element, sequence) {
        	var $element = $(element);
        	if ($element.hasClass("o_menu_item")) {
        		keys[$element.data('id')] = sequence;
        	}
        });
        this.fields = _.sortBy(this.fields, function(field) { 
        	return keys[field.id];
        });
        this._updateDropdownFields();
        this._notifyFieldsUpdate();
    },
    _onFieldClick: function (event) {
        event.preventDefault();
        event.stopPropagation();
        var field = _.findWhere(this.fields, {
        	id: $(event.currentTarget).data('id')
        });
        field.active = !field.active;
        this._updateDropdownFields();
        this._notifyFieldsUpdate();
    },
    _onResetClick: function (event) {
    	this.call('local_storage', 'removeItem', this.viewClass._getViewStorageKey());
    	location.reload();
    },
    _onSearch: _.debounce(function(event) {
    	var search = $(event.currentTarget).val().toLowerCase();
    	_.each(this.fields, function (field) {
        	field.invisible = search ? field.description.toLowerCase().indexOf(search) < 0 : false;
        });
    	this._updateDropdownFields();
    }, 250),
    _notifyFieldsUpdate: function (event) {
    	this.trigger_up('update_fields', this._getData());
    },
    _getData: function() {
    	return {
			arch: this._getArch(),
			info: this._getFieldInfo(),
	    };
    },
    _getArch: function () {
    	var arch = [];
    	_.each(this.fields, function (field) {
    		if (field.id in this.info) {
    			arch.push($.extend(true, this.arch[field.id], {
    				attrs: {
    					modifiers: {
    						invisible: !field.active,
    						column_invisible: !field.active,
    					},
						invisible: !field.active,
    				},
    			}));
    		} else if (field.active && !(field.id in this.arch)) {
    			arch.push({
	    			tag: "field",
    				attrs: {
    					modifiers: {
    						readonly: field.data.readonly,
            				required: field.data.required,
    					},
    					name: field.id,
    				},
	    			children: [],
    			});
    		}
    	}, this);
    	return arch;
    },   
    _getFieldInfo: function () {
    	var info = {};
    	_.each(this.fields, function (field) {
    		if (field.id in this.info) {
    			info[field.id] = $.extend(true, {}, this.info[field.id]);
    			info[field.id].modifiers = _.extend({}, info[field.id].modifiers, {
    				column_invisible: !field.active,
    				invisible: !field.active,
    			});
    		} else if (field.active && !(field.id in this.info)) {
    			info[field.id] = this.viewClass._processField('list', field.data, {
        			modifiers: {
        				readonly: field.data.readonly,
        				required: field.data.required,
        			},
    				name: field.id,
    			});
    		}
    	}, this);
    	return info;
    }, 
});

return FieldDropdown;

});
