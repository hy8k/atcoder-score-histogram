"use strict";

const tabList = document.getElementsByClassName('tab');
const chartList = document.getElementsByClassName('chart');
const updateChartButton = document.getElementById('btn-update-chart');
const standingsUpdateButton = document.getElementById('btn-update-standings');
const downloadPlotButton = document.getElementById('btn-download-plot');

document.addEventListener('DOMContentLoaded', function () {
    if (tabList.length !== 0 && chartList.length !== 0) {
        tabList[0].classList.add('active');
        chartList[0].classList.add('show');
        for (let i = 0; i < tabList.length; i++) {
            tabList[i].addEventListener('click', tabSwitch, false);
        }

        updateChartButton.addEventListener('click', updateChart, false);
        standingsUpdateButton.addEventListener('click', updateStandingsInfo, false);
        standingsUpdateButton.addEventListener('click', function () {
            standingsUpdateButton.disabled = true;
            setTimeout(function () {
                standingsUpdateButton.disabled = false;
            }, 3000);
        }, false);

        downloadPlotButton.addEventListener('click', function () {
            const taskScreenName = document.getElementsByClassName('active')[0].getAttribute('value');

            drawChart(taskScreenName, 'chart-for-png', standingsInfo);
            Plotly.downloadImage('chart-for-png', { format: 'png', width: 800, height: 800, filename: taskScreenName });
        }, false);

        tabList[0].click();

    }
}, false);

function tabSwitch() {
    const arrayTabs = Array.prototype.slice.call(tabList);
    const index = arrayTabs.indexOf(this);
    const taskScreenName = this.getAttribute('value');

    document.getElementsByClassName('active')[0].classList.remove('active');
    this.classList.add('active');
    document.getElementsByClassName('show')[0].classList.remove('show');
    document.getElementsByClassName('chart')[index].classList.add('show');

    drawChart(taskScreenName, taskScreenName, standingsInfo);
};

async function updateStandingsInfo() {
    const contestScreenName = standingsInfo['contest_info']['screen_name'];
    let response = await fetch(formActionURL + '?contest=' + contestScreenName + '&data');

    if (response.ok) {
        let newStandingsInfo = await response.json();
        standingsInfo = newStandingsInfo;
        updateChart();
    }
};

function updateChart() {
    const taskScreenName = document.getElementsByClassName('active')[0].getAttribute('value');
    drawChart(taskScreenName, taskScreenName, standingsInfo)
};

function drawChart(taskScreenName, chartArea, standingsInfo) {
    const userNames = document.getElementById('user-names').value;

    const taskInfo = standingsInfo['task_info'][taskScreenName];
    const taskName = taskInfo['name'];
    const taskAssignment = taskInfo['assignment'];
    const taskUpdateTime = taskInfo['update_time'];

    let scores = [];
    for (const userName in taskInfo['result_info']) {
        scores.push(taskInfo['result_info'][userName]['score']);
    }

    const layout = {
        font: { size: 14 },
        plot_bgcolor: "rgb(250, 250, 250)",
        xaxis: {
            title: {
                text: "Score"
            }
        },
        yaxis: {
            title: {
                text: "Frequency"
            }
        },
        title: chartArea === 'chart-for-png' ? 'Problem ' + taskAssignment : '',
        shapes: [],
        margin: {
            l: 50,
            r: 50,
            b: 50,
            t: 50,
        }
    };

    const traceOfScore = {
        x: scores.map(x => x / 100),
        type: "histogram",
        name: "cumulative",
        marker: {
            color: "#c4ecec",
            line: {
                color: "#000000",
                width: 0.03
            }
        },
        nbinsx: 30
    };

    const data = [traceOfScore];
    const config = { responsive: true };

    layout.annotations = [];

    if (userNames !== '') {
        const colors = [
            "#ff1111",
            "#0011a3",
            "#bfbf00",
            "#a55111",
            "#000fff",
            "#999999",
            "#ff00ff",
            "#dd0000",
            "#ff7777",
            "#000000",
        ];
        const userNameList = Array.from(new Set(userNames.split(',').map(s => s.trim())));
        const resultInfo = taskInfo['result_info'];

        let userNameListLength = userNameList.length;
        let loop = 0;
        let invalid_users = [];

        for (const userName of userNameList) {
            if (!(userName in resultInfo)) {
                invalid_users.push(userName);
                userNameListLength--;
            }
        }

        for (const userName of userNameList) {
            if (!(userName in resultInfo)) {
                continue;
            }

            const userLine = {
                type: "line",
                x0: resultInfo[userName]['score'] / 100,
                y0: 0,
                x1: resultInfo[userName]['score'] / 100,
                y1: 1,
                yref: "paper",
                line: {
                    color: colors[loop],
                    width: 1.8
                }
            };

            const annotation = {
                showarrow: true,
                text: userName + '<br>Score:' + resultInfo[userName]['score'] / 100,
                x: resultInfo[userName]['score'] / 100,
                yref: "paper",
                y: loop / userNameListLength,
                align: "right",
                xanchor: "right",
                yanchor: "bottom",
                font: {
                    color: colors[loop],
                    size: 12
                }
            };

            layout["shapes"].push(userLine);
            layout.annotations.push(annotation);
            loop++;
        }

        if (invalid_users.length !== 0) {
            document.getElementById('invalid-users').textContent = 'Invalid usernames: ' + invalid_users.join(', ');
        } else {
            document.getElementById('invalid-users').textContent = ''
        }
    }

    document.getElementById('task-name').textContent = (taskName == '' ? '' : taskName);
    document.getElementById('update-time').textContent = (new Date(taskUpdateTime)).toLocaleString();

    Plotly.newPlot(chartArea, data, layout, config);
}
