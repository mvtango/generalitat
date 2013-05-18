
/*
 * aciFragment jQuery Plugin v1.1.0
 * http://acoderinsights.ro
 *
 * Copyright (c) 2013 Dragos Ursu
 * Dual licensed under the MIT or GPL Version 2 licenses.
 *
 * Require jQuery Library >= v1.7.1 http://jquery.com
 * + aciPlugin >= v1.1.1 https://github.com/dragosu/jquery-aciPlugin
 *
 * Date: Apr Fri 26 18:00 2013 +0200
 */

/*
 * aciFragment can be used to store multiple key/value pairs into the fragment part of the URL, it is thus possible to
 * implement interactive widgets that save states into the URL fragment and in - the same time - have the browser history work.
 * 
 * aciFragment is based on the simple ideea: we can have GET parameters in a URL, something like
 * "...resource?key1=value1&key2=value2&..." where the key "key1" has a value of "value1" etc.
 * 
 * It is possible then to have the same thing after the hash (#) used as the fragment part of the URL, like:
 * "...resource?key1=value1#hash1=hash_value1&hash2=hash_value2&..." where the key "hash1" has a value of "hash_value1" and so on.
 * 
 * By default the browser will jump (depending on the browser) to the first element with the id/name attributes set to be equal with the fragment.
 * Because we want to store more than a single value in the fragment section of the URL, we'll need a way to handle the key/value pairs and
 * still have a way to let anchors work. 
 * 
 * aciFragment come into play here to add support for adding/setting/removing the key/value pais and
 * parse the URL fragment so it is programmatically possible to scroll the document to a anchor based on a predefined key and its parsed value.
 * The key/value pais are dynamically added and we can still use the implicit fragment functionality offered by the browser.
 * 
 * By using aciFragment:
 * 
 * - "...resource#heading" will work as expected, the document will jump to the anchor defined with the "heading" id/name;
 * 
 * - "...resource#[anchor]=heading" (where [anchor] is the plugin "options.anchor" option value) can be parsed by 
 * aciFragment and we'll be able to scroll the document to the anchor defined by the "heading" (the value of the [anchor] key);
 * 
 * - using the api to add/change the key/value pairs:
 * "...resource#heading" + a new key/value pair will be transformed to: "...resource#[anchor]=heading&newkey1=newvalue1"
 * (where newkey1/newvalue1 is a sample for the new key/value pair).
 */

