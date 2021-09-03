<div class="rack" id="rack-{{rack_index}}">
    <details open>
    <summary>
        {{rack_index}}._._:
        <a href="/cc/{{rack_index}}">--:--</a>
        <input type="checkbox" checked="{{rack['enabled']}}" name="rack_enabled_{{rack_index}}" title="Rack enable">
        <span>rack-{{rack_index}}</span>
    </summary>
    <div class="operations">
        <a title="move up" href="move_rack_up/{{rack_index}}">up</a>
        <a title="move down" href="move_rack_down/{{rack_index}}">dwn</a>
        <a title="save" href="save/{{rack_index}}">sv</a>
        <a title="save as..." href="saveas/{{rack_index}}">(as)</a>
        <a title="load" href="load/{{rack_index}}">ld</a>
        <a title="reset to defaults" href="reset/{{rack_index}}">rst</a>
        <a title="delete" href="delete/{{rack_index}}">rm</a>
        <a title="upload" href="upload/{{rack_index}}">ul</a>
        <a title="download" href="download/{{rack_index}}" download="ogfx-rack.json">dl</a>
    </div>
    <div class="connections-info">
        % channel_index = 0
        % for channel in rack['input_connections']:
          <div>input channel-{{channel_index}}:</div>
          % connection_index = 0
          % for connection in channel:
            <div class="operations"><span>{{connection}}</span><a class="operations" href="disconnect/{{rack_index}}/input/{{channel_index}}/{{connection_index}}">disconnect</a></div>
            % connection_index = connection_index + 1
          % end
          <div><a class="operations" href="connect/{{rack_index}}/input/{{channel_index}}">connect</a></div>
          % channel_index = channel_index + 1
        % end
        <div>midi-input:</div>
        % connection_index = 0
        % for connection in rack['input_midi_connections']:
          <div class="operations"><span>{{connection}}</span><a class="operations" href="disconnect/{{rack_index}}/midi-input/{{connection_index}}">disconnect</a></div>
          % connection_index = connection_index + 1
        % end
        <div><a class="operations" href="connect/{{rack_index}}/midi-input">connect</a></div>
    </div>
    <div class="add-unit">
        <a href="add/{{rack_index}}/0">add unit</a>
    </div>
    % unit_index = 0
    % for unit in rack['units']:
        % include('unit.tpl', unit=unit)
    % unit_index = unit_index + 1
    <div class="add-unit">
        <a href="add/{{rack_index}}/{{unit_index}}">add unit</a>
    </div>
    % end
    <div class="connections-info">
        % channel_index = 0
        % for channel in rack['output_connections']:
        <div>output channel-{{channel_index}}:</div>
        % connection_index = 0
        % for connection in channel:
        <div class="operations"><span>{{connection}}</span><a class="operations" href="disconnect/{{rack_index}}/output/{{channel_index}}/{{connection_index}}">disconnect</a></div>
        % connection_index = connection_index + 1
        % end
        <div><a class="operations" href="connect/{{rack_index}}/output/{{channel_index}}">connect</a></div>
        % channel_index = channel_index + 1
        % end
    </div>
    </details>
</div>
