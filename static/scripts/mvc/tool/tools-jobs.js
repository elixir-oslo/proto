define(["utils/utils","mvc/tool/tools-template"],function(a,b){return{submit:function(c,d,e){var f=this,g={tool_id:d.id,tool_version:d.version,inputs:c.data.create()};return c.trigger("reset"),this._validation(c,g)?(Galaxy.emit.debug("tools-jobs::submit()","Validation complete.",g),void a.request({type:"POST",url:galaxy_config.root+"api/tools",data:g,success:function(a){e&&e(),c.$el.replaceWith(b.success(a)),f._refreshHdas()},error:function(a){if(e&&e(),Galaxy.emit.debug("tools-jobs::submit","Submission failed.",a),a&&a.err_data){var d=c.data.matchResponse(a.err_data);for(var f in d){c.highlight(f,d[f]);break}}else c.modal.show({title:"Job submission failed",body:a&&a.err_msg||b.error(g),buttons:{Close:function(){c.modal.hide()}}})}})):(Galaxy.emit.debug("tools-jobs::submit()","Submission canceled. Validation failed."),void(e&&e()))},_validation:function(a,b){var c=b.inputs,d=-1,e=null;for(var f in c){var g=c[f],h=a.data.match(f),i=a.field_list[h],j=a.input_list[h];if(h&&j&&i){if(!j.optional&&null==g)return a.highlight(h),!1;if(g&&g.batch){var k=g.values.length,l=null;if(k>0&&(l=g.values[0]&&g.values[0].src),l)if(null===e)e=l;else if(e!==l)return a.highlight(h,"Please select either dataset or dataset list fields for all batch mode fields."),!1;if(-1===d)d=k;else if(d!==k)return a.highlight(h,"Please make sure that you select the same number of inputs for all batch mode fields. This field contains <b>"+k+"</b> selection(s) while a previous field contains <b>"+d+"</b>."),!1}}else Galaxy.emit.debug("tools-jobs::_validation()","Retrieving input objects failed.")}return!0},_refreshHdas:function(a,b){parent.Galaxy&&parent.Galaxy.currHistoryPanel&&parent.Galaxy.currHistoryPanel.refreshContents(a,b)}}});
//# sourceMappingURL=../../../maps/mvc/tool/tools-jobs.js.map