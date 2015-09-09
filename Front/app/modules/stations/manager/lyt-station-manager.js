define([
	'jquery',
	'underscore',
	'backbone',
	'marionette',
	'radio',

	'./lyt-protocol',

	'sweetAlert',
	'config',
	'simplePagination',

	'ns_form/NSFormsModuleGit',

	'i18n'

], function($, _, Backbone, Marionette, Radio, LytProto,
	Swal, config, simplePagination, NsForm
){

	'use strict';

	return Marionette.LayoutView.extend({

		className: 'full-height white',

		template: 'app/modules/stations/manager/templates/tpl-station-manager.html',

		name : 'Protocol managing',

		regions: {
			rgStation: '#rgStation',
			rgProtos : '#rgProtos'
		},

		ui: {
			accordionContainer : '#accordionContainer',
			protoList : '#protoList',
			total: '#total',
			formStation: '#stationForm',
			formStationBtns: '#stationFormBtns',
		},

		events : {
			'click #addProto' : 'addProtoFromList',
			'click #prevStation' : 'prevStation',
			'click #nextStation' : 'nextStation'
		},

		total : 0,

		initialize: function(options){
			if(options.id){
				this.stationId = options.id;
			}else{
				this.stationId = options.model.get('ID');
					if(window.app.temp){
						var coll = window.app.temp.collection;
						this.stationIndex = coll.indexOf(options.model);
					}
			}
		},

		check: function(){
		},

		validate: function(){
			return true;
		},

		getStepOptions: function(){
		},

		onDestroy: function(){
		},

		onShow: function(){
			var _this = this;
			this.displayStation(this.stationId);
			this.feedProtoList();
			//this.$el.i18n();
			//this.translater = Translater.getTranslater();
		},

		prevStation: function(e){
			if(window.app.temp){
				var coll = window.app.temp;
				if(this.stationIndex != 0)
					this.stationIndex--;
				this.stationId = coll.collection.models[this.stationIndex].get('ID');
				this.onShow();
			}
		},

		nextStation: function(e){
			if(window.app.temp){
				var coll = window.app.temp;
				if(this.stationIndex <= coll.collection.models.length)
					this.stationIndex++;
				this.stationId = coll.collection.models[this.stationIndex].get('ID');
				this.onShow();
			}
		},

		displayStation: function(stationId){
			this.total = 0;
			console.log(stationId);
			var stationType = 1;
			var _this = this;
			this.nsForm = new NsForm({
				name: 'StaForm',
				modelurl: config.coreUrl+'stations',
				formRegion: this.ui.formStation,
				buttonRegion: [this.ui.formStationBtns],
				displayMode: 'display',
				objectType: stationType,
				id: stationId,
				reloadAfterSave : true,
			});

			this.nsForm.BeforeShow = function(){
				_this.displayProtos();
			};
		},

		displayProtos: function(){
			var _this = this;
			var ProtoColl = Backbone.Collection.extend({
				url: config.coreUrl+'stations/'+this.stationId+'/protocols',
				fetch: function(options) {
					if(!options){
						var options= {};
					}
					options.data = {
						FormName : 'ObsForm',
						DisplayMode : 'edit'
					};
					options.success = function(protos){

					};
					return Backbone.Collection.prototype.fetch.call(this, options);
				},

			});

			this.protoColl = new ProtoColl();
			this.protoColl.fetch({reset: true});

			var ProtoCollView = Backbone.Marionette.CollectionView.extend({
				childView : LytProto,
				childViewOptions : {
					stationId:	this.stationId
				},
				id : 'accordion',
				onRender: function(){
					var _this = this;
					this.$el.on('show.bs.collapse', function () {
						_this.$el.find('.in').collapse('hide');
					});
				},
			});

			this.protoCollView = new ProtoCollView({ collection: this.protoColl });
			this.protoCollView.render();
			this.ui.accordionContainer.html(this.protoCollView.el);

			this.bindProtosEvts();
		},

		bindProtosEvts: function(){
			this.listenTo(this.protoCollView.collection, 'destroy', this.onProtoDestroy);
			this.listenTo(this.protoCollView.collection, 'add', this.onProtoAdd);
			this.listenTo(this.protoCollView.collection, 'change', this.onProtoChange);
		},

		onProtoChange: function(mod){
			/*
			if(mod._previousAttributes.total){
				//up on a proto
				var prev = mod._previousAttributes.total;
				this.total -= prev;
				if(Number.isInteger(mod.get('total'))){
					console.log('test');

					this.total += (prev+1)
				}else{
					console.log('test');
					this.total += (prev-1);
				}
			}else{
				//new proto
				this.total += mod.get('total');
			}
			this.ui.total.html(this.total);*/
			this.total = 0; 
			for (var i = 0; i < this.protoCollView.collection.models.length; i++) {
				this.total += this.protoCollView.collection.models[i].get('obs').length;
			};
			this.ui.total.html(this.total);
		},
		
		onProtoDestroy: function(){
			console.log('destroy');
		},
		
		onProtoAdd: function(mod){
			this.total = 0; 
			for (var i = 0; i < this.protoCollView.collection.models.length; i++) {
				this.total += this.protoCollView.collection.models[i].get('obs').length;
			};
			this.ui.total.html(this.total);
		},

		feedProtoList: function(){
			var _this = this;
			this.protoSelectList = new Backbone.Collection();
			this.protoSelectList.fetch({
				url: config.coreUrl+'/protocolTypes',
				reset: true,
				success: function(){
					_.each(_this.protoSelectList.models,function( model ){
						_this.ui.protoList.append(new Option(model.get('Name'),model.get('ID')));
					},this);
				},
			});
		},

		addProtoFromList: function(){
			var name = this.ui.protoList.find(':selected').text();
			var objectType = parseInt(this.ui.protoList.val());

			var md = this.protoCollView.collection.findWhere({'ID' : objectType});
			if(md){
				var cid = md.cid;
				var viewId = this.protoCollView.children._indexByModel[cid];
				var view = this.protoCollView.children._views[viewId];
				view.addObs();
			}else{
				//append a new proto
				this.addProtoType(name, objectType);
			}
		},


		addProtoType: function(name, objectType){
			var _this = this;

			var proto = new Backbone.Model();

			this.jqxhr = $.ajax({
				url: config.coreUrl+'stations/'+this.stationId+'/protocols/0',
				context: this,
				type: 'GET',
				data: {
					FormName: '_' + objectType + '_',
					ObjectType: objectType,
					DisplayMode: 'edit'
				},
				dataType: 'json',
				success: function (resp) {
					proto.set({Name : name});
					proto.set({ID : objectType});
					proto.set({show : true});
					proto.set({obs : {
						data : resp.data,
						fieldsets : resp.fieldsets,
						schema : resp.schema
					}});
					_this.protoCollView.collection.push(proto);
				},
				error: function (msg) {
					console.warn('request new proto error');
				}
			});
		},

	});
});