(function($, window, undefined) {

    // default options

    var options = {
        anchor: 'anchor',                   // the key name to keep the reference to an anchor
        // exampe: if 'anchor' is equal with 'jumpto' then "...resource#jumpto=heading2" mean scroll to the anchor named "heading2"
        poolDelay: 250,                     // how many [ms] before we check for a hash change (if 'hashchange' is not native implemented)
        scroll: {// scroll animation (NULL to disable animation)
            duration: 'medium',
            easing: 'linear'
        }
    };

    // aciFragment plugin core

    var aciFragment = {
        // add extra data
        __extend: function() {
            $.extend(this._instance, {
                lastHash: null,
                lastParsed: null,
                // the parsed hash
                parsed: {
                },
                // flag to tell if the anchor was present
                anchor: true,
                // timeout interval
                timeOut: null,
                native: ('onhashchange' in window) && ((window.document.documentMode === undefined) || (window.document.documentMode > 7))
            });
        },
        // init
        init: function() {
            var _this = this;
            if (this.wasInit()) {
                return;
            }
            if (this._instance.native) {
                $(window).bind('hashchange' + this._instance.nameSpace, function() {
                    _this._trigger();
                });
            } else {
                this._change();
            }
            this._instance.anchor = true;
            this._trigger();
            this._super();
        },
        // trigger the event
        _trigger: function() {
            this._instance.jQuery.trigger('acifragment', [this, this._instance.anchor]);
            this._instance.anchor = false;
        },
        // handle the hash change when 'hashchange' is not native supported
        _change: function() {
            var _this = this;
            var hash = window.location.hash;
            if (hash != this._instance.lastHash) {
                this._trigger();
                this._instance.lastHash = hash;
            }
            this._instance.timeOut = window.setTimeout(function() {
                _this._change();
            }, this._instance.options.poolDelay);
        },
        // scroll to current hash
        // should be used on links that have the anchor defined
        scroll: function() {
            var hash = this.get(this._instance.options.anchor);
            if (hash && hash.length) {
                var found = $('#' + hash + ':first');
                if (!found.length) {
                    found = $('[name="' + hash + '"]:first');
                }
                if (found.length) {
                    var rect = found.get(0).getBoundingClientRect();
                    var left = $(window).scrollLeft() + rect.left, top = $(window).scrollTop() + rect.top;
                    if (this._instance.options.scroll) {
                        // scroll using animations
                        $('html,body').stop(true).animate({
                            scrollLeft: left,
                            scrollTop: top
                        },
                        this._instance.options.scroll);
                    } else {
                        window.scrollTo(left, top);
                    }
                }
            }
        },
        // default click process on a link
        // 'link' is a jQuery object for the link
        // when 'scroll' is TRUE document scroll will be made
        click: function(link, scroll) {
            var href = link.attr('href');
            if (href) {
                // parse the URL
                var pairs = this.parse(href);
                // update the current fragment (add new key/value pairs and update old ones)
                this.update(pairs);
                // only do scroll if the anchor is defined
                if (scroll && this.hasAnchor(pairs)) {
                    // process the scroll
                    this.scroll();
                }
            }
        },
        // parse values from URL
        // returns object with a property set for each hash key
        parse: function(url) {
            var pos = url.indexOf('#'), parsed = {
            };
            if (pos != -1) {
                url = url.substr(pos + 1);
                var vars = url.split('&'), pair;
                for (var i in vars) {
                    pair = vars[i].split('=');
                    if (pair.length > 1) {
                        parsed[window.decodeURIComponent(pair[0])] = window.decodeURIComponent(pair[1]);
                    } else {
                        parsed[this._instance.options.anchor] = window.decodeURIComponent(pair[0]);
                    }
                }
            }
            return parsed;
        },
        // test if the anchor is defined
        // 'pairs' is a object with the hash keys set as properties
        hasAnchor: function(pairs) {
            return pairs[this._instance.options.anchor] && (pairs[this._instance.options.anchor].length > 0);
        },
        // set the anchor value
        setAnchor: function(anchor) {
            this.set(this._instance.options.anchor, anchor);
        },
        // get the anchor value
        getAnchor: function(defaultValue) {
            return this.get(this._instance.options.anchor, defaultValue);
        },
        // parse the current hash
        // returns object with a property set for each hash key
        parseHash: function() {
            var hash = window.location.hash;
            if (hash == this._instance.lastParsed) {
                return this._instance.parsed;
            }
            var parsed = this.parse(hash);
            this._instance.parsed = parsed;
            this._instance.lastParsed = hash;
            return parsed;
        },
        // get a hash key value
        get: function(key, defaultValue) {
            var parsed = this.parseHash();
            if ((parsed[key] !== null) && (parsed[key] !== undefined) && window.String(parsed[key]).length) {
                return parsed[key];
            } else {
                return defaultValue;
            }
        },
        // replace the URL fragment
        // 'pairs' is a object with the hash keys set as properties
        // if a key value is empty string then will be removed
        // skipAnchor is internally used to skip anchor change check
        replace: function(pairs, skipAnchor) {
            var hash = [];
            for (var i in pairs) {
                if ((pairs[i] !== null) && (pairs[i] !== undefined) && window.String(pairs[i]).length) {
                    hash[hash.length] = window.encodeURIComponent(i) + '=' + window.encodeURIComponent(pairs[i]);
                }
            }
            if (!skipAnchor && this.hasAnchor(pairs)) {
                this._instance.anchor = true;
            }
            var oldHash = window.location.hash;
            if (hash.length) {
                window.location.hash = '#' + hash.join('&');
            } else if (window.history && window.history.pushState) {
                // try to remove the '#'
                window.history.pushState('', window.document.title, window.location.pathname + window.location.search);
            } else {
                window.location.hash = '';
            }
            if (window.location.hash == oldHash) {
                // triger the event if no hash changed
                this._trigger();
            }
        },
        // update the URL fragment
        // 'pairs' is a object with the hash keys set as properties
        update: function(pairs) {
            var parsed = this.parseHash();
            for (var i in pairs) {
                parsed[i] = pairs[i];
            }
            if (this.hasAnchor(pairs)) {
                this._instance.anchor = true;
            }
            this.replace(parsed, true);
        },
        // set/add a hash key/value pair
        set: function(key, value) {
            var parsed = this.parseHash();
            parsed[key] = value;
            if (key == this._instance.options.anchor) {
                this._instance.anchor = true;
            }
            this.replace(parsed, true);
        },
        // destroy
        destroy: function() {
            if (!this.wasInit()) {
                return;
            }
            if (this._instance.native) {
                $(window).unbind(this._instance.nameSpace);
            }
            window.clearTimeout(this._instance.timeOut);
            this._super();
        }
    };

    // extend the base aciPluginUi class and store into aciPluginClass.plugins
    aciPluginClass.plugins.aciFragment = aciPluginClass.aciPluginUi.extend(aciFragment, 'aciFragment');

    // publish the plugin & the default options
    aciPluginClass.publish('aciFragment', options);

})(jQuery, this);
