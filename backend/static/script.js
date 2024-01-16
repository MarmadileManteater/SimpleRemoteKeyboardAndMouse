(async () => {
  (await fetch()).json()
    let calculateDistance = (a, b) => {
        return Math.sqrt(Math.pow(b[0] - a[0], 2) + Math.pow(b[1] - a[1], 2))
    }
    let mapButtonEventToRoute = (button, event, route) => {
        button.addEventListener(event, () => {
            let routeType, fetchRoute// if the route is a function, evaluate it, and if it is a string, just send it
            if ((fetchRoute = (routeType = typeof route) === 'function'?route():routeType === 'string'?route:'') !== '')
                return fetch(fetchRoute)
        })
    }
    let keyboard = document.querySelector('.keyboard')
    mapButtonEventToRoute(document.querySelector('.send'), 'click', () => {
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
    let state = {x: 0, y: 0, isTouching: false, isScrolling: false, lastTimeSent: 0 }
    let touchpad = document.querySelector('.touch')
    touchpad.addEventListener('touchstart', (e) => {
        e.preventDefault()
        Object.assign(state, { x: e.touches[0].clientX, y: e.touches[0].clientY, isTouching: true, isScrolling: e.touches.length > 1 })
    })
    touchpad.addEventListener('touchmove', (e) => {
        // if the user is currently touching the screen and the last time trackpad data was sent is greater than 150ms ago,
        if (state.lastTimeSent < new Date().getTime() - 150 && state.isTouching) {
            let touches = Array.from(e.touches).map((touch) => {
                return [touch.clientX, touch.clientY]
            })
            // calculate the distance moved since last fetch to server
            let dx = parseInt(state.x - touches[0][0])
            let dy = parseInt(state.y - touches[0][1])
            // set the d object to the current client x and y values
            Object.assign(state, { x: touches[0][0], y: touches[0][1], isScrolling: touches.length == 2?calculateDistance.apply(null, touches) < 100:false, lastTimeSent: new Date().getTime() })
            fetch(`/mouse${state.isScrolling?'scroll':isDragToggled?'drag':'move'}/${(- dx * 2)}/${(- dy * 2)}`)
        }
    })
    touchpad.addEventListener('touchend', () => {
        // clear out the position  object and the isTouching variable
        Object.assign(state, { x: 0, y: 0, isTouching: false, isScrolling: false })
    })
})()
