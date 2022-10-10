(async function () {
    
    var getQuery = function () {
        var queryObject = {};
        if (window.location.search) {
            var queryArray;
            var queryParts = window.location.search.split("?")[1];
            if (queryParts.indexOf("&") !== -1) {
                queryArray = queryParts.split("&")
            } else {
                queryArray = [queryParts]
            }
            for (var i = 0; i < queryArray.length; i++) {
                var queryEntry = queryArray[i];
                if (queryEntry.indexOf('=') !== -1) {
                    var keyValuePair = queryEntry.split("=");
                    if (keyValuePair.length === 2) {// only honor valid key value pairs
                        queryObject[keyValuePair[0]] = keyValuePair[1]
                    }
                }
            }
        }
        return queryObject;
    }

    var pageQuery = getQuery();
    if (Object.keys(pageQuery).indexOf('theme') !== -1) {
        document.body.setAttribute('class', pageQuery['theme']);
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
    var keyboard = document.querySelector('.keyboard')
    var typewriteSend = document.querySelector('.send')
    mapButtonEventToRoute(typewriteSend, 'click', () => {
        var key = keyboard.value
        keyboard.value = ''
        return `/typewrite?query=${encodeURI(key)}`
    })
    window.isClicking = false
    document.querySelectorAll('.ui').forEach((element) => {
        if ((send = element.getAttribute('data-send')) !== null)
            mapButtonEventToRoute(element, 'click', `/send/${send}`)
        if ((hk = element.getAttribute('data-hotkey')) !== null)
            mapButtonEventToRoute(element, 'click', `/send-hotkey/${hk}`)
        if ((toggle = element.getAttribute('data-toggle')) !== null)
            if (toggle === 'drag')
                mapButtonEventToRoute(element, 'click', () => {
                    window.isClicking = !window.isClicking
                    element.setAttribute('data-active', window.isClicking)
                    return '/disabledrag'
                })
    })
    // #endregion

    // #region mouse controls
    // The current position object
    var d = {x: 0, y: 0};
    var isTouching = false;
    var isScrolling = false;
    var touchpad = document.querySelector('.touch');
    window.lastTimeSent = 0;
    touchpad.addEventListener('touchstart', function (e) {
        e.preventDefault()
        isTouching = true;
        if (e.touches.length > 1) {
            // This is a scroll event
            isScrolling = true;
        } 
        d.x = e.touches[0].clientX;
        d.y = e.touches[0].clientY;
    });
    touchpad.addEventListener('touchmove', function (e) {
        // if the last time trackpad data was sent is greater than 150ms ago,
        if (window.lastTimeSent < new Date().getTime() - 150) {
            // and if the user is current touching the screen
            if (isTouching) {
                // calculate the distance moved since last fetch to server
                var distx = d.x - e.touches[0].clientX;
                var disty = d.y - e.touches[0].clientY;
                // set the d object to the current client x and y values
                d.x = e.touches[0].clientX;
                d.y = e.touches[0].clientY;
                isScrolling = false;
                if (e.touches.length == 2) {
                    // This is a scroll event
                    var distanceBetweenTouchPoints = calculate2DDistance([e.touches[0].clientX, event.touches[0].clientY], [event.touches[1].clientX, event.touches[1].clientY ]);

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