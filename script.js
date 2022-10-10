(async function () {
    let theme
    if ((theme = new URLSearchParams(window.location.search).get('theme')) !== undefined)
        document.body.setAttribute('class', theme)
    /**
     * @param {array} a an array that contains the coordinate pair [ x1, y1 ]
     * @param {array} b an array that contains the coordinate pair [ x2, y2 ]
    **/
    let calculateDistance = (a, b) => {
        return Math.sqrt(Math.pow(b[0] - a[0], 2) + Math.pow(b[1] - a[1], 2))
    }
    let mapButtonEventToRoute = (button, event, route) => {
        button.addEventListener(event, () => {
            switch (typeof route) {
                case 'string':
                    fetch(route)
                    break
                case 'function':
                    fetch(route())
                    break
                default:
                    console.warn(`The given button route "${route}" is not a string or function.`)
                    break
            }
        })
    }
    let keyboard = document.querySelector('.keyboard')
    let typewriteSend = document.querySelector('.send')
    mapButtonEventToRoute(typewriteSend, 'click', () => {
        let key = keyboard.value
        keyboard.value = ''
        return `/typewrite?query=${encodeURI(key)}`
    })
    let isDragToggled = false
    document.querySelectorAll('.ui').forEach((element) => {
        let send, hk, toggle
        if ((send = element.getAttribute('data-send')) !== null)
            mapButtonEventToRoute(element, 'click', `/send/${send}`)
        if ((hk = element.getAttribute('data-hotkey')) !== null)
            mapButtonEventToRoute(element, 'click', `/send-hotkey/${hk}`)
        if ((toggle = element.getAttribute('data-toggle')) !== null)
            if (toggle === 'drag')
                mapButtonEventToRoute(element, 'click', () => {
                    isDragToggled = !isDragToggled
                    element.setAttribute('data-active', isDragToggled)
                    return '/disabledrag'
                })
    })
    // The current position object
    let d = {x: 0, y: 0}
    let isTouching = false
    let isScrolling = false
    let touchpad = document.querySelector('.touch')
    let lastTimeSent = 0
    touchpad.addEventListener('touchstart', (e) => {
        e.preventDefault()
        isTouching = true
        if (e.touches.length > 1)// This is a scroll event
            isScrolling = true
        d = { x: e.touches[0].clientX, y: e.touches[0].clientY }
    })
    touchpad.addEventListener('touchmove', function (e) {
        // if the user is current touching the screen and the last time trackpad data was sent is greater than 150ms ago,
        if (lastTimeSent < new Date().getTime() - 150 && isTouching) {
            // calculate the distance moved since last fetch to server
            let touches = Array.from(e.touches).map((touch) => {
                return [touch.clientX, touch.clientY]
            })
            let dx = d.x - touches[0][0]
            let dy = d.y - touches[0][1]
            // set the d object to the current client x and y values
            d = { x: touches[0][0], y: touches[0][1] }
            isScrolling = false
            if (e.touches.length == 2) {// this is a scroll event
                let distance = calculateDistance.apply(null, touches)
                if (distance < 100)
                    isScrolling = true
            }
            if (isScrolling) {
                fetch(`/mousescroll/${(- dx * 2)}/${(- dy * 2)}`)
            } else {
                if (!isDragToggled) {// if the drag toggle is disabled
                    fetch(`/mousemove/${(- dx * 2)}/${(- dy * 2)}`)
                } else {// if the drag toggle is enabled
                    fetch(`/mousedrag/${(- dx * 2)}/${(- dy * 2)}`)
                }
            }
            lastTimeSent = new Date().getTime()
        }
    })
    touchpad.addEventListener('touchend', () => {
        // clear out the position  object and the isTouching variable
        isTouching = false
        isScrolling = false
        d = { x: 0, y: 0 }
    })
}())