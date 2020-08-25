<!DOCTYPE html>
<html>
    <head>
        <title>OGFX - Unit Selection</title>
        <link rel="stylesheet" type="text/css" href="/static/index.css">
        <link rel="stylesheet" type="text/css" href="/static/range.css">
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>
        <div class="rack">
            <span>Choose a unit to add:</span>
            <table>
                % map_index = 0
                % for uri, unit in units.items():
                    <tr>
                        <td><a href="/add2{{remaining_path}}/{{map_index}}">{{unit['name']}}</td>
                        <td>#in: {{len(unit['input_audio_ports'])}}</td>
                        <td>#out: {{len(unit['output_audio_ports'])}}</td>
                        <td><span>{{uri}}</span></td>
                    </tr>
                    % map_index = map_index + 1
                % end
            </table>
        </div>
    </body>
</html>
