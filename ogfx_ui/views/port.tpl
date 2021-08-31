<div class="port-info">
    % port_index = 0
    % for port in unit['input_control_ports']:
    <details>
    <summary id="port-{{rack_index}}-{{unit_index}}-{{port_index}}">
        <span>{{rack_index}}.{{unit_index}}.{{port_index}}:</span>
        <span>{{port['name']}} [{{port['range'][1]}} {{port['range'][0]}} {{port['range'][2]}}]</span>
        <div class="control-input-container">
            <input class="input-control-port-value-slider" type="range" min="{{port['range'][1]}}" max="{{port['range'][2]}}" step="0.001" value="{{port['value']}}" autocomplete="off" name="input_control_port_value_slider_{{rack_index}}_{{unit_index}}_{{port_index}}" data-rack-index="{{rack_index}}" data-unit-index="{{unit_index}}" data-port-index="{{port_index}}">
            <input class="input-control-port-value-text" type="text" inputmode="decimal" value="{{port['value']}}" autocomplete="off" size="5" id="input_control_port_value_text_{{rack_index}}_{{unit_index}}_{{port_index}}" data-rack-index="{{rack_index}}" name="input_control_port_value_text_{{rack_index}}_{{unit_index}}_{{port_index}}" data-rack-index="{{rack_index}}" data-unit-index="{{unit_index}}" data-port-index="{{port_index}}">
        </div>
    </summary>
    Ch: <input title="Midi channel ([0..15], -1 for disabled)" type="number" min="-1" max="15" value="-1">
    CC: <input title="Midi CC ([0..127], -1 for disabled)" type="number" min="-1" max="127" value="-1">
    Min: <input title="Minimum value" type="number" min="{{port['range'][1]}}" value="{{port['range'][1]}}" max="{{port['range'][2]}}" step="0.01">
    Max: <input title="Maximum value" type="number" min="{{port['range'][1]}}" max="{{port['range'][2]}}" value="{{port['range'][2]}}" step="0.01">
    </details>

    % port_index = port_index + 1
    % end
</div>
