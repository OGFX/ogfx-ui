<div class="port-info">
    % port_index = 0
    % for port in unit['input_control_ports']:
        <div class="port-summary-wrap port">
            <div class="port-summary">
                <div class="port-summary-first-line">
                    <div>
                    <span>{{port['name']}}</span>
                    </div>
                </div>
                <div class="control-input-container">
                    <input class="input-control-port-value-slider" type="range" min="{{port['range'][1]}}" max="{{port['range'][2]}}" step="0.001" value="{{port['value']}}" autocomplete="off" name="input_control_port_value_slider_{{rack_index}}_{{unit_index}}_{{port_index}}" data-rack-index="{{rack_index}}" data-unit-index="{{unit_index}}" data-port-index="{{port_index}}">
                    <input class="input-control-port-value-text float" type="text" value="{{port['value']}}" autocomplete="off" id="input_control_port_value_text_{{rack_index}}_{{unit_index}}_{{port_index}}" data-rack-index="{{rack_index}}" name="input_control_port_value_text_{{rack_index}}_{{unit_index}}_{{port_index}}" data-unit-index="{{unit_index}}" data-port-index="{{port_index}}">
                    <input class="input-control-port-cc-enabled-checkbox" type="checkbox" data-rack-index="{{rack_index}}" data-unit-index="{{unit_index}}" data-port-index="{{port_index}}" name="input_control_port_cc_enabled_checkbox_{{rack_index}}_{{unit_index}}_{{port_index}}" title="CC enabled" {{'checked' if unit['input_control_ports'][port_index]['cc']['enabled'] else ''}}>
                </div>
            </div>
            <span class="port-cc-mapping" {{ !"style=\"display: none;\"" if not port['cc']['enabled'] else ''}}>
                MIDI CC:
                <input name="port_midi_cc_channel_{{rack_index}}_{{unit_index}}_{{port_index}}" class="midi-cc-channel" title="Midi channel ([0..15])" type="text" min="0" max="15" value="{{port['cc']['channel']}}">
                <input name="port_midi_cc_cc_{{rack_index}}_{{unit_index}}_{{port_index}}" class="midi-cc-cc" title="Midi CC ([0..127])" type="text" min="0" max="127" value="{{port['cc']['cc']}}">
                <input name="port_midi_cc_min_{{rack_index}}_{{unit_index}}_{{port_index}}" class="float" title="Minimum value" type="text" min="{{port['range'][1]}}" max="{{port['range'][2]}}" value="{{port['cc']['target_minimum']}}" step="0.01">
                <input name="port_midi_cc_max_{{rack_index}}_{{unit_index}}_{{port_index}}" class="float" title="Maximum value" type="text" min="{{port['range'][1]}}" max="{{port['range'][2]}}" value="{{port['cc']['target_maximum']}}" step="0.01">
            </span>
        </div>
    % port_index = port_index + 1
  % end
</div>
