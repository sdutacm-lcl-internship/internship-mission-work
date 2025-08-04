<template>
    <div ref="chartRef" style="height: 350px; width: 100%;"></div>
</template>

<script setup>
    import * as echarts from 'echarts'
    import { ref, onMounted } from 'vue'


    const props = defineProps({
        ratings: {
            type: Array,
            required: true
        }
    })

    const chartRef = ref(null)
    let chart = null

    const ratingBackground = [
        { name: 'Newbie', min: 0, max: 1199, color: '#CCCCCC' },
        { name: 'Pupil', min: 1200, max: 1399, color: '#77FF77' },
        { name: 'Specialist', min: 1400, max: 1599, color: '#77DDBB' },
        { name: 'Expert', min: 1600, max: 1899, color: '#AAAAFF' },
        { name: 'Candidate Master', min: 1900, max: 2099, color: '#FF88FF' },
        { name: 'Master', min: 2100, max: 2299, color: '#FFCC88' },
        { name: 'International Master', min: 2300, max: 2399, color: '#FFBB55' },
        { name: 'Grandmaster', min: 2400, max: 2599, color: '#FF7777' },
        { name: 'International Grandmaster', min: 2600, max: 2999, color: '#FF3333' },
        { name: 'Legendary Grandmaster', min: 3000, max: 10000, color: '#AA0000' },
    ]

    const rankTicks = [0, 1200, 1400, 1600, 1900, 2100, 2300, 2400, 2600, 3000];


    let maxRating, minRating
    const padding = 300

    function renderChart() {
        const ratings = props.ratings
        const data = ratings.map(item => [
            new Date(item.ratingUpdatedAt),
            item.newRating,
            item
        ])

        if(!ratings || ratings.length === 0){
            maxRating = 800;
            minRating = 0;
        }else{
            maxRating = Math.max(...ratings.map(item => item.newRating))
            minRating = Math.min(...ratings.map(item => item.newRating))
        }

        const option = {
            // title: {},
            tooltip: {
                trigger: 'item',
                backgroundColor: 'rgba(255, 255, 255, 0.6)',
                position: 'right',
                textStyle: {
                    fontSize: '12',
                    align: 'left',
                },
                formatter: (params) => {
                    const item = params.data[2]
                    const diff = item.newRating - item.oldRating
                    return `
                    ${item.newRating}(${diff >= 0 ? '+' : ''}${diff})<br/>
                    <strong>Rank:</strong>${item.rank}<br/>
                    ${item.contestName}<br/>
                    ${item.ratingUpdatedAt}
                    `
                },
            },
            // 横坐标轴 默认为 value 类型
            xAxis: {
                type: 'time',
                splitLine: {
                    show: true,
                    lineStyle: {
                        color: '#5f6b7c99',
                        type: 'solid',
                    }
                }
                // axisLabel: {
                //     formatter: (value) => {
                //         const date = new Date(value)
                //         const firstData = new Date(ratings[0].ratingUpdatedAt)
                //         const now = new Date()
                //         const span = (now - firstData) / (1000 * 60 * 60 * 24);
                //         const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                //                         "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
                //         if (span > 365 * 3) {
                //             return date.getFullYear().toString();
                //         } else if (span > 180) {
                //             return `${months[date.getMonth()]} ${date.getFullYear()}`;
                //         } else {
                //             return `${date.getDate().toString().padStart(2, '0')} ${months[date.getMonth()]}\n ${date.getFullYear()}`;
                //         }
                //     },
                // }

            },
            // 纵坐标轴
            yAxis: {
                type: 'value',
                min: Math.max(minRating - padding, 0),
                max: Math.max(maxRating + padding, 2000),
                splitLine: {
                    show: false
                },
                axisLabel: {
                    fontSize: 11,
                    formatter: function(value){
                        return rankTicks.includes(value) ? value.toString() : ''
                    }
                },
                interval: 1,
            },

            dataZoom: [
                {
                    type: 'inside',
                    xAxisIndex: 0,
                    start: 0,
                    end: 100,
                    zoomOnMouseWheel: true,
                    moveOnMouseMove: true,
                    moveOnMouseWheel: true,
                    preventDefaultMouseMove: true,
                    filterMode: 'weakFilter',
                    throttle: 10,
                },
                {
                    type: 'inside',
                    yAxisIndex: 0,
                    start: 0,
                    end: 100,
                    zoomOnMouseWheel: true,
                    moveOnMouseMove: true,
                    moveOnMouseWheel: true,
                    preventDefaultMouseMove: true,
                    filterMode: 'weakFilter',
                },
            ],


            series: {
                type: 'line',
                showSymbol: true,
                sampling: 'lttb',
                itemStyle: {
                    color: '#edc240'
                },
                lineStyle: {
                    shadowColor: '#b9b9b9',
                    shadowBlur: 3,
                    // shadowOffsetX: -3,
                    shadowOffsetY: 2,
                },
                data: data,
                markArea: {
                    silent: true,
                    z: -1,
                    data: ratingBackground.map(level => ([
                        {
                            yAxis: level.min,
                            itemStyle: {
                                color: level.color,
                                // opacity: 0.5,
                            }
                        },
                        {
                            yAxis: level.max
                        }
                    ]))
                }
            }
        }
        chart.setOption(option)
    }

    function resizeChart() {
        if (chart) {
            chart.resize()
        }
    }

    onMounted(() => {
        chart = echarts.init(chartRef.value)
        renderChart()
    })

    window.addEventListener('resize', resizeChart)

</script>

<style scoped></style>
