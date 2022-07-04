(async function () {
    if (window.location.search.split("?")[1] === 'theme=lunar') {
        document.body.setAttribute('class', 'lunar')
    }
    /**
     * @param {array} coordA an array that contains the coordinate pair [ x1, y1 ]
     * @param {array} coordB an array that contains the coordinate pair [ x2, y2 ]
    **/
    var calculate2DDistance = function (coordA, coordB) {
        var x1 = parseInt(coordA[0]);
        var x2 = parseInt(coordB[0]);
        var y1 = parseInt(coordA[1]);
        var y2 = parseInt(coordB[1]);
        return Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
    }

    var mapButtonEventToRoute = function (button, event, route) {
        button.addEventListener(event, function () {
            if (typeof route === 'string') {
                fetch(route);
            }
            if (typeof route === 'function') {
                fetch(route());
            }
        })
    }

    // #region keyboard controls
    var keyboard = document.querySelector('.keyboard');
    var typewriteSend = document.querySelector('.send');
    mapButtonEventToRoute(typewriteSend, 'click', function () {
        var key = keyboard.value;
        keyboard.value = "";
        return "/typewrite?query=" + encodeURI(key);
    });

    var enter = document.querySelector(".enter");
    mapButtonEventToRoute(enter, 'click', '/send/enter');

    var backspace = document.querySelector(".backspace");
    mapButtonEventToRoute(backspace, 'click', '/send/backspace');

    var copy = document.querySelector(".copy");
    mapButtonEventToRoute(copy, 'click', '/send-hotkey/ctrl,c');
    
    var paste = document.querySelector(".paste");
    mapButtonEventToRoute(paste, 'click', '/send-hotkey/ctrl,v');

    var left = document.querySelector(".left");
    mapButtonEventToRoute(left, 'click', '/send/left');

    var up = document.querySelector(".up");
    mapButtonEventToRoute(up, 'click', '/send/up');

    var down = document.querySelector(".down");
    mapButtonEventToRoute(down, 'click', '/send/down');
    
    var right = document.querySelector(".right");
    mapButtonEventToRoute(right, 'click', '/send/right');


    window.isClicking = false;
    var toggleDrag = document.querySelector('.toggle-drag');
    mapButtonEventToRoute(toggleDrag, 'click', function () {
        window.isClicking = !window.isClicking;
        toggleDrag.setAttribute("data-active", window.isClicking);
        return "/disabledrag";
    });
    // #endregion

    // #region mouse controls
    var leftmouse = document.querySelector('.leftmouse');
    mapButtonEventToRoute(leftmouse, 'click', '/sendleftclick');

    var rightmouse = document.querySelector('.rightmouse');
    mapButtonEventToRoute(rightmouse, 'click', '/sendrightclick');
    // The current position object
    var d = {x: 0, y: 0};
    var isTouching = false;
    var isScrolling = false;
    var touchpad = document.querySelector('.touch');
    window.lastTimeSent = 0;
    touchpad.addEventListener('touchstart', function (e) {
        isTouching = true;
        if (event.touches.length > 1) {
            // This is a scroll event
            isScrolling = true;
        } 
        d.x = event.touches[0].clientX;
        d.y = event.touches[0].clientY;
    });
    touchpad.addEventListener('touchmove', function (e) {
        // if the last time trackpad data was sent is greater than 150ms ago,
        if (window.lastTimeSent < new Date().getTime() - 150) {
            // and if the user is current touching the screen
            if (isTouching) {
                // calculate the distance moved since last fetch to server
                var distx = d.x - event.touches[0].clientX;
                var disty = d.y - event.touches[0].clientY;
                // set the d object to the current client x and y values
                d.x = event.touches[0].clientX;
                d.y = event.touches[0].clientY;
                isScrolling = false;
                if (event.touches.length == 2) {
                    // This is a scroll event
                    var distanceBetweenTouchPoints = calculate2DDistance([event.touches[0].clientX, event.touches[0].clientY], [event.touches[1].clientX, event.touches[1].clientY ]);

                    if (distanceBetweenTouchPoints < 100) {
                        isScrolling = true;

                    }
                }
                if (isScrolling) {
                    fetch("/mousescroll/" + (- distx * 2) + "/" +  (- disty * 2))
                } else {
                    if (!isClicking) {// if the drag toggle is disabled
                        fetch("/mousemove/" + (- distx * 2) + "/" +  (- disty * 2))
                    } else {// if the drag toggle is enabled
                        fetch("/mousedrag/" + (- distx * 2) + "/" +  (- disty * 2))
                    }
                }
                window.lastTimeSent = new Date().getTime();
            }
        }
    });
    touchpad.addEventListener('touchend', function (e) {
        // clear out the position  object and the isTouching variable
        isTouching = false;
        isScrolling = false;
        d.x = 0;
        d.y = 0;
    });
    // #endregion
}());