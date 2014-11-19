/*
 * eXeLearning Style Designer 1.0
 * By Ignacio Gros (http://www.gros.es/) for eXeLearning (http://exelearning.net/)
 * Creative Commons Attribution-ShareAlike (http://creativecommons.org/licenses/by-sa/3.0/)
 */
var $designer = {
	init : function(){	
		var sd_style = "base";
		var sd_href= window.location.href;
		var sd_href_parts = sd_href.split("?style=");
		if (sd_href_parts.length==2) sd_style = sd_href_parts[1];
		this.styleId = sd_style;
	},
	isBrowserCompatible : function(){
		var n = navigator.userAgent.toLowerCase();
		n = (n.indexOf('msie') != -1) ? parseInt(n.split('msie')[1]) : false;
		if (n && n<7) return false;
		return true;
	},	
	printStyles : function(type){
		document.write('<link rel="stylesheet" type="text/css" href="/style/base.css" />');
		document.write('<link rel="stylesheet" type="text/css" href="/style/'+this.styleId+'/content.css" id="base-content-css" />');
		document.write('<style type="text/css" id="my-content-css"></style>');
		if (type=='website') {
			document.write('<link rel="stylesheet" type="text/css" href="/style/'+this.styleId+'/nav.css" id="base-nav-css" />');
			document.write('<style type="text/css" id="my-nav-css"></style>');
		}
	},
	printExtraBody : function(){
		this.disableAllLinks();
		document.write('<script type="text/javascript" src="/style/'+this.styleId+'/_my_js.js"></script>');
		if (this.isBrowserCompatible()) this.openDesigner();
		else alert($i18n.Browser_Incompatible);
	},
	disableAllLinks : function(){
		$("A","#content").click(function(){
			return false;
		});
	},
	openDesigner : function(){
		// return false;
		// Settings
		var mypage="/tools/style-designer/";
		var myname="eXeLearning_Style_Designer";
		var w=650;
		var h=500;
		var features="";
		// / Settings
		var win = null;
		var winl = (screen.width-w)/2;
		var wint = (screen.height-h)/2;
		if (winl < 0) winl = 0;
		if (wint < 0) wint = 0;
		var settings = 'height=' + h + ',';
		settings += 'width=' + w + ',';
		settings += 'top=' + wint + ',';
		settings += 'left=' + winl + ',';
		settings += features;
		win = window.open(mypage,myname,settings);
		if (win) win.focus();
	}
}
$designer.init();