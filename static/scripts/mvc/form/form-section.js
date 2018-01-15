define("mvc/form/form-section",["exports","utils/utils","mvc/ui/ui-misc","mvc/ui/ui-portlet","mvc/form/form-repeat","mvc/form/form-input","mvc/form/form-parameters"],function(e,t,i,a,n,d,s){"use strict";function l(e){return e&&e.__esModule?e:{default:e}}Object.defineProperty(e,"__esModule",{value:!0});var p=l(t),o=(l(i),l(a)),r=l(n),c=l(d),u=l(s),h=Backbone.View.extend({initialize:function(e,t){this.app=e,this.inputs=t.inputs,this.parameters=new u.default,this.setElement($("<div/>")),this.render()},render:function(){var e=this;this.$el.empty(),_.each(this.inputs,function(t){e.add(t)})},add:function(e){var t=jQuery.extend(!0,{},e);switch(t.id=e.id=p.default.uid(),this.app.input_list[t.id]=t,t.type){case"conditional":this._addConditional(t);break;case"repeat":this._addRepeat(t);break;case"section":this._addSection(t);break;default:this._addRow(t)}},_addConditional:function(e){var t=this;e.test_param.id=e.id,this.app.model.get("sustain_conditionals")&&(e.test_param.disabled=!0);var i=this._addRow(e.test_param);i.model&&i.model.set("onchange",function(i){var a=t.app.data.matchCase(e,i);for(var n in e.cases){var d=e.cases[n],s=t.$("#"+e.id+"-section-"+n),l=!1;for(var p in d.inputs)if(!d.inputs[p].hidden){l=!0;break}n==a&&l?s.fadeIn("fast"):s.hide()}t.app.trigger("change")});for(var a in e.cases){var n=new h(this.app,{inputs:e.cases[a].inputs});this._append(n.$el.addClass("ui-form-section"),e.id+"-section-"+a)}i.trigger("change")},_addRepeat:function(e){function t(t){var d=e.id+"-section-"+a++,s=new h(i.app,{inputs:t});n.add({id:d,$el:s.$el,ondel:function(){n.del(d),i.app.trigger("change")}})}for(var i=this,a=0,n=new r.default.View({title:e.title||"Repeat",min:e.min,max:e.max,onnew:function(){t(e.inputs),i.app.trigger("change")}}),d=_.size(e.cache),s=0;s<Math.max(Math.max(d,e.min||0),e.default||0);s++)t(s<d?e.cache[s]:e.inputs);this.app.model.get("sustain_repeats")&&n.hideOptions();var l=new c.default(this.app,{label:e.title||e.name,help:e.help,field:n});this._append(l.$el,e.id)},_addSection:function(e){var t=new o.default.View({title:e.title||e.name,cls:"ui-portlet-section",collapsible:!0,collapsible_button:!0,collapsed:!e.expanded});t.append(new h(this.app,{inputs:e.inputs}).$el),t.append($("<div/>").addClass("ui-form-info").html(e.help)),this.app.on("expand",function(e){t.$("#"+e).length>0&&t.expand()}),this._append(t.$el,e.id)},_addRow:function(e){var t=this,i=e.id;e.onchange=e.onchange||function(){t.app.trigger("change",i)};var a=this.parameters.create(e);this.app.field_list[i]=a;var n=new c.default(this.app,{name:e.name,label:e.hide_label?"":e.label||e.name,value:e.value,text_value:e.text_value,collapsible_value:e.collapsible_value,collapsible_preview:e.collapsible_preview,help:e.help,argument:e.argument,disabled:e.disabled,color:e.color,style:e.style,backdrop:e.backdrop,hidden:e.hidden,fixed:e.fixed,field:a});return this.app.element_list[i]=n,this._append(n.$el,e.id),a},_append:function(e,t){this.$el.append(e.addClass("section-row").attr("id",t))}});e.default={View:h}});