define([
	'jquery',
	'underscore',
	'backbone',
	'marionette',
	'translater',
	'config',
	'./lyt-camTrapModal',
	'./lyt-camTrapImageModel',
	'ez-plus',
  'backbone.marionette.keyShortcuts',
	'noty',
	'bootstrap-star-rating',


], function($, _, Backbone, Marionette, Translater, config , ModalView , CamTrapImageModel ,ezPlus, BckMrtKeyShortCut, noty, btstrp_star ) {

  'use strict';
  return Marionette.ItemView.extend({
		model: CamTrapImageModel,//ImageModel,
		keyShortcuts :{
			//'space': 'onClickImage',
		},
		events:{
			'click img':'clickFocus',
			'dblclick img': 'goFullScreen'
		},
		className : 'col-md-2 imageCamTrap',
		template : 'app/modules/monitoredSites/templates/tpl-image.html',

		clickFocus : function(e){
		this.$el.find('img').focus();
		if( e.ctrlKey) {
			console.log("LE FOCUS ET LE CTRL KEY");
		} else {
				var lastPosition = this.parent.currentPosition;
			if(lastPosition === null)
			lastPosition = 0;
			//this.parent.currentViewImg = this;
			//TODO fait bugguer la position pour le
			this.parent.currentPosition = this.parent.currentCollection.indexOf(this.model);
			if ( this.parent.tabView[lastPosition].$el.find('.vignette').hasClass('active') ) {
			this.parent.tabView[lastPosition].$el.find('.vignette').removeClass('active');
			}
			//console.log(this.parent.tabSelected.length);
			if( this.parent.tabSelected.length > 0) {//supprime les elements select
				console.log("ON SUPPRRRIMMMEE");
				$('#gallery .ui-selected').removeClass('ui-selected').removeClass('already-selected');
				for ( var i of this.parent.tabSelected ) {
					if( lastPosition != i  )
					this.parent.tabView[i].$el.find('.vignette').toggleClass('active');
				}
			}
			this.parent.tabSelected = [] ;
			this.handleFocus();
				}
		},

		handleFocus: function(e) {
			//console.log(" la liste :")
			//console.log(this.parent.tabSelected);
			if( this.parent.tabSelected.length > 0) {
				$('#gallery .ui-selected').removeClass('ui-selected');
				$('#gallery').trigger('unselected')
				for ( var i of this.parent.tabSelected ) {
					this.parent.tabView[i].$el.find('.vignette').toggleClass('active');
				}
			}
			this.$el.find('.vignette').toggleClass('active');
			this.parent.tabSelected = [] ;

		},
		hoveringStart:function(){
			console.log("je survole la photo");
			console.log("je charge la photo");
		},

		initialize : function(options) {
			this.parent = options.parent;
			this.lastzoom = null;
		},

		onRender: function(){
			var _this = this;

		},

		goFullScreen: function(e) {
			if (!e.ctrlKey) {
				this.parent.displayModal(e);
			}
		},

		onDestroy: function() {
			console.log("bim destroy");
		},


	});

});
