function initChart() {
    const dataset = document.currentScript.dataset;
    const resourceId = dataset.id;
    const canvasId = "priceChart-" + resourceId;
    const containerId = "chart-container-" + resourceId;

    const container = document.getElementById(containerId);
    const canvas = document.createElement("canvas");

    canvas.id = canvasId;
    container.appendChild(canvas);

    const ctx = canvas.getContext("2d");
    const labels = JSON.parse(
        document.getElementById("chart_labels_" + resourceId).textContent,
    );
    const data = JSON.parse(
        document.getElementById("chart_data_" + resourceId).textContent,
    );
    const sellsData = JSON.parse(
        document.getElementById("chart_sells_" + resourceId).textContent,
    );
    const emptyData = JSON.parse(
        document.getElementById("chart_empty_" + resourceId).textContent,
    );

    new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Resource price",
                    data: data,
                    borderColor: "rgba(75, 192, 192, 1)",
                    backgroundColor: "rgba(75, 192, 192, 0.2)",
                    tension: 0.1,
                    spanGaps: true,
                },
                {
                    label: "Average sales price",
                    data: sellsData,
                    borderColor: "rgba(255, 159, 64, 1)",
                    backgroundColor: "rgba(255, 159, 64, 0.2)",

                    tension: 0.1,
                    pointRadius: 5,
                },
                {
                    label: "Empty stock",
                    data: emptyData,
                    type: "bar",
                    borderColor: "rgba(255, 99, 132, 1)",
                    backgroundColor: "rgba(255, 99, 132, 0.2)",
                    // barPercentage: 1.0,
                    // categoryPercentage: 1.0,
                    tension: 0.1,
                    yAxisID: "yEmpty",
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 150,
                easing: "easeOutQuad",
            },
            plugins: {
                legend: {
                    position: "right",
                },
                title: {
                    display: false,
                },
            },
            scales: {
                y: {
                    title: {
                        display: false,
                    },
                },
                yEmpty: {
                    type: "linear",
                    position: "right",
                    min: 0,
                    max: 1,
                    display: false,
                },
            },
        },
    });
}
initChart();
