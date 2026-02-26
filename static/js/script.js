document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("send-btn").addEventListener("click", function () {
        const userInput = document.getElementById("user-input").value.trim();
        const chatbox = document.getElementById("chatbox");

        if (userInput === "") {
            alert("Please enter a disease name.");
            return;
        }

        // Show user's message
        chatbox.innerHTML += `<p><b>You:</b> ${userInput}</p>`;

        // Make POST request to Flask
        fetch("http://127.0.0.1:5000/chat/get_medications", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ disease: userInput })
        })
        .then(response => response.json())
        .then(data => {
            let responseMessage = "";

            if (data.error) {
                responseMessage = `<b>Bot:</b> ${data.error}`;
            } else if (data.message) {
                responseMessage = `<b>Bot:</b> ${data.message}`;
            } else {
                const med = data.medication;
                responseMessage = `
                    <b>Recommended Medication for ${userInput}:</b><br><br>
                    <b>Brand Name:</b> ${med.brand_name}<br>
                    <b>Usage:</b> ${med.usage}<br>
                    <b>Warnings:</b> ${med.warnings}<br>
                    <b>Food Guidelines:</b> ${med.food_guidelines}
                `;
            }

            chatbox.innerHTML += `<p>${responseMessage}</p>`;
            chatbox.scrollTop = chatbox.scrollHeight; // Auto scroll
        })
        .catch(error => {
            console.error("Error:", error);
            chatbox.innerHTML += `<p><b>Bot:</b> Failed to fetch data.</p>`;
        });

        document.getElementById("user-input").value = ""; // Clear input
    });
});
