<div class="port-info">
    % port_index = 0
    % for port in unit['input_control_ports']:
        <div class="port-summary-wrap port rounded-shadow-box">
            <div class="port-summary">
                <div class="port-summary-first-line">
                    <div>
                    <span>{{rack_index}}.{{unit_index}}.{{port_index}}:</span>
                    <span>{{port['name']}} [{{port['range'][1]}} {{port['range'][0]}} {{port['range'][2]}}]</span>
                    </div>
                    <input class="input-control-port-value-text float" type="number" step="0.001" value="{{port['value']}}" autocomplete="off" id="input_control_port_value_text_{{rack_index}}_{{unit_index}}_{{port_index}}" data-rack-index="{{rack_index}}" name="input_control_port_value_text_{{rack_index}}_{{unit_index}}_{{port_index}}" data-unit-index="{{unit_index}}" data-port-index="{{port_index}}">
                </div>
                <div class="control-input-container">
                    <input class="input-control-port-value-slider" type="range" min="{{port['range'][1]}}" max="{{port['range'][2]}}" step="0.001" value="{{port['value']}}" autocomplete="off" name="input_control_port_value_slider_{{rack_index}}_{{unit_index}}_{{port_index}}" data-rack-index="{{rack_index}}" data-unit-index="{{unit_index}}" data-port-index="{{port_index}}">
                </div>
            </div>
            <!--
            <span>
                MIDI CC:
                <input name="port-midi-cc-channel-{{rack_index}}-{{unit_index}}-{{port_index}}" class="midi-cc-channel" title="Midi channel ([0..15], -1 for disabled)" type="text" min="-1" max="15" value="-1">
                <input name="port-midi-cc-cc-{{rack_index}}-{{unit_index}}-{{port_index}}" class="midi-cc-cc" title="Midi CC ([0..127], -1 for disabled)" type="text" min="-1" max="127" value="-1">
                <input name="port-midi-cc-min-{{rack_index}}-{{unit_index}}-{{port_index}}" class="float" title="Minimum value" type="text" min="{{port['range'][1]}}" max="{{port['range'][2]}}" value="{{port['range'][1]}}" step="0.01">
                <input name="port-midi-cc-max-{{rack_index}}-{{unit_index}}-{{port_index}}" class="float" title="Maximum value" type="text" min="{{port['range'][1]}}" max="{{port['range'][2]}}" value="{{port['range'][2]}}" step="0.01">
            </span>
            -->
        </div>
    % port_index = port_index + 1
  % end
</div>
