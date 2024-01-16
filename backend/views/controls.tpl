<!DOCTYPE html>
<html>
    <head>
        <meta name="viewport" content="width=device-width, height=device-height,  initial-scale=1.0, user-scalable=no;user-scalable=0;"/>
        <link rel="stylesheet" type="text/css" href="styles.css" />
        <template id="toast" tag-name="div">
          <div class="icon"></div>
          <div class="message"></div>
        </template>
        <meta charset="utf-8"/>
        <meta name="api-version" content="{{api_version}}" />
    </head>    
    <body >
        % if disable_indicator != True:
        <div id="status-light"></div>
        % end
        <div id="toast-center">
        </div>
        <div class="touchpad flex-box wrap border-radius">
            <div class="touch"></div>
            <div class="ui leftmouse" data-send="leftclick"></div>
            <div class="ui rightmouse" data-send="rightclick"></div>
        </div>
        <div class="flex-box space-between">
            <textarea class="keyboard border-radius"></textarea>
            <button class="send keys border-radius long-text">Typewrite</button>
        </div>
        <div class="flex-box wrap space-between">
            <button class="ui keys border-radius" data-send="enter">Enter</button>
            <button class="ui keys border-radius backspace long-text" data-send="backspace" >Backspace</button>
            <button class="ui keys border-radius" data-hotkey="ctrl,c">Copy</button>
            <button class="ui keys border-radius" data-hotkey="ctrl,v" >Paste</button>
            <button class="ui keys border-radius" data-toggle="drag">Toggle Drag</button>
            % if volume_controls:
            <button class="ui keys border-radius" data-send="volumemute">🔇</button>
            <button class="ui keys border-radius" data-send="volumedown">🔈</button>
            <button class="ui keys border-radius" data-send="volumeup">🔊</button>
            % end
        </div>
        <div class="flex-box space-between">
            <button class="ui keys border-radius" data-send="left">←</button>
            <div class="up-down">
                <div class="inner">
                    <button class="ui keys border-radius up" data-send="up">↑</button>
                    <button class="ui keys border-radius down" data-send="down">↓</button>
                </div>
            </div>
            <button class="ui keys border-radius" data-send="right">→</button>
        </div>
        <script src="main.js" type="module" ></script>
    </body>
</html>
