const autoScroll = () => {
    return setInterval(() => window.scrollTo(0, document.body.scrollHeight), 2000) 
}

const stopScroll = (interval) => {
    clearInterval(interval)
}

autoScroll()