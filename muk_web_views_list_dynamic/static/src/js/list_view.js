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

odoo.define('muk_web_views_list_dynamic.view', function (require) {
"use strict";

var core = require('web.core');
var session = require('web.session');
var framework = require('web.framework');
var field_registry = require('web.field_registry');

var ListView = require('web.ListView');
var LocalStorage = require('web.local_storage');

var _t = core._t;
var QWeb = core.qweb;

ListView.include({
    init: function (viewInfo, params) {
    	this._super.apply(this, arguments);
    	this.controllerParams.viewClass = this;
    },  
    _getViewStorageKey: function (fieldsView) {
    	var fv = fieldsView || this.fieldsView;
    	var type = fv.type === 'tree' ? 'list' : fv.type;
    	return type + ',' + fv.view_id + ',' + session.uid;
    },  
    _getViewStorageData: function (key) {
    	var value = LocalStorage.getItem(key);
    	return value && JSON.parse(value);
    }, 
    _processFieldsView: function (fieldsView, viewType) {
    	var res = this._super.apply(this, arguments);
    	var storageKey = this._getViewStorageKey(fieldsView);
    	var storageData = this._getViewStorageData(storageKey);
    	if (fieldsView.view_id && storageData) {
        	res.arch = storageData;
            this._processArch(res.arch, res);
    	}
        return res;
    },
});

});
