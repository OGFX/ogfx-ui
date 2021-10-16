function sliderChanged(el) {
    console.log('sliderChanged');
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/set_port_value/" + this.dataset.rackIndex + "/" + this.dataset.unitIndex + "/" + this.dataset.portIndex + "/" + this.value, true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send();
    text = document.getElementById("input_control_port_value_text_" + this.dataset.rackIndex + "_" + this.dataset.unitIndex + "_" + this.dataset.portIndex);
    text.value = this.value;
};

function unitEnableChanged(event) {
    console.log('unitEnableChanged');
    console.log(event.target.checked);
    var xhr = new XMLHttpRequest();
    var enabled = 0;
    if (event.target.checked) { 
        enabled = 1;
    }
    xhr.open("GET", "/enable_unit/" + this.dataset.rackIndex + "/" + this.dataset.unitIndex + "/" + enabled, true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send();
};

function unitMidiCCChanged(event) {
    console.log('unitMidiCCChanged()');
    var xhr = new XMLHttpRequest();
    var rack_index = this.parentNode.childNodes[1].dataset.rackIndex;
    var unit_index = this.parentNode.childNodes[1].dataset.unitIndex;
    var enabled = this.parentNode.childNodes[1].checked ? 1 : 0;
    var channel = this.parentNode.childNodes[3].value;
    var cc = this.parentNode.childNodes[5].value;
    xhr.open('GET', '/set_unit_midi_cc/' + rack_index + '/' + unit_index + '/' + enabled + '/' + channel + '/' + cc);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send();
};

const debounce = (fn, delay) => {
  let timeOutId;
  return function(...args) {
    if(timeOutId) {
      clearTimeout(timeOutId);
    }
    timeOutId = setTimeout(() => {
      fn(...args);
    },delay);
  }
}

function updateView(payload) {
    // console.log('updateView');
    // console.log(payload);
    for (var rack_index = 0; rack_index < payload['racks'].length; ++rack_index) {
        var rack = payload['racks'][rack_index];
        for (var unit_index = 0; unit_index < payload['racks'][rack_index]['units'].length; ++unit_index) {
            var unit = rack['units'][unit_index];
            var unit_enabled_checkbox = document.getElementById('unit-enable-checkbox-' + rack_index + '-' + unit_index);
            unit_enabled_checkbox.checked = unit['enabled'];
        }
    }
};

function viewUpdateRequestStateChanged() {
    if (this.readyState == 4 && this.status == 200) {
        var payload = JSON.parse(this.responseText);
        updateView(payload);
    }
};

function requestViewUpdate() {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = viewUpdateRequestStateChanged;
    xhr.open('GET', '/download', true);
    xhr.send();
};

document.addEventListener("readystatechange", event => {
    console.log('readystatechange...');
    if (event.target.readyState === "complete") {
        console.log('Setting up listeners...');
        var sliders = document.getElementsByClassName("input-control-port-value-slider");
        for (var index = 0; index < sliders.length; ++index) {
            sliders[index].style.display="block";
            sliders[index].oninput = sliderChanged;
        }

        var unit_checkboxes = document.getElementsByClassName("unit-enable-checkbox");
        for (var index = 0; index < unit_checkboxes.length; ++index) {
            unit_checkboxes[index].oninput = unitEnableChanged;
        }

        var unit_midi_cc_checkboxes = document.getElementsByClassName('unit-midi-cc-enabled');
        for (var index = 0; index < unit_midi_cc_checkboxes.length; ++index) {
            unit_midi_cc_checkboxes[index].oninput = unitMidiCCChanged;
        }

        var unit_midi_cc_channels = document.getElementsByClassName('unit-midi-cc-channel');
        for (var index = 0; index < unit_midi_cc_channels.length; ++index) {
            unit_midi_cc_channels[index].oninput = unitMidiCCChanged;
        }

        var unit_midi_cc_ccs = document.getElementsByClassName('unit-midi-cc-cc');
        for (var index = 0; index < unit_midi_cc_ccs.length; ++index) {
            unit_midi_cc_ccs[index].oninput = unitMidiCCChanged;
        }

        console.log("Done setting up listeners.");

        console.log("Setting up updater...");
        window.setInterval(requestViewUpdate, 1000);
        console.log("Done setting up updater.");
    }
});
