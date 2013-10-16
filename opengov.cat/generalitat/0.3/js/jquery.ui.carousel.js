/*!
 * jQuery UI Carousel 0.3.0
 *
 * Copyright 2010, George Paterson
 * Dual licensed under the MIT or GPL Version 2 licenses.
 *
 * Depends:
 *	jquery.ui.core.js
 *	jquery.ui.widget.js
 * Optional:
 *  jquery.effects.core.js
 */
(function($, undefined) {
	$.widget("ui.carousel", {
    options: {
			scroll: 3,
			visible: 3,
			itemWidth: null,
			setWidth: false,
			track: true,
			easing: 'swing',
			speed: 'normal'
    },
		_create: function() {
			/**
			 * Default function of a UI widget.
			 * Inject UI Carousel HTML into designated container.
			 * Set the initial dimensions of the carousel.
			 * If a tracker is requested then generate tracker.
			 * Set the initial state of the navigation.
			 * Attach events to the carousel. 
			 */
			this.animated = false;
			this.element.addClass('ui-carousel ui-widget ui-widget-content ui-corner-all');
			$(' > ul', this.element).addClass('ui-carousel-slide');
			$('.ui-carousel-slide > li', this.element).addClass('ui-carousel-item');
			$('.ui-carousel-slide', this.element).wrap('<div class="ui-carousel-clip"></div>');
			$('.ui-carousel-clip', this.element).before('<div class="ui-carousel-header ui-widget-header ui-corner-all"></div>');
			$('.ui-carousel-header', this.element).prepend('<ul class="ui-carousel-navigation"><li class="ui-carousel-previous ui-state-default ui-corner-all"><a class="ui-icon ui-icon-circle-triangle-w" title="Previous" href="#">Previous</a></li><li class="ui-carousel-next ui-state-default ui-corner-all"><a class="ui-icon ui-icon-circle-triangle-e" title="Next" href="#">Next</a></li></ul>');
			this.dimensions();
			if(this.options.track) {
				this._setTracker();
			}
			this._navigationState();
			this._events();
		},
		destroy: function() {
			/**
			 * Default function of a UI widget.
			 * This will destroy the widget and remove any injected code.  
			 */
			$('.ui-carousel-previous a', this.element).unbind('click');
			$('.ui-carousel-next a', this.element).unbind('click');
			$('.ui-carousel-navigation', this.element).remove();
			$('.ui-carousel-slide', this.element).unwrap('<div class="ui-carousel-clip"></div>');
			$(".ui-carousel-slide > li", this.element).removeClass('ui-carousel-item');
			$(' > ul', this.element).removeClass('ui-carousel-slide');
			this.element.removeClass('ui-carousel ui-widget ui-corner-all');
			return this;
		},
		dimensions: function() {
			/**
			 * Gets the initial number of items in the carousel.
			 * If itemWidth is not set then itemWidth is retrieved from the width of the list element.
			 * If setWidth is set then the width of the clipping element will be the total width of the list elements.
			 */
			this.currentItem = 1;
			this.totalItems = $('.ui-carousel-slide > li', this.element).length;
			if(!this.options.itemWidth) {
				this.options.itemWidth = $('.ui-carousel-slide > li', this.element).outerWidth(true);
			}
			this.distance = parseInt(this.options.itemWidth * this.options.scroll, 10);
			if(this.options.setWidth) {
				if(!this.options.itemWidth) {
					this.options.itemWidth = $(' > li', this.element.children('ul')).outerWidth(true);
				}
				this.carouselWidth = this.options.visible * this.options.itemWidth;
				$('.ui-carousel-clip', this.element).css({'width': this.carouselWidth+'px'});				
			}			
		},
		_setTracker: function() {
			/**
			 * Inject the initial state of the tracker.
			 * Could be a single item or a range.
			 */
			var range = this.currentItem + this.options.scroll - 1;
			if (this.options.visible == 1) {
				$('.ui-carousel-navigation', this.element).after('<p class="ui-carousel-tracker">showing '+this.currentItem+' of '+this.totalItems+'</p>');
			}
			else {
				$('.ui-carousel-navigation', this.element).after('<p class="ui-carousel-tracker">showing '+this.currentItem+' - '+range+' of '+this.totalItems+'</p>');
			}
		},
		_updateTracker: function() {
			/**
			 * Update the tracker after a navigation event.
			 * Uses modulo to calculate incomplete scroll events.
			 */
			var modulo = this.totalItems % this.options.visible,
				range = this.currentItem + this.options.scroll - 1;
			if (range > this.totalItems) {
				range = range - (this.options.visible - modulo);
				if (this.currentItem == this.totalItems) {
					$('.ui-carousel-tracker', this.element).html('showing '+this.currentItem+' of '+this.totalItems);
				}
				else {
					$('.ui-carousel-tracker', this.element).html('showing '+this.currentItem+' - '+range+' of '+this.totalItems);
				}
			}
			else if (range == this.totalItems) {
				$('.ui-carousel-tracker', this.element).html('showing '+this.currentItem+' of '+this.totalItems);
			}
			else {
				if (this.options.visible == 1) {
					$('.ui-carousel-tracker', this.element).html('showing '+this.currentItem+' of '+this.totalItems);
				}
				else {
					$('.ui-carousel-tracker', this.element).html('showing '+this.currentItem+' - '+range+' of '+this.totalItems);
				}
			}
		},
		_navigationState: function() {
			/**
			 * Enable or disable navigation depending on current position.
			 */
			if((this.currentItem - this.options.scroll) < 1){
				$('.ui-carousel-previous', this.element).addClass('ui-state-disabled');
				
      }
			else {
				if($('.ui-carousel-previous', this.element).hasClass('ui-state-disabled')) {
					$('.ui-carousel-previous', this.element).removeClass('ui-state-disabled');
				}
			}
			if(this.currentItem > (this.totalItems - this.options.scroll)){
				$('.ui-carousel-next', this.element).addClass('ui-state-disabled');
				
      }
			else {
				if($('.ui-carousel-next', this.element).hasClass('ui-state-disabled')) {
					$('.ui-carousel-next', this.element).removeClass('ui-state-disabled');
				}
			}
		},
		_events: function() {
			/**
			 * Events for navigation.
			 * Includes hover state and click events.
			 */
			var self = this,
				o = this.options,
				direction = null;
			$('.ui-carousel-previous', this.element).bind('mouseover', function(){
				if(self.currentItem > 1){
					$(this).addClass('ui-state-hover');
				}
			});
			$('.ui-carousel-previous', this.element).bind('mouseout', function(){
				$(this).removeClass('ui-state-hover');
			});
			$('.ui-carousel-previous a', this.element).click(function(element) {
				element.preventDefault();
				direction = 'previous';
				if(self.currentItem - o.scroll <= 1){
					$(this).parent().removeClass('ui-state-hover'); 
				}
				if(self.currentItem > 1){
	          self.carouselAnimation(direction, self.distance);
	      }
			});
			$('.ui-carousel-next', this.element).bind('mouseover', function(){
				if(self.currentItem <= (self.totalItems - o.scroll)){
					$(this).addClass('ui-state-hover');
				}
			});
			$('.ui-carousel-next', this.element).bind('mouseout', function(){
				$(this).removeClass('ui-state-hover');
			});
			$('.ui-carousel-next a', this.element).click(function(element) {
				element.preventDefault();
				direction = 'next';
				if ((self.currentItem + o.scroll + o.visible) > self.totalItems) {
					$(this).parent().removeClass('ui-state-hover');
				}
				if (self.currentItem <= (self.totalItems - o.scroll)){
						self.carouselAnimation(direction, - self.distance);
	      }
			});				
		},
		carouselAnimation: function(direction, distance) {
			/**
			 * After a click event triggered the carousel is animated.
			 * Further click events prevented during animation.
			 * If tracker enabled it will be updated.
			 * Navigation state updated.
			 * Further click events then enabled.
			 */
			var self = this,
				o = this.options;
			if(!this.animated){
				this.animated = true;
				if ($('.ui-carousel-slide', this.element).css('left') == 'auto') {
					current = 0;
				}
				else {
					current = parseInt($('.ui-carousel-slide', this.element).css('left'), 10);
				}
				if (direction == 'previous') {
					this.currentItem = this.currentItem - this.options.scroll;
				}
				else {
					this.currentItem = this.currentItem + this.options.scroll;
				}
				distance = current + distance;
				$('.ui-carousel-slide', this.element).animate({left: distance + 'px'}, this.options.speed, this.options.easing, function() {
					if(o.track) {
						self._updateTracker();
					}
					self._navigationState();
					self.animated = false;
			  });
      }
		}
	});
	$.extend($.ui.carousel, {
		version: 0.3
	});
})(jQuery);