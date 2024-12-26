let timeElapsed = 0;

function startTimer() {
    const timerElement = document.getElementById('timer');

    setInterval(() => {
        timeElapsed++;
        const minutes = Math.floor(timeElapsed / 60);
        const seconds = timeElapsed % 60;
        timerElement.innerHTML = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    }, 1000);
}

function stopActivity(button) {
    const stopUrl = button.getAttribute('data-stop-url');
    window.location.href = stopUrl;
}

window.onload = startTimer;

