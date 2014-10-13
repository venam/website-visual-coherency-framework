var textArea = document.getElementById("edit-box");
var submitButton = document.getElementById("submit_pages");

submitButton.addEventListener(
	"click",
	function() {
		text = textArea.value;
		self.port.emit("save_link", text);
	},
	false
);

self.port.on("show", function onShow(oldConf) {
	textArea.value = oldConf;
	textArea.focus();
});
