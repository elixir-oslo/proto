!function(e){function t(o){function v(){t(n)}var n=o.data||o;switch(o.type){case"mouseenter":n.dist2=0,n.event=o,o.type="hoverstart",!1!==e.event.dispatch.call(this,o)&&(n.elem=this,e.event.add(this,"mousemove",t,n),n.timer=setTimeout(v,n.delay));break;case"mousemove":n.dist2+=Math.pow(o.pageX-n.event.pageX,2)+Math.pow(o.pageY-n.event.pageY,2),n.event=o;break;case"mouseleave":clearTimeout(n.timer),n.hovered?(o.type="hoverend",e.event.dispatch.call(this,o),n.hovered--):e.event.remove(n.elem,"mousemove",t);break;default:n.dist2<=Math.pow(n.speed*(n.delay/1e3),2)?(e.event.remove(n.elem,"mousemove",t),n.event.type="hover",!1!==e.event.dispatch.call(n.elem,n.event)&&n.hovered++):n.timer=setTimeout(v,n.delay),n.dist2=0}}e.fn._hover=e.fn.hover,e.fn.hover=function(e,t,o){return o&&this.bind("hoverstart",e),t&&this.bind("hoverend",o||t),e?this.bind("hover",o?t:e):this.trigger("hover")};var o=e.event.special.hover={delay:100,speed:100,setup:function(v){v=e.extend({speed:o.speed,delay:o.delay,hovered:0},v||{}),e.event.add(this,"mouseenter mouseleave",t,v)},teardown:function(){e.event.remove(this,"mouseenter mouseleave",t)}}}(jQuery);