const topChartConfig = {
    type: "bar",
    data: {
        labels: ['DWG KIA', 'FunPlus Phoenix', 'EDward Gaming', 'MAD Lions', 'Royal Never Give Up', 'LNG Esports', 'T1', '100 Thieves', 'Top Esports', 'Suning', 'Fnatic', 'Team WE'],
        datasets: [{
            label: "Rating Points",
            backgroundColor: ['#dc5f57', '#dca157', '#d4dc57', '#91dc57', '#57dc5f', '#57dca1', '#57d4dc', '#5791dc', '#5f57dc', '#a157dc', '#dc57d4', '#dc5791'],
            data: [2536.9, 2536.3, 2523.2, 2513.9, 2499.0, 2414.1, 2395.1, 2367.7, 2359.4, 2355.4, 2346.8, 2340.7],
        }]
    },
    options: {
        plugins: {
            legend: {
                display: false
            }
        },
        scales: {
            x: {
                grid: {
                    display: false
                }
            },
            y: {
                min: 2312,
                max: 2566
            }
        }
    }
};