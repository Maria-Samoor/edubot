// let timeElapsed = 0;

// function startTimer() {
//     const timerElement = document.getElementById('timer');

//     setInterval(() => {
//         timeElapsed++;
//         const minutes = Math.floor(timeElapsed / 60);
//         const seconds = timeElapsed % 60;
//         timerElement.innerHTML = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
//     }, 1000);
// }

// function stopActivity(button) {
//     const stopUrl = button.getAttribute('data-stop-url');
//     window.location.href = stopUrl;
// }

// window.onload = startTimer;

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

function publishFingerCount(activityId) {
    // Publish the current finger count for activity 3
    const fingerCount = getCurrentFingerCount(); // Assuming you have a function to get the current finger count
    if (fingerCount !== null) {
        const mqttTopic = `activity/fingers/${activityId}`;
        const mqttMessage = {
            topic: mqttTopic,
            message: fingerCount
        };

        // Assuming you are using MQTT.js or some other method to publish
        mqttClient.publish(mqttMessage.topic, mqttMessage.message);
        console.log(`Published finger count ${fingerCount} to topic ${mqttTopic}`);
    } else {
        console.error("Finger count is not available.");
    }
}

function getCurrentFingerCount() {
    // This is a placeholder function. You should replace it with actual logic
    // to detect the number of raised fingers from the camera or stream.
    return Math.floor(Math.random() * 10);  // Replace this with actual finger detection logic
}

window.onload = startTimer;
