var React = require("react");
var FunctionTabs = React.createClass({
	render: function() {
		return (
			<div class = "functionTabs">
				<div class="btn-toolbar">
					<button id="compileIRBtn" class="btn btn-primary" onClick={this.onButtonClick}>Compile To IR</button>
					<button id="instrumentBtn" class="btn disabled" onClick={this.onButtonClick}>Instrument</button>
					<button id="profilingBtn" class="btn disabled" onClick={this.onButtonClick}>Profiling</button>
					<button id="runtimeOptionBtn" class="btn disabled" onClick={this.onButtonClick}>Runtime Options</button>
					<button id="injectFaultBtn" class="btn disabled" onClick={this.onButtonClick}>Inject Fault</button>
					<button id="traceGraphBtn" class="btn disabled" onClick={this.onButtonClick}>Trace Graph</button>
				</div>
			</div>
		);
	},
	onButtonClick: function(event) {
		// If the current button clicked is disabled, do nothing
		if ($("#"+event.currentTarget.id).hasClass("disabled")) {
			return;
		}

		// Disable all the following buttons and enable the next button only
		$("#"+event.currentTarget.id).nextAll().removeClass("btn-primary");
		$("#"+event.currentTarget.id).nextAll().addClass("disabled");
		$("#"+event.currentTarget.id).next().removeClass("disabled");
		$("#"+event.currentTarget.id).next().addClass("btn-primary");
	},
});

module.exports = FunctionTabs;