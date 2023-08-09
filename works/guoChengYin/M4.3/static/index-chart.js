let myChart = echarts.init(document.getElementById('lineChart'));
yData = [1200, 1400, 1600, 1900, 2100, 2300, 2400, 2600, 3000]
// 指定图表的配置项和数据
console.log(UpdatedAts)
option = {
  tooltip: {
    trigger: 'item',
    formatter: function (params) {
      var dataIndex = params.dataIndex;
      var item = rating_hisyory[dataIndex];
      return item.contestName + '<br>' + 'rank:' + item.rank;
    }
  },
  legend: {},
  toolbox: {
    show: true,
    feature: {
      dataZoom: {
        yAxisIndex: 'none'
      },
      dataView: {readOnly: false},
      magicType: {type: ['line', 'bar']},
      restore: {},
      saveAsImage: {}
    }
  },
  xAxis: {
    type: 'category',
    boundaryGap: true,
    data: UpdatedAts,
  },
  yAxis: {
    show: true,
    interval: 100,
    axisLabel: {
      formatter: function (value, index) {
        console.log(value)
        if (yData.indexOf(value) != -1) {
          return value// 使用自定义刻度文本
        } else {
          return ""
        }
      }
    },
    axisLine: {
      show: true,
      lineStyle: {
        color: 'black', // 坐标轴线颜色
        width: 3.5 // 坐标轴线宽度
      }
    },


  },
  series: [

    {
      name: 'Rating',
      type: 'line',
      data: ratings,
      lineStyle: {
        color: 'rgb(238,186,63)', // 折线颜色
        width: 2 // 折线宽度
      },
      itemStyle: {
        color: 'rgb(238,186,63)', // 数据点颜色
        symbolSize: 20
      },
      markArea: {
        data: [
          [{
            yAxis: 0,
            itemStyle: {
              color: 'rgba(128,128,128)'
            }
          }, {
            yAxis: 1200
          }],
          [{
            yAxis: 1201,
            itemStyle: {
              color: 'rgb(119,255,119)'
            }
          }, {
            yAxis: 1400
          }],
          [{
            yAxis: 1401,
            itemStyle: {
              color: 'rgb(119,221,187)'
            }
          }, {
            yAxis: 1600
          }],
          [{
            yAxis: 1601,
            itemStyle: {
              color: 'rgb(170,170,255)'
            }
          }, {
            yAxis: 1900
          }],
          [{
            yAxis: 1901,
            itemStyle: {
              color: 'rgb(255,136,255)'
            }
          }, {
            yAxis: 2100
          }],
          [{
            yAxis: 2101,
            itemStyle: {
              color: 'rgb(255,204,136)'
            }
          }, {
            yAxis: 2300
          }],
          [{
            yAxis: 2301,
            itemStyle: {
              color: 'rgb(255,187,85)'
            }
          }, {
            yAxis: 2400
          }],
          [{
            yAxis: 2401,
            itemStyle: {
              color: 'rgb(255,119,119)'
            }
          }, {
            yAxis: 2600
          }],
          [{
            yAxis: 2601,
            itemStyle: {
              color: 'rgb(255,51,51)'
            }
          }, {
            yAxis: 3000
          }],
          [{
            yAxis: 3001,
            itemStyle: {
              color: 'rgb(170,0,0)'
            }
          }, {
            yAxis: 5000
          }]
        ]
      },
      markLine: {
        data: [
          [
            {
              symbol: 'none',
              x: '90%',
              yAxis: 'max'
            },
            {
              symbol: 'circle',
              label: {
                position: 'start',
                formatter: 'Max'
              },
              type: 'max',
              name: '最高点'
            }
          ]
        ]
      }
    }
  ]
};
