<!DOCTYPE html>
<html>
<head>
    <title>OGFX</title>
    <link rel="stylesheet" type="text/css" href="/static/index.css">
    <link rel="stylesheet" type="text/css" href="/static/range.css">
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>

<body>
<div id="top-menu">
    <span>setup:</span>
    <p class="operations">
        <a href="save">save</a> 
        <a href="saveas">(as)</a> 
        <a href="load">load</a> 
        <a href="new">new</a>
    </p>
</div>

<div class="racks-navigation-list">
    <span>racks:</span>
    <div class="operations">
        % index = 0
        % for rack in racks:
            <a href="#rack-{{index}}">rack-{{index}}</a>
            % index = index + 1
        %end
    </div>
</div>

<div id="racks">
    <div class="add-rack">
        <a href="add-rackt">add rack</a>
    </div>
    % rack_index = 0
    % for rack in racks:
        <div class="rack" id="rack-{{rack_index}}">
            <div>
                <span>{{rack_index}}._._:</span>
                <span>rack-{{rack_index}}</span>
                <div class="operations">
                    <a href="save">save</a> 
                    <a href="saveas">(as)</a> 
                    <a href="load">load</a> 
                    <a href="new">new</a>
                </div>
            </div>
            <div class="add-unit">
                <a href="add-unit">add unit</a>
            </div>
            % unit_index = 0
            % for unit in rack:
            <div class="unit">
                <div class="unit-info">
                    <span>{{rack_index}}.{{unit_index}}._:</span>
                    <span>{{unit[1]}}</span>
                    <div class="operations">
                        <a href="save">save</a> <a href="saveas">(as)</a> <a href="load">load</a> <a href="reset">reset</a> <a href="delete">delete</a>
                    </div>
                </div>
                <div class="port-info">
                    % port_index = 0
                    % for port in unit[2]:
                        <div>
                            <span>{{rack_index}}.{{unit_index}}.{{port_index}}:</span>
                            <span>{{port[0]}}</span>
                            <div class="control-input-container">
                                <input type="range" min="{{port[2][1]}}" max="{{port[2][2]}}" step="0.001" value="{{port[4]}}" autocomplete="off">
                                <input type="text" inputmode="decimal" value="{{port[4]}}" autocomplete="off" size="5">
                            </div>
                        </div>
                        % port_index = port_index + 1
                    % end
                </div>
                % unit_index = unit_index + 1
            </div>
            <div class="add-unit">
                <a href="add-unit">add unit</a>
            </div>
            % end
        </div>
        %rack_index = rack_index + 1
        <div class="add-rack">
            <a href="add-rackt">add rack</a>
        </div>
    % end
</div>

</body>
</html>
