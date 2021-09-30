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
                <a title="save" href="save">sv</a>
                <a title="save as..." href="saveas">(as)</a>
                <a title="load" href="load">ld</a>
                <a title="reset to defaults" href="reset">rst</a>
                <a title="upload" href="upload">ul</a>
                <a title="download" href="download" download="ogfx-setup.json">dl</a>
            </div>
        </div>

        <div class="racks-navigation-list rounded-shadow-box">
            <span>racks:</span>
            <div class="operations indent">
                % index = 0
                % for rack in setup['racks']:
                    <a href="#rack-{{index}}">rack-{{index}}</a>
                    % index = index + 1
                %end
            </div>
        </div>

        <form action="/" method="post">
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
