<div class="unit" id="unit-{{rack_index}}-{{unit_index}}">
    <details open="true">
        <summary class="unit-info">
            <span>{{rack_index}}.{{unit_index}}._:</span>
            <input title="Midi channel ([0..15], -1 for disabled)" type="number" min="-1" max="15" value="-1">:<input title="Midi CC ([0..127], -1 for disabled)" type="number" min="-1" max="127" value="-1">
            <input class="unit_enable_checkbox" type="checkbox" {{'checked' if unit['enabled'] else ''}} name="unit_enabled_{{rack_index}}_{{unit_index}}" data-rack-index="{{rack_index}}" data-unit-index="{{unit_index}}">
            <span>{{len(unit['input_audio_ports'])}}:{{len(unit['output_audio_ports'])}}</span>
            <span>{{unit['name']}}</span>
        </summary>
        <div class="operations">
            <a href="move_unit_up/{{rack_index}}/{{unit_index}}">up</a>
            <a href="move_unit_down/{{rack_index}}/{{unit_index}}">dwn</a>
            <a href="save/{{rack_index}}/{{unit_index}}">sv</a>
            <a href="saveas/{{rack_index}}/{{unit_index}}">(as)</a>
            <a href="load/{{rack_index}}/{{unit_index}}">ld</a>
            <a href="reset/{{rack_index}}/{{unit_index}}">rst</a>
            <a href="delete/{{rack_index}}/{{unit_index}}">rm</a>
            <a href="upload/{{rack_index}}/{{unit_index}}">ul</a>
            <a href="download/{{rack_index}}/{{unit_index}}" download="ogfx-unit.json">dl</a>
        </div>
        <div class="connections-info">
            % channel_index = 0
            % for channel in unit['input_connections']:
                <div>input channel-{{channel_index}}:</div>
                % connection_index = 0
                % for connection in channel:
                    <div class="operations"><span>{{connection}}</span><a class="operations" href="disconnect/{{rack_index}}/{{unit_index}}/input/{{channel_index}}/{{connection_index}}">disconnect</a></div>
                    % connection_index = connection_index + 1
                % end
                <div><a class="operations" href="connect/{{rack_index}}/{{unit_index}}/input/{{channel_index}}">connect</a></div>
                % channel_index = channel_index + 1
            % end
        </div>
        % include('port.tpl', unit=unit)
        <div class="connections-info">
            % channel_index = 0
            % for channel in unit['output_connections']:
                <div>output channel-{{channel_index}}:</div>
                % connection_index = 0
                % for connection in channel:
                    <div class="operations"><span>{{connection}}</span><a class="operations" href="disconnect/{{rack_index}}/{{unit_index}}/output/{{channel_index}}/{{connection_index}}">disconnect</a></div>
                    % connection_index = connection_index + 1
                % end
                <div><a class="operations" href="connect/{{rack_index}}/{{unit_index}}/output/{{channel_index}}">connect</a></div>
                % channel_index = channel_index + 1
            % end
        </div>
    </details>
</div>
