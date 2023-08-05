new Vue({
    el: '#app',
    data: {
        name: '',
        handle: '',
        contents: [],
        rating: 0,
        times: [],
        ratings: [],
        names: [],
        is1:false,
        is3:false,
    },
    methods: {
        add() {
            this.is1=false;
            this.is3=false;
            this.contents = [];
            this.names = [];
            this.ratings = [];
            this.times = [];
            if (this.name === "") {
                alert("输入不能为空");
                return;
            }
            let dataToSend1 = {
                handle: this.name
            };
            let dataToSend2 = {
                handles: this.name
            };

            let url2 = '/getUserRatings?' + "handle=" + this.name;
            let url1 = '/batchGetUserInfo?' + "handles=" + this.name;
            let num1, num2;
            axios.get(url1)
                .then(response => {
                        num1 = response.status;
                        return response.data;
                    }
                )
                .then(data => {
                    data1 = data;
                    return axios.get(url2)
                })
                .then(response => {
                    num2 = response.status;
                    return response.data;
                })
                .then(data => {
                    data2 = data;
                    //处理数据
                    for (var i = 0; i < data2.length; i++) {
                        this.contents.push({
                            'ratingUpdatedAt': data2[i]["ratingUpdatedAt"],
                            'contestName': data2[i]["contestName"],
                            'rank': data2[i]["rank"],
                            'oldRating': data2[i]["oldRating"],
                            'newRating': data2[i]["newRating"],
                        });
                        this.times.push(data2[i]["ratingUpdatedAt"]);
                        this.ratings.push(data2[i]["newRating"]);
                        this.names.push(data2[i]["contestName"]);
                    }
                    if (data2.length === 0) {
                        this.handle = data1[0]["result"]["handle"];
                        this.rating = 0;
                        this.is1=true;
                        this.is3=false;
                        console.log(this.is3);
                    } else {
                        this.handle = data1[0]["result"]["handle"] + "(" + data1[0]["result"]["rank"] + ')';
                        this.rating = data1[0]["result"]["rating"];
                        this.is1=true;
                        this.is3=false;
                        this.addchart()
                    }
                    return;
                })
                .catch(error => {
                    // console.log(error.response.status===404);
                    console.log(error);
                    if (error.response.status === 404) {
                        alert("查无此人");
                    } else {
                        alert("出错了！" + error);
                    }

                });
        },
        addchart() {
            // 准备数据
            // console.log(this.names);echars.dispose(chart);
            var chart = echarts.init(document.getElementById('ratingchart'));
            console.log(this.times);
            var p = this.times;
            var pp = this.ratings;
            var maxx=0;
            // 获取rating数据中的最大值
            for(var k=0;k<pp.length;k++){
                if(maxx<pp[k]){
                    maxx=pp[k];
                }
            }
            maxx=maxx+500;
            var ppp = this.names;
            let pppp = p.map(str => str.slice(0, -15));
            // 配置项
            var option = {
                title: {
                    text: '比赛成绩分布',
                    subtext: ''
                },
                tooltip: {
                    formatter: function (params) {
                        var data = params.data;  // 获取当前气泡的数据
                        let index = params.dataIndex;

                        var x = p[index];
                        var y = pp[index];
                        var z = ppp[index];

                        return '比赛时间：' + x + '<br>'
                            + 'rating：' + y + '<br>'
                            + '比赛名称:' + z;
                    }
                },
                toolbox: {
                    show: true,
                    feature: {
                        saveAsImage: {}
                    }
                },
                xAxis: {
                 type: 'category',
                boundaryGap: false,
                // prettier-ignore
                data: pppp,
                },
                yAxis: {
                    type: 'value',
                    axisLabel: {
                        formatter: '{value}'
                    },
                    axisPointer: {
                        snap: true
                    },
                    max:maxx,
                },
                visualMap: {
                    show: false,
                    dimension: 0,
                },
                // 省略其余的配置

                series: [
                    {
                        name: 'rating',
                        type: 'line',
                        smooth: true,
                        data: this.ratings
                    },
                    {
                        type: 'line',
                        markArea: {
                            data: [
                                [
                                    {yAxis: '0'},
                                    {yAxis: '1200'}
                                ]
                            ],
                            itemStyle: {
                                color: 'rgb(204,204,204)' // 第一个区域的颜色为橙色
                            }
                        }
                    },
                    {
                        type: 'line',
                        markArea: {
                            data: [
                                [
                                    {yAxis: '1200'},
                                    {yAxis: '1400'}
                                ]
                            ],
                            itemStyle: {
                                color: 'rgb(119,255,119)' // 第二个区域的颜色为绿色
                            }
                        }
                    },
                    {
                        type: 'line',
                        markArea: {
                            data: [
                                [
                                    {yAxis: '1400'},
                                    {yAxis: '1600'}
                                ]
                            ],
                            itemStyle: {
                                color: 'rgba(119,221,187)' // 第三个区域的颜色为蓝色
                            }
                        }
                    },
                    {
                        type: 'line',
                        markArea: {
                            data: [
                                [
                                    {yAxis: '1600'},
                                    {yAxis: '1900'}
                                ]
                            ],
                            itemStyle: {
                                color: 'rgba(170,170,255)' // 第三个区域的颜色为蓝色
                            }
                        }
                    },
                    {
                        type: 'line',
                        markArea: {
                            data: [
                                [
                                    {yAxis: '1900'},
                                    {yAxis: '2100'}
                                ]
                            ],
                            itemStyle: {
                                color: 'rgba(255,204,136)' // 第三个区域的颜色为蓝色
                            }
                        }
                    },
                    {
                        type: 'line',
                        markArea: {
                            data: [
                                [
                                    {yAxis: '2100'},
                                    {yAxis: '2300'}
                                ]
                            ],
                            itemStyle: {
                                color: 'rgba(255,204,136)' // 第三个区域的颜色为蓝色
                            }
                        }
                    },
                    {
                        type: 'line',
                        markArea: {
                            data: [
                                [
                                    {yAxis: '2300'},
                                    {yAxis: '2400'}
                                ]
                            ],
                            itemStyle: {
                                color: 'rgba(255,187,85)' // 第三个区域的颜色为蓝色
                            }
                        }
                    },
                    {
                        type: 'line',
                        markArea: {
                            data: [
                                [
                                    {yAxis: '2400'},
                                    {yAxis: '2600'}
                                ]
                            ],
                            itemStyle: {
                                color: 'rgba(255,119,119)' // 第三个区域的颜色为蓝色
                            }
                        }
                    },
                    {
                        type: 'line',
                        markArea: {
                            data: [
                                [
                                    {yAxis: '2600'},
                                    {yAxis: '3000'}
                                ]
                            ],
                            itemStyle: {
                                color: 'rgba(255,51,51)' // 第三个区域的颜色为蓝色
                            }
                        }
                    },
                    {
                        type: 'line',
                        markArea: {
                            data: [
                                [
                                    {yAxis: '3000'},
                                    {yAxis: '10000'}
                                ]
                            ],
                            itemStyle: {
                                color: 'rgba(170,0,0)' // 第三个区域的颜色为蓝色
                            }
                        }
                    },
                ]

            };

            // 应用配置
            chart.setOption(option);
        }
    }
});
