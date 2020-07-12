function sliderChanged(el) {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/set_port_value/" + this.dataset.rackIndex + "/" + this.dataset.unitIndex + "/" + this.dataset.portIndex + "/" + this.value, true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send();
    text = document.getElementById("input_control_port_value_text_" + this.dataset.rackIndex + "_" + this.dataset.unitIndex + "_" + this.dataset.portIndex);
    text.value = this.value;
};

function unitEnableChanged(event) {
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

document.addEventListener("readystatechange", event => {
    if (event.target.readyState === "complete") {
        var sliders = document.getElementsByClassName("input-control-port-value-slider");
        for (var index = 0; index < sliders.length; ++index) {
            sliders[index].style.display="block";
            sliders[index].oninput = sliderChanged;
        }

        var unit_checkboxes = document.getElementsByClassName("unit_enable_checkbox");
        for (var index = 0; index < unit_checkboxes.length; ++index) {
            unit_checkboxes[index].oninput = unitEnableChanged;
        }
    }
    console.log("test");
});
