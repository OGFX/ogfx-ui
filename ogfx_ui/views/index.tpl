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
        <div id="top-menu" class="rounded-shadow-box">
            <span>setup: {{filename}}</span>
            <div class="indent">
                <a title="save as..." href="saveas">sv..</a>
                <a title="load" href="load">ld..</a>
                <a title="reset to defaults" href="reset">rst</a>
                <a title="upload" href="upload">ul..</a>
                <a title="download" href="download" download="ogfx-setup.json">dl..</a>
            </div>
        </div>

        <div class="connections-info rounded-shadow-box">
            <div>midi-input:</div>
            % connection_index = 0
            % for connection in setup['input_midi_connections']:
                <div class="indent"><span>{{connection}}</span><a class="indent" href="disconnect/midi-input/{{connection_index}}">disconnect</a></div>
                % connection_index = connection_index + 1
            % end
            <div><a class="indent" href="connect/midi-input">connect..</a></div>
        </div>

        <form action="/" method="post">
            <div class="connections-info rounded-shadow-box">
                tempo tap MIDI CC:
                <input id="tempotap-midi-cc-enabled" class="tempotap-midi-cc-enabled" name="tempotap_midi_cc_enabled" title="Midi CC enabled" type="checkbox" {{'checked' if setup['tempotap']['enabled'] else ''}}>
                <input id="tempotap-midi-cc-channel" class="tempotap-midi-cc-channel midi-cc-channel" name="tempotap_midi_cc_channel" title="Midi channel (0..15)" type="number" min="0" max="15" value="{{setup['tempotap']['channel']}}">
                <input id="tempotap-midi-cc-cc" class="tempotap-midi-cc-cc midi-cc-cc" name="tempotap_midi_cc_cc" title="Midi CC (0..127)" type="number" min="0" max="127" value="{{setup['tempotap']['cc']}}">
            </div>
    
            <div class="add-rack rounded-shadow-box">
            <a href="add/0">add rack</a>
            </div>
            % rack_index = 0
            % for rack in setup['racks']:
                % include('rack.tpl', rack=rack)
                % rack_index = rack_index + 1
                <div class="add-rack rounded-shadow-box">
                    <a href="add/{{rack_index}}">add rack</a>
                </div>
            % end
            <input type="submit" value="submit">
        </form>
    </body>
</html>
