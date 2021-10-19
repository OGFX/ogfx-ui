<div class="unit rounded-shadow-box" id="unit-{{rack_index}}-{{unit_index}}">
    <details open>
        <summary class="unit-info">
            <span>{{rack_index}}.{{unit_index}}._:</span>
            <input id="unit-enable-checkbox-{{rack_index}}-{{unit_index}}" class="unit-enable-checkbox" title="Unit enabled" type="checkbox" {{'checked' if unit['enabled'] else ''}} name="unit_enabled_{{rack_index}}_{{unit_index}}" data-rack-index="{{rack_index}}" data-unit-index="{{unit_index}}">
            <span>{{len(unit['input_audio_ports'])}}:{{len(unit['output_audio_ports'])}}</span>
            <span>{{unit['name']}}</span>
        </summary>
        <div class="indent">
            <a href="move_unit_up/{{rack_index}}/{{unit_index}}">up</a>
            <a href="move_unit_down/{{rack_index}}/{{unit_index}}">dwn</a>
            <a href="saveas/{{rack_index}}/{{unit_index}}">sv..</a>
            <a href="load/{{rack_index}}/{{unit_index}}">ld..</a>
            <a href="reset/{{rack_index}}/{{unit_index}}">rst</a>
            <a href="delete/{{rack_index}}/{{unit_index}}">rm</a>
            <a href="upload/{{rack_index}}/{{unit_index}}">ul..</a>
            <a href="download/{{rack_index}}/{{unit_index}}" download="ogfx-unit.json">dl..</a>
        </div>
        <span class="indent">
            MIDI CC:
            <input id="unit-midi-cc-enabled-{{rack_index}}-{{unit_index}}" class="unit-midi-cc-enabled" name="unit_midi_cc_enabled_{{rack_index}}_{{unit_index}}" title="Midi CC enabled" type="checkbox" {{'checked' if unit['cc']['enabled'] else ''}} data-rack-index="{{rack_index}}" data-unit-index="{{unit_index}}">
            <input id="unit-midi-cc-channel-{{rack_index}}-{{unit_index}}" class="unit-midi-cc-channel midi-cc-channel" name="unit_midi_cc_channel_{{rack_index}}_{{unit_index}}" title="Midi channel (0..15)" type="number" min="0" max="15" value="{{unit['cc']['channel']}}">
            <input id="unit-midi-cc-cc-{{rack_index}}-{{unit_index}}" class="unit-midi-cc-cc midi-cc-cc" name="unit_midi_cc_cc_{{rack_index}}_{{unit_index}}" title="Midi CC (0..127)" type="number" min="0" max="127" value="{{unit['cc']['cc']}}">
        </span>
        <div class="connections-info">
            <details>
                <summary>extra input connections</summary>
                % channel_index = 0
                % for channel in unit['input_connections']:
                    <div>input channel-{{channel_index}}:</div>
                    % connection_index = 0
                    % for connection in channel:
                        <div class="indent"><span>{{connection}}</span><a class="operations" href="disconnect/{{rack_index}}/{{unit_index}}/input/{{channel_index}}/{{connection_index}}">disconnect</a></div>
                        % connection_index = connection_index + 1
                    % end
                    <div><a class="indent" href="connect/{{rack_index}}/{{unit_index}}/input/{{channel_index}}">connect..</a></div>
                    % channel_index = channel_index + 1
                % end
            </details>
        </div>
        % include('port.tpl', unit=unit)
        <div class="connections-info">
            <details>
                <summary>extra output connections</summary>
                % channel_index = 0
                % for channel in unit['output_connections']:
                    <div>output channel-{{channel_index}}:</div>
                    % connection_index = 0
                    % for connection in channel:
                        <div class="indent"><span>{{connection}}</span><a class="operations" href="disconnect/{{rack_index}}/{{unit_index}}/output/{{channel_index}}/{{connection_index}}">disconnect</a></div>
                        % connection_index = connection_index + 1
                    % end
                    <div><a class="indent" href="connect/{{rack_index}}/{{unit_index}}/output/{{channel_index}}">connect..</a></div>
                    % channel_index = channel_index + 1
                % end
            </details>
        </div>
    </details>
</div>
