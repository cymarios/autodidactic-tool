let chart = null;
const literals = ["x1", "¬x1", "x2", "¬x2", "x3", "¬x3", "x4", "¬x4", "x5", "¬x5"];
const BACKEND_URL = "https://autodidactic-tool.onrender.com";

async function submitExample() {
    const example = document.getElementById("example").value.trim();
    const label = document.getElementById("label").value.trim();

    if (!example || !label) {
        alert("Please enter both example and label.");
        return;
    }

    try {
        const response = await fetch(`${BACKEND_URL}/submit_example`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ example, label })
        });

        const data = await response.json();
        updateOutput(data.current_hypothesis, data.log);
        updateChart(data.current_hypothesis);
    } catch (error) {
        alert("Could not connect to backend.");
    }
}

async function resetLearner() {
    try {
        const response = await fetch(`${BACKEND_URL}/reset`, { method: "POST" });
        const data = await response.json();

        document.getElementById("example").value = "";
        document.getElementById("label").value = "";

        updateOutput(data.current_hypothesis, data.log);
        updateChart(data.current_hypothesis);
    } catch (error) {
        alert("Reset failed.");
    }
}

function updateOutput(hypothesis, log) {
    document.getElementById("output").textContent =
        hypothesis.length > 0 ? hypothesis.join(", ") : "[Empty hypothesis]";

    const logBox = document.getElementById("log");
    logBox.innerHTML = log.map(line => `<div>${line}</div>`).join("");
}

function updateChart(hypothesis) {
    const data = literals.map(lit => hypothesis.includes(lit) ? 1 : 0);

    if (!chart) {
        const ctx = document.getElementById("hypothesisChart").getContext("2d");
        chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: literals,
                datasets: [{
                    label: 'Included in Hypothesis',
                    data: data,
                    backgroundColor: data.map(val => val ? 'green' : 'lightgray'),
                }]
            },
            options: {
                scales: {
                    y: { beginAtZero: true, max: 1.2, ticks: { display: false } }
                },
                plugins: { legend: { display: false } }
            }
        });
    } else {
        chart.data.datasets[0].data = data;
        chart.data.datasets[0].backgroundColor = data.map(val => val ? 'green' : 'lightgray');
        chart.update();
    }
}
