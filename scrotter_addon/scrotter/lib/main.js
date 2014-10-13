var self    = require("sdk/self");
var buttons = require('sdk/ui/button/action');
var tabs    = require('sdk/tabs');
var base64  = require('sdk/base64');
const tmr   = require('sdk/timers');
var sp      = require("sdk/simple-prefs");
var ss      = require("sdk/simple-storage");
var prefs   = sp.prefs;
const { Cc, Ci, Cu, components } = require("chrome");
const {OS}  = Cu.import("resource://gre/modules/osfile.jsm", {});

if (!ss.storage.pages) {
	ss.storage.pages = [
		"file:///home/stick/prog/serv/canvas_city/canvas_city.html",
		"http://duckduckgo.com",
		"http://nixers.net"
	]
}

var LOCATION     = prefs.LOCATION;
var TIMEOUT      = prefs.TIMEOUT * 1000;
var current_page = 0;
var current_date = date_formatted();

function date_formatted() {
	let d       = new Date();
	let year    = d.getFullYear();
	let month   = d.getMonth();
	let day     = d.getDate();
	let hour    = d.getHours();
	let minute  = d.getMinutes();
	let seconds = d.getSeconds();
	return year+"_"+month+"_"+day+"_"+hour+"_"+minute+"_"+seconds;
}

var panel = require("sdk/panel").Panel({
	width: 300,
	height: 450,
	contentURL:  self.data.url("text-entry.html"),
	contentScriptFile: self.data.url("get-text.js")
});

sp.on("PAGES", function() {
	panel.show();
});

panel.on("show", function() {
	var the_list_of_pages = ""
	for (var i in ss.storage.pages) {
		the_list_of_pages += ss.storage.pages[i]+"\n";
	}
	panel.port.emit("show", the_list_of_pages);
});

panel.port.on("save_link", function(text) {
	console.log(text);
	var links_arr = filter_arr(text.split("\n"));
	ss.storage.pages = links_arr;
	panel.hide();
});

function filter_arr(arr) {
	var new_arr = [];
	var regexp = /\b((?:[a-z][\w-]+:(?:\/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}\/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))/i;
	for (var i in arr) {
		//some kind of url filtering
		var result = regexp.exec(arr[i]);
		if (result != null) {
			new_arr.push(result[0]);
		}
	}
	return new_arr;
}

function onPrefChange() {
	LOCATION     = prefs.LOCATION;
	TIMEOUT      = prefs.TIMEOUT * 1000;
}

var button  = buttons.ActionButton({
	id: "scrotter",
	label: "Scrotter Addon",
	icon: {
		"16": "./icon-16.png",
		"32": "./icon-32.png",
		"64": "./icon-64.png"
	},
	onClick: handleClick
});

function handleClick(state) {
	button.disabled = true;
	current_date    = date_formatted();
	current_page    = 0;
	tabs.open({
		url: ss.storage.pages[current_page],
		onReady: function(tab) {
			start_finish_loading_tab_with_timer(tab);
		}
	});
}

function start_finish_loading_tab_with_timer(tab) {
	tmr.setTimeout( 
		function() {
			tab_finish_loading(tab)
		},
		TIMEOUT
	);
}

function tab_finish_loading(tab) {
	console.log("Tab: "+tab.url+" finished loading");
	let the_image = get_image();
	//workers port communication with content script
	var worker    = tab.attach({
		contentScriptFile: self.data.url("save.js")
	});

	worker.port.on("receive", function (binary_image_file) {
		var the_url = prepare_url(tab.url);
		var save_to = LOCATION+current_date
		OS.File.exists(save_to).then(
			exists => {
				if(exists) {
					save_to += "/"+the_url+".jpeg";
					writeBinaryDataToFile(binary_image_file, save_to)
				}
				else {
					OS.File.makeDir(save_to).then (
						function onFulfill() {
							console.log("dir created");
							save_to += "/"+the_url+".jpeg";
							writeBinaryDataToFile(binary_image_file, save_to)
						},
						function onReject() {
							console.log("error creating dir");
							return;
						}
					);
				}
			}
		);
		tab.close();
	});

	worker.port.emit("save",the_image);
	goto_next_page();
}

function get_image() {
	let window           = require('sdk/window/utils').getMostRecentBrowserWindow();
	let active_tab       = require('sdk/tabs/utils').getActiveTab(window);
	let thumbnail        = window.document.createElementNS("http://www.w3.org/1999/xhtml", "canvas");
	thumbnail.mozOpaque  = true;
	window               = active_tab.linkedBrowser.contentWindow;
	thumbnail.width      = window.innerWidth + window.scrollMaxX;
	thumbnail.height     = window.innerHeight + window.scrollMaxY;
	var ctx              = thumbnail.getContext("2d");
	ctx.drawWindow(window, 0, 0, thumbnail.width, thumbnail.height,"rgb(255,255,255)");
	return thumbnail.toDataURL("image/jpeg");
}

function prepare_url(text) {
	return encodeURI(text.replace( /\//g , "_").replace( / /g, "_").replace( /:/g, "_"));
}

function writeBinaryDataToFile(data, filename) {
	var fileIO = require("sdk/io/file");
	var ByteWriter = fileIO.open(filename, "wb");
	if (!ByteWriter.closed) {
		ByteWriter.write(data);
		ByteWriter.close();
	}
}

function goto_next_page() {
	if (current_page < ss.storage.pages.length-1) {
		current_page++;
		tabs.open({
			url: ss.storage.pages[current_page],
			onReady: function(tab) {
				start_finish_loading_tab_with_timer(tab);
			}
		});
	}
	else {
		//reactivate button
		button.disabled = false;
	}
}

