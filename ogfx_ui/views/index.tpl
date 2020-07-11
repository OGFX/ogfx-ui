<!DOCTYPE html>
<html lang="en">
  <head>
    <title>OGFX</title>
    <link rel="stylesheet" type="text/css" href="/static/index.css">
    <link rel="stylesheet" type="text/css" href="/static/range.css">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="/static/index.js"></script>
  </head>

  <body>
    <div id="top-menu">
      <span>setup: {{setup['name']}}</span>
      <div class="operations">
        <a title="save" href="save">sv</a> 
        <a title="save as..." href="saveas">(as)</a> 
        <a title="load" href="load">ld</a> 
        <a title="reset to defaults" href="reset">rst</a>
        <a title="upload" href="upload">ul</a>
        <a title="download" href="download" download="ogfx-setup.json">dl</a>
      </div>
    </div>

    <div class="racks-navigation-list">
      <span>racks:</span>
      <div class="operations">
        % index = 0
        % for rack in setup['racks']:
        <a href="#rack-{{index}}">rack-{{index}}</a>
        % index = index + 1
        %end
      </div>
    </div>

    <div id="racks">
      <form action="/" method="post">
        <div class="add-rack">
          <a href="add/0">add rack</a>
        </div>
        % rack_index = 0
        % for rack in setup['racks']:
        <div class="rack" id="rack-{{rack_index}}">
          <details open>
            <summary>
              {{rack_index}}._._: 
              <a href="/cc/{{rack_index}}">--:--</a>
              <input type="checkbox" checked="{{rack['enabled']}}" name="rack_enabled_{{rack_index}}" title="Rack enable">
              <span>rack-{{rack_index}}</span>
            </summary>
            <div class="operations">
              <a title="move up" href="moveup/{{rack_index}}">▲</a> 
              <a title="move down" href="movedown/{{rack_index}}">▼</a> 
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
            </div>
            <div class="add-unit">
              <a href="add/{{rack_index}}/0">add unit</a>
            </div>
            % unit_index = 0
            % for unit in rack['units']:
            <div class="unit" id="unit-{{rack_index}}-{{unit_index}}">
              <details>
                <summary class="unit-info">
                  <span>{{rack_index}}.{{unit_index}}._:</span>
                  <a href="/cc/{{rack_index}}/{{unit_index}}">--:--</a>
                  <input type="checkbox" {{'checked' if unit['enabled'] else ''}} name="unit_enabled_{{rack_index}}_{{unit_index}}">
                  <span>{{len(unit['input_audio_ports'])}}:{{len(unit['output_audio_ports'])}}</span>
                  <span>{{unit['name']}}</span>
                </summary>
                <div class="operations">
                  <a href="moveup/{{rack_index}}/{{unit_index}}">▲</a> 
                  <a href="movedown/{{rack_index}}/{{unit_index}}">▼</a> 
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
                <div class="port-info">
                  % port_index = 0
                  % for port in unit['input_control_ports']:
                  <div id="port-{{rack_index}}-{{unit_index}}-{{port_index}}">
                    <span>{{rack_index}}.{{unit_index}}.{{port_index}}:</span>
                    <a href="/cc/{{rack_index}}/{{unit_index}}/{{port_index}}">--:--:lin</a>
                    <span>{{port['name']}} [{{port['range'][1]}} {{port['range'][0]}} {{port['range'][2]}}]</span>
                    <div class="control-input-container">
                      <input class="input-control-port-value-slider" type="range" min="{{port['range'][1]}}" max="{{port['range'][2]}}" step="0.001" value="{{port['value']}}" autocomplete="off" name="input_control_port_value_slider_{{rack_index}}_{{unit_index}}_{{port_index}}" data-rack-index="{{rack_index}}" data-unit-index="{{unit_index}}" data-port-index="{{port_index}}">
                      <input class="input-control-port-value-text" type="text" inputmode="decimal" value="{{port['value']}}" autocomplete="off" size="5" name="input_control_port_value_text_{{rack_index}}_{{unit_index}}_{{port_index}}" data-rack-index="{{rack_index}}" data-unit-index="{{unit_index}}" data-port-index="{{port_index}}">
                    </div>
                  </div>
                  % port_index = port_index + 1
                  % end
                </div>
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
              % unit_index = unit_index + 1
            </div>
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
        %rack_index = rack_index + 1
        <div class="add-rack">
          <a href="add/{{rack_index}}">add rack</a>
        </div>
        % end
        <input type="submit" value="submit">
      </form>

    </div>

  </body>
</html>
